import pytest
import sqlite3
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field

from CapsuleCore_book.capsule.SQLiteAdapter import SQLiteAdapter


# --- Importa aquí tus clases reales ---
# from tu_modulo import SQLiteAdapter, Entry, Relation


@dataclass
class Entry:
    id: str
    title: str
    content: str
    tags: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class Relation:
    from_id: str
    to_id: str
    connection_type: str


# --- Fixtures ---


@pytest.fixture
def temp_db(tmp_path):
    """Crea una ruta temporal para la base de datos en cada test."""
    db_file = tmp_path / "test_knowledge.db"
    return str(db_file)


@pytest.fixture
def repo(temp_db):
    """Instancia el repositorio usando el archivo temporal."""
    return SQLiteAdapter(db_path=temp_db)


@pytest.fixture
def sample_entry():
    return Entry(
        id="entry-123",
        title="Testing Pytest",
        content="Contenido de prueba para el repositorio",
        tags=["unit-test", "python"],
        created_at=datetime(2024, 5, 20, 10, 30),
        updated_at=datetime(2024, 5, 20, 11, 0),
        metadata={"priority": "high"},
    )


# --- Tests ---


class TestSQLiteAdapter:
    def test_save_and_retrieve(self, repo, sample_entry):
        # 1. Guardar
        repo.save(sample_entry)

        # 2. Recuperar y verificar campos
        retrieved = repo.get_by_id(sample_entry.id)

        assert retrieved is not None
        assert retrieved.id == "entry-123"
        assert retrieved.title == "Testing Pytest"
        assert "unit-test" in retrieved.tags
        assert retrieved.metadata["priority"] == "high"
        assert isinstance(retrieved.created_at, datetime)

    def test_upsert_behavior(self, repo, sample_entry):
        repo.save(sample_entry)

        # Modificar solo el título
        sample_entry.title = "Nuevo Título"
        repo.save(sample_entry)

        retrieved = repo.get_by_id(sample_entry.id)
        assert retrieved.title == "Nuevo Título"
        assert retrieved.content == "Contenido de prueba para el repositorio"

    def test_find_by_tag_search(self, repo, sample_entry):
        repo.save(sample_entry)

        # Añadir otra entrada con tags distintos
        entry2 = Entry(
            id="entry-456",
            title="Otro",
            content="...",
            tags=["sql"],
            created_at=datetime.now(),
        )
        repo.save(entry2)

        # Buscar tag que existe en sample_entry
        results = repo.find_by_tag("python")
        assert len(results) == 1
        assert results[0].id == "entry-123"

    def test_delete_cascades_relations(self, repo, sample_entry):
        # Crear dos entradas
        entry2 = Entry(
            id="entry-2", title="B", content="...", tags=[], created_at=datetime.now()
        )
        repo.save(sample_entry)
        repo.save(entry2)

        # Crear relación
        rel = Relation(
            from_id=sample_entry.id, to_id=entry2.id, connection_type="links"
        )
        repo.add_relation(rel)

        # Borrar la entrada origen
        repo.delete(sample_entry.id)

        # Verificar que la entrada no existe
        assert repo.get_by_id(sample_entry.id) is None

        # Verificar que la relación se limpió (vía manual si no tienes get_relations)
        with sqlite3.connect(repo.db_path) as conn:
            res = conn.execute(
                "SELECT * FROM relations WHERE from_id = ?", (sample_entry.id,)
            ).fetchall()
            assert len(res) == 0

    def test_get_non_existent_returns_none(self, repo):
        assert repo.get_by_id("non-existent") is None

    def test_remove_specific_relation(self, repo):
        # Setup de dos entradas y una relación
        e1 = Entry(id="a", title="T1", content="C1", tags=[], created_at=datetime.now())
        e2 = Entry(id="b", title="T2", content="C2", tags=[], created_at=datetime.now())
        repo.save(e1)
        repo.save(e2)
        rel = Relation(from_id="a", to_id="b", connection_type="test")

        repo.add_relation(rel)
        repo.remove_relation(rel)

        with sqlite3.connect(repo.db_path) as conn:
            res = conn.execute("SELECT * FROM relations WHERE from_id = 'a'").fetchall()
            assert len(res) == 0
