import pytest
from datetime import datetime

# Asumiendo la estructura de carpetas de tu proyecto
from cc_book_kit.core import Entry, Relation
from cc_book_kit.capsule.PydanticLexicon import PydanticLexicon


@pytest.fixture
def temp_storage(tmp_path):
    """Crea una ruta temporal para el archivo JSON de prueba."""
    return str(tmp_path / "test_codex.json")


@pytest.fixture
def lexicon(temp_storage):
    """Instancia el adaptador con la ruta temporal."""
    return PydanticLexicon(storage_path=temp_storage)


def test_save_and_get_entry(lexicon):
    """Verifica que una entrada se guarde y recupere manteniendo la integridad."""
    entry = Entry(
        title="Test Pydantic",
        content="Contenido de prueba",
        tags=["pydantic", "test"],
        category="Tech",
    )

    lexicon.save(entry)
    retrieved = lexicon.get_by_id(entry.id)

    assert retrieved is not None
    assert retrieved.id == entry.id
    assert retrieved.title == "Test Pydantic"
    assert "pydantic" in retrieved.tags
    # Verifica que la conversión de fecha (ISO -> datetime) sea correcta
    assert isinstance(retrieved.created_at, datetime)


def test_save_relation_and_integrity(lexicon):
    """Verifica la persistencia de relaciones y la prevención de duplicados."""
    e1 = Entry(content="Origen")
    e2 = Entry(content="Destino")
    lexicon.save(e1)
    lexicon.save(e2)

    relation = Relation(from_id=e1.id, to_id=e2.id, connection_type="link")

    lexicon.save_relation(relation)

    # Verificar que existe
    assert lexicon.check_relation(relation) is True

    # Intentar guardar duplicado (no debería generar error, pero Lexicon debe manejarlo)
    lexicon.save_relation(relation)

    out_rels = lexicon.get_out_relations(e1.id)
    assert len(out_rels) == 1
    assert out_rels[0].to_id == e2.id


def test_atomic_delete(lexicon):
    """Verifica que al borrar una entrada se limpien sus relaciones (Cascada Manual)."""
    e1 = Entry(content="A")
    e2 = Entry(content="B")
    lexicon.save(e1)
    lexicon.save(e2)

    rel = Relation(from_id=e1.id, to_id=e2.id)
    lexicon.save_relation(rel)

    # Ejecutar borrado atómico definido en el contrato Lexicon
    success = lexicon.delete(e1.id)

    assert success is True
    assert lexicon.get_by_id(e1.id) is None
    # La relación debe haber desaparecido
    assert lexicon.check_relation(rel) is False


def test_filter_by_tag_and_category(lexicon):
    """Prueba las capacidades de filtrado del adaptador."""
    e1 = Entry(content="E1", tags=["python"], category="Dev")
    e2 = Entry(content="E2", tags=["python", "logic"], category="Math")

    lexicon.save(e1)
    lexicon.save(e2)

    python_entries = lexicon.get_by_tag("python")
    dev_entries = lexicon.get_by_category("Dev")

    assert len(python_entries) == 2
    assert len(dev_entries) == 1
    assert dev_entries[0].content == "E1"


def test_pydantic_validation_error(temp_storage):
    """
    Verifica que Pydantic protege la integridad si el archivo
    se corrompe externamente con tipos inválidos.
    """
    import json

    # Escribimos manualmente basura en el archivo
    bad_data = {
        "entries": {
            "invalid_id": {
                "id": "invalid_id",
                "title": 12345,  # Debería ser string
                "content": "Contenido",
                "created_at": "esto no es una fecha",
            }
        },
        "relations": [],
    }

    with open(temp_storage, "w") as f:
        json.dump(bad_data, f)

    lexicon = PydanticLexicon(storage_path=temp_storage)

    # Al intentar leer, el adaptador debe manejar el error de Pydantic
    # o fallar si no se capturó. En la implementación sugerida,
    # retorna un storage vacío si hay error de validación.
    entry = lexicon.get_by_id("invalid_id")
    assert entry is None
