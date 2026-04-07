import ujson
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from .Lexicon import Lexicon
from ..core import Entry, Relation


class UJSONLexicon(Lexicon):
    """
    Adaptador de persistencia que utiliza ujson para alta velocidad de
    serialización/deserialización en archivos planos.
    """

    def __init__(self, storage_path: str = "codex_data.json"):
        self.storage_path = Path(storage_path)
        self._initialize_storage()

    def _initialize_storage(self):
        """Prepara el archivo con una estructura de grafo inicial si no existe."""
        if not self.storage_path.exists():
            self._write_data({"entries": {}, "relations": []})

    def _read_data(self) -> Dict:
        """Lee el archivo usando ujson. Retorna dict vacío si hay error."""
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return ujson.load(f)
        except ValueError, FileNotFoundError:
            return {"entries": {}, "relations": []}

    def _write_data(self, data: Dict):
        """Escribe datos en el archivo. ujson.dump es significativamente más rápido."""
        with open(self.storage_path, "w", encoding="utf-8") as f:
            # escape_forward_slashes=False es útil para URLs en metadata
            ujson.dump(data, f, indent=4, escape_forward_slashes=False)

    # --- Implementación del Puerto Lexicon ---

    def save(self, entry: Entry) -> None:
        data = self._read_data()
        # Convertimos el Entry (frozen dataclass) a un dict serializable
        data["entries"][entry.id] = {
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "tags": entry.tags,
            "category": entry.category,
            "created_at": entry.created_at.isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": entry.metadata,
        }
        self._write_data(data)

    def get_by_id(self, entry_id: str) -> Optional[Entry]:
        data = self._read_data()
        entry_dict = data["entries"].get(entry_id)
        return self._map_to_entry(entry_dict) if entry_dict else None

    def get_by_title(self, title: str) -> Optional[Entry]:
        data = self._read_data()
        for e in data["entries"].values():
            if e.get("title") == title:
                return self._map_to_entry(e)
        return None

    def save_relation(self, relation: Relation) -> None:
        data = self._read_data()
        if not self._check_relation_in_data(data, relation):
            data["relations"].append(
                {
                    "from_id": relation.from_id,
                    "to_id": relation.to_id,
                    "connection_type": relation.connection_type,
                    "metadata": relation.metadata,
                }
            )
            self._write_data(data)

    def get_in_relations(self, entry_id: str) -> List[Relation]:
        data = self._read_data()
        return [
            self._map_to_relation(r)
            for r in data["relations"]
            if r["to_id"] == entry_id
        ]

    def get_out_relations(self, entry_id: str) -> List[Relation]:
        data = self._read_data()
        return [
            self._map_to_relation(r)
            for r in data["relations"]
            if r["from_id"] == entry_id
        ]

    def delete(self, entry_id: str) -> bool:
        data = self._read_data()
        if entry_id not in data["entries"]:
            return False

        # 1. Limpieza de relaciones (Integridad referencial manual)
        data["relations"] = [
            r
            for r in data["relations"]
            if r["from_id"] != entry_id and r["to_id"] != entry_id
        ]

        # 2. Eliminar la entrada
        del data["entries"][entry_id]

        self._write_data(data)
        return True

    def check_relation(self, relation: Relation) -> bool:
        data = self._read_data()
        return self._check_relation_in_data(data, relation)

    def get_by_ids(self, entry_ids: List[str]) -> List[Entry]:
        """Recupera múltiples entradas de forma eficiente."""
        data = self._read_data()
        results = []
        for eid in entry_ids:
            entry_dict = data["entries"].get(eid)
            if entry_dict:
                results.append(self._map_to_entry(entry_dict))
        return results

    def get_by_tag(self, tag: str) -> List[Entry]:
        """Filtra entradas por un tag específico."""
        data = self._read_data()
        return [
            self._map_to_entry(e)
            for e in data["entries"].values()
            if tag in e.get("tags", [])
        ]

    def get_by_category(self, category: str) -> List[Entry]:
        """Filtra entradas por categoría."""
        data = self._read_data()
        return [
            self._map_to_entry(e)
            for e in data["entries"].values()
            if e.get("category") == category
        ]

    def get_by_date_range(self, start: datetime, end: datetime) -> List[Entry]:
        """Filtra entradas por rango de fechas de creación."""
        data = self._read_data()
        results = []
        for e in data["entries"].values():
            created_at = datetime.fromisoformat(e["created_at"])
            if start <= created_at <= end:
                results.append(self._map_to_entry(e))
        return results

    def delete_relation(
        self, from_id: str, to_id: str, connection_type: Optional[str] = None
    ) -> bool:
        """Elimina una relación específica entre dos entradas."""
        data = self._read_data()
        initial_count = len(data["relations"])

        data["relations"] = [
            r
            for r in data["relations"]
            if not (
                r["from_id"] == from_id
                and r["to_id"] == to_id
                and (connection_type is None or r["connection_type"] == connection_type)
            )
        ]

        if len(data["relations"]) < initial_count:
            self._write_data(data)
            return True
        return False

    # --- Helpers Privados ---

    def _check_relation_in_data(self, data: Dict, relation: Relation) -> bool:
        return any(
            r["from_id"] == relation.from_id
            and r["to_id"] == relation.to_id
            and r["connection_type"] == relation.connection_type
            for r in data["relations"]
        )

    def _map_to_entry(self, d: Dict) -> Entry:
        return Entry(
            id=d["id"],
            title=d["title"],
            content=d["content"],
            tags=d["tags"],
            category=d["category"],
            created_at=datetime.fromisoformat(d["created_at"]),
            updated_at=datetime.fromisoformat(d["updated_at"]),
            metadata=d.get("metadata", {}),
        )

    def _map_to_relation(self, d: Dict) -> Relation:
        return Relation(
            from_id=d["from_id"],
            to_id=d["to_id"],
            connection_type=d["connection_type"],
            metadata=d.get("metadata", {}),
        )

    # Implementar métodos restantes (get_by_tag, get_by_category, etc) siguiendo el mismo patrón...
