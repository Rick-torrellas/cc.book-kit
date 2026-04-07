import pytest
import orjson
from datetime import datetime, timedelta

from CapsuleCore_book.core import Entry, Relation
from CapsuleCore_book.capsule import ORJSONLexicon

@pytest.fixture
def temp_file(tmp_path):
    """Crea un archivo temporal para las pruebas."""
    return tmp_path / "test_orjson_codex.json"

@pytest.fixture
def lexicon(temp_file):
    """Instancia el adaptador ORJSON con el archivo temporal."""
    return ORJSONLexicon(storage_path=str(temp_file))

def test_orjson_initialization(temp_file):
    """Verifica que el archivo se cree con la estructura correcta (binaria)."""
    lexicon = ORJSONLexicon(storage_path=str(temp_file))  # noqa: F841
    assert temp_file.exists()
    
    # Leer como binario para verificar que orjson escribió correctamente
    with open(temp_file, "rb") as f:
        data = orjson.loads(f.read())
        assert "entries" in data
        assert "relations" in data

def test_save_and_retrieve_complex_entry(lexicon):
    """Prueba el ciclo de vida de una Entry con metadatos y tipos nativos."""
    entry = Entry(
        title="Rendimiento Orjson",
        content="Contenido de alta velocidad",
        tags=["performance", "python"],
        category="DevLog",
        metadata={"priority": 1, "nested": {"key": "value"}}
    )
    
    lexicon.save(entry)
    retrieved = lexicon.get_by_id(entry.id)
    
    assert retrieved is not None
    assert retrieved.id == entry.id
    assert retrieved.metadata["priority"] == 1
    assert isinstance(retrieved.created_at, datetime)

def test_relation_persistence(lexicon):
    """Prueba que las relaciones se guarden y filtren correctamente."""
    e1 = Entry(content="Entry 1")
    e2 = Entry(content="Entry 2")
    lexicon.save(e1)
    lexicon.save(e2)
    
    rel = Relation(from_id=e1.id, to_id=e2.id, connection_type="mentions")
    lexicon.save_relation(rel)
    
    # Verificar existencia
    assert lexicon.check_relation(rel) is True
    
    # Verificar filtros de entrada/salida
    in_rels = lexicon.get_in_relations(e2.id)
    out_rels = lexicon.get_out_relations(e1.id)
    
    assert len(in_rels) == 1
    assert in_rels[0].from_id == e1.id
    assert len(out_rels) == 1
    assert out_rels[0].connection_type == "mentions"

def test_delete_cascading(lexicon):
    """Verifica que el borrado elimine la entrada y sus vínculos asociados."""
    e1 = Entry(content="Target")
    e2 = Entry(content="Source")
    lexicon.save(e1)
    lexicon.save(e2)
    
    rel = Relation(from_id=e2.id, to_id=e1.id)
    lexicon.save_relation(rel)
    
    # Borrar e1 (el destino de la relación)
    lexicon.delete(e1.id)
    
    assert lexicon.get_by_id(e1.id) is None
    assert lexicon.check_relation(rel) is False
    assert len(lexicon.get_out_relations(e2.id)) == 0

def test_date_range_filtering(lexicon):
    """Prueba la búsqueda cronológica (crítico para orjson por el formato ISO)."""
    now = datetime.now()
    old_date = now - timedelta(days=10)
    
    e_new = Entry(content="New", created_at=now)
    e_old = Entry(content="Old", created_at=old_date)
    
    lexicon.save(e_new)
    lexicon.save(e_old)
    
    # Rango que solo incluye la nueva
    results = lexicon.get_by_date_range(now - timedelta(hours=1), now + timedelta(hours=1))
    
    assert len(results) == 1
    assert results[0].content == "New"

def test_delete_specific_relation(lexicon):
    """Prueba el método delete_relation con tipos de conexión."""
    e1_id, e2_id = "1", "2"
    rel1 = Relation(from_id=e1_id, to_id=e2_id, connection_type="type_a")
    rel2 = Relation(from_id=e1_id, to_id=e2_id, connection_type="type_b")
    
    lexicon.save_relation(rel1)
    lexicon.save_relation(rel2)
    
    # Borrar solo la de tipo A
    lexicon.delete_relation(e1_id, e2_id, connection_type="type_a")
    
    assert lexicon.check_relation(rel1) is False
    assert lexicon.check_relation(rel2) is True

def test_get_by_ids_bulk(lexicon):
    """Verifica la recuperación por lista de IDs."""
    ids = []
    for i in range(3):
        e = Entry(content=f"Entry {i}")
        lexicon.save(e)
        ids.append(e.id)
    
    results = lexicon.get_by_ids([ids[0], ids[2]])
    assert len(results) == 2
    contents = [r.content for r in results]
    assert "Entry 0" in contents
    assert "Entry 2" in contents