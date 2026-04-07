from abc import ABC, abstractmethod
from datetime import datetime

from ..core import Entry, Relation
from typing import List, Optional


class Lexicon(ABC):
    """
    Puerto de Persistencia (Repository Pattern).
    Define el contrato que cualquier motor de base de datos (JSON, SQL, NoSQL)
    debe cumplir para ser compatible con el Codex.
    """

    @abstractmethod
    def save(self, entry: Entry) -> None:
        """
        Guarda o actualiza una entrada.
        Si el ID ya existe, debe sobrescribir la entrada anterior (Upsert).
        El adaptador debe asegurar que los tipos de datos del dataclass
        sean compatibles con el motor de almacenamiento.
        """
        pass

    @abstractmethod
    def save_relation(self, relation: Relation) -> None:
        """
        Persiste un vínculo entre dos entradas.
        Debe evitar la creación de duplicados exactos (mismo origen, destino y tipo)
        si el motor de base de datos no lo gestiona por restricciones de unicidad.
        """
        pass

    @abstractmethod
    def get_in_relations(self, entry_id: str) -> List[Relation]:
        """
        Búsqueda de conexiones entrantes.
        Retorna todas las relaciones donde 'to_id' coincide con el ID proporcionado.
        Debe retornar una lista vacía si no hay coincidencias.
        """
        pass

    @abstractmethod
    def get_out_relations(self, entry_id: str) -> List[Relation]:
        """
        Búsqueda de conexiones salientes.
        Retorna todas las relaciones donde 'from_id' coincide con el ID proporcionado.
        Fundamental para la navegación del grafo desde el origen.
        """
        pass

    @abstractmethod
    def get_by_title(self, title: str) -> Optional[Entry]:
        """
        Busca una coincidencia exacta por título.
        Utilizado principalmente por el Codex para validar la unicidad antes de crear.
        Retorna None si no existe.
        """
        pass

    @abstractmethod
    def get_by_id(self, entry_id: str) -> Optional[Entry]:
        """
        Recupera una entrada única por su identificador (UUID).
        Es el método principal para operaciones de edición y consulta directa.
        """
        pass

    @abstractmethod
    def get_by_ids(self, entry_ids: List[str]) -> List[Entry]:
        """
        Consulta por lote (Batch Query).
        Recupera múltiples entradas basadas en una lista de IDs.
        El adaptador debe optimizar esto para evitar el problema de N+1 consultas.
        """
        pass

    @abstractmethod
    def get_by_tag(self, tag: str) -> List[Entry]:
        """
        Búsqueda por etiquetas.
        Debe retornar entradas que contengan el tag exacto en su lista de 'tags'.
        """
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Entry]:
        """
        Filtrado taxonómico.
        Retorna las entradas que pertenecen a la categoría especificada.
        """
        pass

    @abstractmethod
    def get_by_date_range(self, start: datetime, end: datetime) -> List[Entry]:
        """
        Búsqueda cronológica.
        Retorna entradas cuyo 'created_at' esté dentro del rango inclusive [start, end].
        """
        pass

    @abstractmethod
    def delete_relation(
        self, from_id: str, to_id: str, connection_type: Optional[str] = None
    ) -> bool:
        """
        Elimina un vínculo específico.
        Si 'connection_type' es None, elimina cualquier relación entre los dos IDs.
        Retorna True si se eliminó algo, False en caso contrario.
        """
        pass

    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        """
        Eliminación Atómica (Cascada Manual).
        El adaptador DEBE garantizar que al eliminar una entrada:
        1. Se borren todas las relaciones donde la entrada es origen (out_relations).
        2. Se borren todas las relaciones donde la entrada es destino (in_relations).
        3. Se borre el objeto Entry.
        Retorna True si la entrada existía y fue eliminada.
        """
        pass

    @abstractmethod
    def check_relation(self, relation: Relation) -> bool:
        """
        Verifica la existencia de un vínculo.
        Utilizado para validaciones lógicas antes de intentar guardar (save_relation).
        """
        pass
