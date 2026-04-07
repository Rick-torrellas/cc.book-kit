import json
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from .Lexicon import Lexicon
from ..core import Entry, Relation


class JSONLexicon(Lexicon):
    def __init__(self, storage_path: str = "codex_data.json"):
        self.storage_path = Path(storage_path)
        self._initialize_storage()

    def _initialize_storage(self):
        """Crea el archivo si no existe con la estructura básica."""
        if not self.storage_path.exists():
            self._write_data({"entries": {}, "relations": []})

    def _read_data(self) -> Dict:
        """Lee y parsea el archivo JSON."""
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError, FileNotFoundError:
            return {"entries": {}, "relations": []}

    def _write_data(self, data: Dict):
        """Guarda los datos en el archivo JSON."""
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, default=str)

    # --- Implementación de Interfaz Lexicon ---

    def save(self, entry: Entry) -> None:
        data = self._read_data()
        # Convertimos el dataclass a dict para JSON
        entry_dict = {
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "tags": entry.tags,
            "category": entry.category,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
            "metadata": entry.metadata,
        }
        data["entries"][entry.id] = entry_dict
        self._write_data(data)

    def save_relation(self, relation: Relation) -> None:
        data = self._read_data()
        rel_dict = {
            "from_id": relation.from_id,
            "to_id": relation.to_id,
            "connection_type": relation.connection_type,
            "metadata": relation.metadata,
        }
        # Evitar duplicados exactos antes de guardar
        if not self.check_relation(relation):
            data["relations"].append(rel_dict)
            self._write_data(data)

    def get_by_id(self, entry_id: str) -> Optional[Entry]:
        data = self._read_data()
        item = data["entries"].get(entry_id)
        return self._map_to_entry(item) if item else None

    def get_by_title(self, title: str) -> Optional[Entry]:
        data = self._read_data()
        for item in data["entries"].values():
            if item.get("title") == title:
                return self._map_to_entry(item)
        return None

    def get_by_ids(self, entry_ids: List[str]) -> List[Entry]:
        data = self._read_data()
        return [
            self._map_to_entry(data["entries"][eid])
            for eid in entry_ids
            if eid in data["entries"]
        ]

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

    def check_relation(self, relation: Relation) -> bool:
        data = self._read_data()
        return any(
            r["from_id"] == relation.from_id
            and r["to_id"] == relation.to_id
            and r["connection_type"] == relation.connection_type
            for r in data["relations"]
        )

    def delete(self, entry_id: str) -> bool:
        data = self._read_data()
        if entry_id not in data["entries"]:
            return False

        # Eliminación atómica de relaciones (limpieza de huérfanos)
        data["relations"] = [
            r
            for r in data["relations"]
            if r["from_id"] != entry_id and r["to_id"] != entry_id
        ]

        del data["entries"][entry_id]
        self._write_data(data)
        return True

    def delete_relation(
        self, from_id: str, to_id: str, connection_type: Optional[str] = None
    ) -> bool:
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

    def get_by_tag(self, tag: str) -> List[Entry]:
        data = self._read_data()
        return [
            self._map_to_entry(e)
            for e in data["entries"].values()
            if tag in e.get("tags", [])
        ]

    def get_by_category(self, category: str) -> List[Entry]:
        data = self._read_data()
        return [
            self._map_to_entry(e)
            for e in data["entries"].values()
            if e.get("category") == category
        ]

    def get_by_date_range(self, start: datetime, end: datetime) -> List[Entry]:
        data = self._read_data()
        results = []
        for e in data["entries"].values():
            created_at = datetime.fromisoformat(e["created_at"])
            if start <= created_at <= end:
                results.append(self._map_to_entry(e))
        return results

    # --- Helpers de Mapeo ---

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
