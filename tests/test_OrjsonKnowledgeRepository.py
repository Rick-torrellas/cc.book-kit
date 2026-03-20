import pytest
from datetime import datetime
from dataclasses import dataclass, field
from typing import List
from datetime import timezone

from CapsuleCore_book.capsule.OrjsonKnowledgeRepository import OrjsonKnowledgeRepository


# --- Mocks de las clases core para que el test funcione ---
@dataclass
class Entry:
    id: str
    content: str
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Relation:
    from_id: str
    to_id: str
    type: str


# --- Fixtures ---


@pytest.fixture
def repo(tmp_path):
    """Crea una instancia del repositorio en un directorio temporal."""
    return OrjsonKnowledgeRepository(storage_path=str(tmp_path))


@pytest.fixture
def sample_entry():
    return Entry(
        id="test-123",
        content="Contenido de prueba",
        tags=["python", "test"],
        # 2. Añade el tzinfo aquí:
        created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )


# --- Tests ---


def test_save_and_get_by_id(repo, sample_entry):
    # Guardar
    repo.save(sample_entry)

    # Recuperar
    retrieved = repo.get_by_id(sample_entry.id)

    assert retrieved is not None
    assert retrieved.id == sample_entry.id
    assert retrieved.content == sample_entry.content
    assert "python" in retrieved.tags
    # Verificar que la hidratación de fechas funciona
    assert isinstance(retrieved.created_at, datetime)
    assert retrieved.created_at == sample_entry.created_at


def test_get_non_existent_entry(repo):
    assert repo.get_by_id("ghost-id") is None


def test_delete_entry_and_file(repo, sample_entry):
    repo.save(sample_entry)
    file_path = repo._get_entry_path(sample_entry.id)
    assert file_path.exists()

    success = repo.delete(sample_entry.id)
    assert success is True
    assert not file_path.exists()
    assert repo.get_by_id(sample_entry.id) is None


def test_find_by_tag(repo):
    entry1 = Entry(id="1", content="A", tags=["IA"])
    entry2 = Entry(id="2", content="B", tags=["ia", "coding"])
    entry3 = Entry(id="3", content="C", tags=["linux"])

    repo.save(entry1)
    repo.save(entry2)
    repo.save(entry3)

    # Búsqueda case-insensitive y con espacios
    results = repo.find_by_tag(" ia ")

    assert len(results) == 2
    ids = [e.id for e in results]
    assert "1" in ids
    assert "2" in ids


def test_add_and_remove_relation(repo):
    rel = Relation(from_id="A", to_id="B", type="references")

    # Agregar
    repo.add_relation(rel)
    relations = repo._read_relations()
    assert len(relations) == 1
    assert relations[0]["from_id"] == "A"

    # Eliminar
    repo.remove_relation(rel)
    assert len(repo._read_relations()) == 0


def test_delete_entry_cleans_relations(repo, sample_entry):
    # Setup: Una entrada con una relación
    repo.save(sample_entry)
    rel = Relation(from_id=sample_entry.id, to_id="other", type="links")
    repo.add_relation(rel)

    assert len(repo._read_relations()) == 1

    # Al borrar la entrada, la relación debe desaparecer
    repo.delete(sample_entry.id)
    assert len(repo._read_relations()) == 0
