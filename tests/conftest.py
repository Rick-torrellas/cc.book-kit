import pytest
from CapsuleCore_book.capsule import Lexicon
from CapsuleCore_book.core import Entry, Relation

class InMemoryLexicon(Lexicon):
    def __init__(self):
        self.entries = {}
        self.relations = []

    def save(self, entry: Entry): self.entries[entry.id] = entry
    def get_by_id(self, entry_id: str): return self.entries.get(entry_id)
    def get_by_title(self, title: str): 
        return next((e for e in self.entries.values() if e.title == title), None)
    
    def save_relation(self, relation: Relation): self.relations.append(relation)
    def check_relation(self, relation: Relation):
        return any(r.from_id == relation.from_id and r.to_id == relation.to_id for r in self.relations)

    # Implementar los demás como pass o listas vacías para que no falle la interfaz
    def get_in_relations(self, id): return []
    def get_out_relations(self, id): return []
    def delete(self, id): return True
    def get_by_ids(self, entry_ids: list[str]):
        return [self.entries[eid] for eid in entry_ids if eid in self.entries]

    def get_by_tag(self, tag: str):
        return [e for e in self.entries.values() if tag in e.tags]

    def get_by_category(self, category: str):
        return [e for e in self.entries.values() if e.category == category]

    def get_by_date_range(self, start, end):
        return [] # Implementación mínima para PoC

    def delete_relation(self, from_id: str, to_id: str, connection_type: str = None) -> bool:
        # Asegúrate de que la firma coincida con lo que acordamos (con connection_type)
        return True

@pytest.fixture
def mock_repo():
    return InMemoryLexicon()

@pytest.fixture
def codex(mock_repo):
    from CapsuleCore_book.core import Codex
    return Codex(repository=mock_repo)