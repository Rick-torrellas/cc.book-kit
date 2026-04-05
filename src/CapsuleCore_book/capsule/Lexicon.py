from abc import ABC, abstractmethod
from datetime import datetime

from ..core import Entry, Relation
from typing import List, Optional


class Lexicon(ABC):
    @abstractmethod
    def save(self, entry: Entry) -> None:
        """Guarda una entrada en el repositorio."""
        pass

    @abstractmethod
    def save_relation(self, relation: Relation) -> None:
        # guarda una relacion 
        pass

    @abstractmethod
    def get_in_relations(self, entry_id: str) -> List[Relation]:
        """Retorna todas las relaciones donde 'to_id' es el ID proporcionado."""
        pass

    @abstractmethod
    def get_out_relations(self, entry_id: str) -> List[Relation]:
        """Retorna todas las relaciones donde 'from_id' es el ID proporcionado."""
        pass

    @abstractmethod
    def get_by_title(self, title: str) -> Optional[Entry]:
        """Busca una entrada exactamente por su título."""
        pass

    @abstractmethod
    def get_by_id(self, entry_id: str) -> Optional[Entry]:
        """Busca una entrada por su ID."""
        pass

    @abstractmethod
    def get_by_ids(self, entry_ids: List[str]) -> List[Entry]:
        """Recupera múltiples entradas de forma eficiente en una sola consulta."""
        pass

    @abstractmethod
    def get_by_tag(self, tag: str) -> List[Entry]:
        """Retorna todas las entradas que contienen el tag proporcionado."""
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Entry]:
        """Filtra entradas por su categoría única."""
        pass

    @abstractmethod
    def get_by_date_range(self, start: datetime, end: datetime) -> List[Entry]:
        """Filtra entradas por rango de creación (fundamental para groupBy_dates)."""
        pass

    @abstractmethod
    def delete_relation(self, from_id: str, to_id: str,connection_type: Optional[str] = None) -> bool:    
        """Elimina la relación entre dos IDs. Retorna True si tuvo éxito."""
        pass

    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        """
        Elimina de forma atómica:
        1. Todas las relaciones donde from_id == entry_id (salientes).
        2. Todas las relaciones donde to_id == entry_id (entrantes).
        3. El objeto Entry con dicho ID.
        
        Esto evita que queden relaciones huérfanas en el sistema.
        """
        pass
        
    @abstractmethod
    def check_relation(self, relation: Relation) -> bool:
        """Verifica si existe una relación específica."""
        pass


