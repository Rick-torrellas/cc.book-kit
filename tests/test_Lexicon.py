import pytest
from typing import List
from dataclasses import dataclass

from CapsuleCore_book.capsule.Lexicon import Lexicon


# --- Mocks de dependencias (ajusta según tus archivos reales) ---
@dataclass
class Entry:
    id: str
    content: str
    tags: List[str]


@dataclass
class Relation:
    from_id: str
    to_id: str


# --- La Suite de Tests Base ---
class LexiconTests:
    """
    Clase base de pruebas. No se ejecuta sola, se hereda en
    las implementaciones concretas.
    """

    def test_save_and_get_by_id(self, repo):
        entry = Entry(id="1", content="Test", tags=["tech"])
        repo.save(entry)

        result = repo.get_by_id("1")
        assert result == entry
        assert result.id == "1"

    def test_get_by_id_returns_none_if_not_exists(self, repo):
        assert repo.get_by_id("non-existent") is None

    def test_find_by_tag(self, repo):
        e1 = Entry(id="1", content="A", tags=["python"])
        e2 = Entry(id="2", content="B", tags=["python", "ai"])
        e3 = Entry(id="3", content="C", tags=["ai"])

        for e in [e1, e2, e3]:
            repo.save(e)

        python_entries = repo.find_by_tag("python")
        assert len(python_entries) == 2
        assert e1 in python_entries
        assert e2 in python_entries

    def test_delete_entry(self, repo):
        entry = Entry(id="del-me", content="Bye", tags=[])
        repo.save(entry)

        deleted = repo.delete("del-me")
        assert deleted is True
        assert repo.get_by_id("del-me") is None

    def test_delete_non_existent_returns_false(self, repo):
        assert repo.delete("ghost") is False


# Implementación concreta simple para el ejemplo
class InMemoryRepository(Lexicon):
    def __init__(self):
        self.entries = {}
        self.relations = []

    def save(self, entry):
        self.entries[entry.id] = entry

    def get_by_id(self, entry_id):
        return self.entries.get(entry_id)

    def find_by_tag(self, tag):
        return [e for e in self.entries.values() if tag in e.tags]

    def delete(self, entry_id):
        return self.entries.pop(entry_id, None) is not None

    def add_relation(self, relation):
        self.relations.append(relation)

    def remove_relation(self, relation):
        self.relations.remove(relation)


# --- El Test Final ---
class TestInMemoryRepository(LexiconTests):
    @pytest.fixture
    def repo(self):
        return InMemoryRepository()
