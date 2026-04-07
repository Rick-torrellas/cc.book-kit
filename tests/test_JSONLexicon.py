import pytest
import os
from datetime import datetime, timedelta
from CapsuleCore_book.core import Entry, Relation
from CapsuleCore_book.capsule import JSONLexicon

# --- Fixtures ---


@pytest.fixture
def temp_db_path(tmp_path):
    """Crea una ruta temporal para el archivo JSON de pruebas."""
    return str(tmp_path / "test_lexicon.json")


@pytest.fixture
def lexicon(temp_db_path):
    """Instancia de JSONLexicon limpia para cada test."""
    return JSONLexicon(storage_path=temp_db_path)


@pytest.fixture
def sample_entry():
    """Entrada de ejemplo para reusar."""
    return Entry(
        title="Test Entry",
        content="Contenido de prueba",
        tags=["tag1", "tag2"],
        category="General",
        metadata={"priority": "high"},
    )


# --- Tests de Persistencia y Entradas ---


def test_save_and_get_by_id(lexicon, sample_entry):
    lexicon.save(sample_entry)

    retrieved = lexicon.get_by_id(sample_entry.id)

    assert retrieved is not None
    assert retrieved.id == sample_entry.id
    assert retrieved.title == "Test Entry"
    assert retrieved.tags == ["tag1", "tag2"]
    # Verificar que la fecha se recuperó como objeto datetime, no como string
    assert isinstance(retrieved.created_at, datetime)


def test_get_by_title(lexicon, sample_entry):
    lexicon.save(sample_entry)

    retrieved = lexicon.get_by_title("Test Entry")
    assert retrieved.id == sample_entry.id

    assert lexicon.get_by_title("Non Existent") is None


def test_get_by_ids(lexicon):
    e1 = Entry(title="E1", content="C1")
    e2 = Entry(title="E2", content="C2")
    lexicon.save(e1)
    lexicon.save(e2)

    results = lexicon.get_by_ids([e1.id, e2.id, "fake_id"])
    assert len(results) == 2
    assert any(e.title == "E1" for e in results)


def test_delete_entry_and_clean_relations(lexicon):
    # Setup: 2 entradas y una relación entre ellas
    e1 = Entry(title="Origin", content="...")
    e2 = Entry(title="Target", content="...")
    lexicon.save(e1)
    lexicon.save(e2)

    rel = Relation(from_id=e1.id, to_id=e2.id)
    lexicon.save_relation(rel)

    # Acción: Borrar el origen
    success = lexicon.delete(e1.id)

    # Verificación
    assert success is True
    assert lexicon.get_by_id(e1.id) is None
    # La relación debería haber desaparecido (limpieza de huérfanos)
    assert len(lexicon.get_out_relations(e1.id)) == 0
    assert len(lexicon.get_in_relations(e2.id)) == 0


# --- Tests de Relaciones ---


def test_save_relation_and_prevent_duplicates(lexicon):
    e1 = Entry(title="A", content="...")
    e2 = Entry(title="B", content="...")
    lexicon.save(e1)
    lexicon.save(e2)

    rel = Relation(from_id=e1.id, to_id=e2.id, connection_type="link")

    lexicon.save_relation(rel)
    lexicon.save_relation(rel)  # Intentar guardar duplicado

    out_rels = lexicon.get_out_relations(e1.id)
    assert len(out_rels) == 1
    assert out_rels[0].connection_type == "link"


def test_delete_specific_relation(lexicon):
    e1 = Entry(title="A", content="...")
    e2 = Entry(title="B", content="...")
    lexicon.save(e1)
    lexicon.save(e2)

    lexicon.save_relation(
        Relation(from_id=e1.id, to_id=e2.id, connection_type="type_a")
    )
    lexicon.save_relation(
        Relation(from_id=e1.id, to_id=e2.id, connection_type="type_b")
    )

    # Borrar solo la de tipo 'type_a'
    lexicon.delete_relation(e1.id, e2.id, connection_type="type_a")

    remaining = lexicon.get_out_relations(e1.id)
    assert len(remaining) == 1
    assert remaining[0].connection_type == "type_b"


# --- Tests de Consultas (Filtros) ---


def test_get_by_tag(lexicon):
    e1 = Entry(title="Py", content="...", tags=["coding", "python"])
    e2 = Entry(title="Js", content="...", tags=["coding", "web"])
    lexicon.save(e1)
    lexicon.save(e2)

    coding_entries = lexicon.get_by_tag("coding")
    python_entries = lexicon.get_by_tag("python")

    assert len(coding_entries) == 2
    assert len(python_entries) == 1


def test_get_by_category(lexicon):
    e1 = Entry(title="Doc 1", content="...", category="Work")
    e2 = Entry(title="Doc 2", content="...", category="Personal")
    lexicon.save(e1)
    lexicon.save(e2)

    work_stuff = lexicon.get_by_category("Work")
    assert len(work_stuff) == 1
    assert work_stuff[0].title == "Doc 1"


def test_get_by_date_range(lexicon):
    # Simulamos fechas
    now = datetime.now()
    past = now - timedelta(days=5)
    future = now + timedelta(days=5)  # noqa: F841

    e = Entry(title="Oldie", content="...")
    # Forzamos la fecha (aunque sea frozen, el Lexicon guarda lo que le pasamos)
    # Nota: En un test real podrías usar freezegun o modificar el objeto antes de save
    lexicon.save(e)

    results = lexicon.get_by_date_range(
        now - timedelta(minutes=1), now + timedelta(minutes=1)
    )
    assert len(results) == 1

    results_empty = lexicon.get_by_date_range(past - timedelta(days=1), past)
    assert len(results_empty) == 0


# --- Test de Robustez de Archivo ---


def test_initialization_creates_file(temp_db_path):
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)

    _ = JSONLexicon(storage_path=temp_db_path)
    assert os.path.exists(temp_db_path)

    with open(temp_db_path, "r") as f:
        import json

        data = json.load(f)
        assert "entries" in data
        assert "relations" in data
