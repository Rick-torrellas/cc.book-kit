import pytest
from typing import List, Optional
from datetime import datetime
from cc_book_kit.capsule import Lexicon
from cc_book_kit.core import Entry, Relation


class InMemoryLexicon(Lexicon):
    def __init__(self):
        self.entries = {}
        self.relations = []

    def save(self, entry: Entry) -> None:
        self.entries[entry.id] = entry

    def get_by_id(self, entry_id: str) -> Optional[Entry]:
        return self.entries.get(entry_id)

    def get_by_title(self, title: str) -> Optional[Entry]:
        return next((e for e in self.entries.values() if e.title == title), None)

    def save_relation(self, relation: Relation) -> None:
        if not self.check_relation(relation):
            self.relations.append(relation)

    def check_relation(self, relation: Relation) -> bool:
        return any(
            r.from_id == relation.from_id
            and r.to_id == relation.to_id
            and r.connection_type == relation.connection_type
            for r in self.relations
        )

    # Implementar los demás como pass o listas vacías para que no falle la interfaz
    def get_in_relations(self, entry_id: str) -> List[Relation]:
        return [r for r in self.relations if r.to_id == entry_id]

    def get_out_relations(self, entry_id: str) -> List[Relation]:
        return [r for r in self.relations if r.from_id == entry_id]

    def delete(self, entry_id: str) -> bool:
        """Implementación atómica para evitar huérfanos según contrato de Lexicon."""
        if entry_id not in self.entries:
            return False

        # 1. Eliminar todas las relaciones asociadas (entrantes y salientes)
        self.relations = [
            r for r in self.relations if r.from_id != entry_id and r.to_id != entry_id
        ]

        # 2. Eliminar la entrada
        del self.entries[entry_id]
        return True

    def get_by_ids(self, entry_ids: List[str]) -> List[Entry]:
        return [self.entries[eid] for eid in entry_ids if eid in self.entries]

    def get_by_tag(self, tag: str) -> List[Entry]:
        return [e for e in self.entries.values() if tag in e.tags]

    def get_by_category(self, category: str) -> List[Entry]:
        return [e for e in self.entries.values() if e.category == category]

    def get_by_date_range(self, start: datetime, end: datetime) -> List[Entry]:
        return [e for e in self.entries.values() if start <= e.created_at <= end]

    def delete_relation(
        self, from_id: str, to_id: str, connection_type: Optional[str] = None
    ) -> bool:
        initial_count = len(self.relations)
        self.relations = [
            r
            for r in self.relations
            if not (
                r.from_id == from_id
                and r.to_id == to_id
                and (connection_type is None or r.connection_type == connection_type)
            )
        ]
        return len(self.relations) < initial_count


@pytest.fixture
def mock_repo():
    return InMemoryLexicon()


@pytest.fixture
def codex(mock_repo):
    from cc_book_kit.core import Codex

    return Codex(repository=mock_repo)
