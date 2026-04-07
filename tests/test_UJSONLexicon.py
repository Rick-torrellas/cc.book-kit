import pytest
import ujson
from datetime import datetime, timedelta

from CapsuleCore_book.core import Entry, Relation
from CapsuleCore_book.capsule.UJSONLexicon import UJSONLexicon


@pytest.fixture
def temp_storage(tmp_path):
    """Crea una ruta temporal para el archivo JSON de pruebas."""
    return str(tmp_path / "test_codex.json")


@pytest.fixture
def lexicon(temp_storage):
    """Instancia del adaptador apuntando al archivo temporal."""
    return UJSONLexicon(temp_storage)


@pytest.fixture
def sample_entry():
    """Entrada de ejemplo para pruebas."""
    return Entry(
        title="Test Entry",
        content="Contenido de prueba",
        tags=["python", "test"],
        category="Dev",
    )


class TestUJSONLexicon:
    def test_save_and_get_by_id(self, lexicon, sample_entry):
        # Guardar
        lexicon.save(sample_entry)

        # Recuperar
        retrieved = lexicon.get_by_id(sample_entry.id)

        assert retrieved is not None
        assert retrieved.id == sample_entry.id
        assert retrieved.title == "Test Entry"
        assert "python" in retrieved.tags

    def test_get_by_title(self, lexicon, sample_entry):
        lexicon.save(sample_entry)
        retrieved = lexicon.get_by_title("Test Entry")
        assert retrieved.id == sample_entry.id

    def test_save_relation_and_integrity(self, lexicon):
        e1 = Entry(title="A", content="...")
        e2 = Entry(title="B", content="...")
        lexicon.save(e1)
        lexicon.save(e2)

        rel = Relation(from_id=e1.id, to_id=e2.id, connection_type="link")
        lexicon.save_relation(rel)

        # Verificar que existe
        assert lexicon.check_relation(rel) is True

        # Verificar relaciones entrantes/salientes
        in_rels = lexicon.get_in_relations(e2.id)
        out_rels = lexicon.get_out_relations(e1.id)

        assert len(in_rels) == 1
        assert in_rels[0].from_id == e1.id
        assert len(out_rels) == 1
        assert out_rels[0].to_id == e2.id

    def test_delete_cascading(self, lexicon, sample_entry):
        # 1. Crear entrada y una relación asociada
        target_entry = Entry(title="Target", content="...")
        lexicon.save(sample_entry)
        lexicon.save(target_entry)

        rel = Relation(from_id=sample_entry.id, to_id=target_entry.id)
        lexicon.save_relation(rel)

        # 2. Borrar la entrada origen
        result = lexicon.delete(sample_entry.id)

        # 3. Validaciones
        assert result is True
        assert lexicon.get_by_id(sample_entry.id) is None
        # La relación debe haber sido borrada por la lógica del adaptador
        assert lexicon.check_relation(rel) is False

    def test_get_by_tag(self, lexicon):
        e1 = Entry(title="E1", content="...", tags=["ia", "fast"])
        e2 = Entry(title="E2", content="...", tags=["ia", "slow"])
        lexicon.save(e1)
        lexicon.save(e2)

        results = lexicon.get_by_tag("fast")
        assert len(results) == 1
        assert results[0].title == "E1"

    def test_get_by_date_range(self, lexicon):
        now = datetime.now()
        old_entry = Entry(
            title="Old", content="...", created_at=now - timedelta(days=10)
        )
        lexicon.save(old_entry)

        # Rango que no incluye la fecha de hace 10 días
        results = lexicon.get_by_date_range(
            start=now - timedelta(days=1), end=now + timedelta(days=1)
        )
        assert len(results) == 0

        # Rango que sí la incluye
        results = lexicon.get_by_date_range(start=now - timedelta(days=11), end=now)
        assert len(results) == 1

    def test_file_persistence(self, temp_storage, sample_entry):
        """Prueba que los datos realmente se guarden en disco al cerrar el objeto."""
        lexicon_1 = UJSONLexicon(temp_storage)
        lexicon_1.save(sample_entry)

        # Creamos una nueva instancia apuntando al mismo archivo
        lexicon_2 = UJSONLexicon(temp_storage)
        retrieved = lexicon_2.get_by_id(sample_entry.id)

        assert retrieved is not None
        assert retrieved.title == sample_entry.title

    def test_ujson_speed_and_format(self, temp_storage, lexicon, sample_entry):
        """Verifica que el archivo se escriba correctamente con ujson."""
        lexicon.save(sample_entry)

        with open(temp_storage, "r") as f:
            raw_content = f.read()
            # Verificamos que sea un JSON válido
            parsed = ujson.loads(raw_content)
            assert sample_entry.id in parsed["entries"]
