from abc import ABC, abstractmethod

from ..core import Entry, Relation
from typing import List, Optional


class Lexicon(ABC):
    @abstractmethod
    def save(self, entry: Entry) -> None:
        pass

    @abstractmethod
    def get_by_id(self, entry_id: str) -> Optional[Entry]:
        pass

    @abstractmethod
    def find_by_tag(self, tag: str) -> List[Entry]:
        pass

    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        """Elimina una entrada por su ID."""
        pass

    @abstractmethod
    def add_relation(self, relation: Relation) -> None:
        pass

    @abstractmethod
    def remove_relation(self, relation: Relation) -> None:
        pass
