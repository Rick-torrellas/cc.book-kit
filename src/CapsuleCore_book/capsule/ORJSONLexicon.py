import orjson
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict

from .Lexicon import Lexicon
from ..core import Entry, Relation


class ORJSONLexicon(Lexicon):
    """
    Adaptador de persistencia de ultra alto rendimiento utilizando orjson.
    Optimiza la serialización nativa de datetimes y UUIDs.
    """

    def __init__(self, storage_path: str = "codex_data.json"):
        self.storage_path = Path(storage_path)
        self._initialize_storage()

    def _initialize_storage(self):
        """Prepara el archivo con una estructura de grafo inicial si no existe."""
        if not self.storage_path.exists():
            self._write_data({"entries": {}, "relations": []})

    def _read_data(self) -> Dict:
        """Lee el archivo usando orjson.loads (retorna bytes internamente para velocidad)."""
        try:
            with open(self.storage_path, "rb") as f:
                return orjson.loads(f.read())
        except (orjson.JSONDecodeError, FileNotFoundError):
            return {"entries": {}, "relations": []}

    def _write_data(self, data: Dict):
        """
        Escribe datos usando orjson.
        OPT_INDENT_2: Para mantener legibilidad similar a tu JSONLexicon.
        OPT_UTC_Z: Asegura que los datetimes sigan el estándar ISO con sufijo Z si es necesario.
        """
        with open(self.storage_path, "wb") as f:
            # orjson retorna bytes, por eso abrimos el archivo en modo 'wb'
            f.write(orjson.dumps(
                data, 
                option=orjson.OPT_INDENT_2 | orjson.OPT_UTC_Z
            ))

    # --- Implementación del Puerto Lexicon ---

    def save(self, entry: Entry) -> None:
        data = self._read_data()
        # Aprovechamos que orjson maneja datetimes nativamente si pasamos el objeto
        # Sin embargo, para mantener consistencia con el esquema de otros adaptadores,
        # lo guardamos como dict.
        data["entries"][entry.id] = {
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "tags": entry.tags,
            "category": entry.category,
            "created_at": entry.created_at,
            "updated_at": datetime.now(),
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
            data["relations"].append({
                "from_id": relation.from_id,
                "to_id": relation.to_id,
                "connection_type": relation.connection_type,
                "metadata": relation.metadata,
            })
            self._write_data(data)

    def get_in_relations(self, entry_id: str) -> List[Relation]:
        data = self._read_data()
        return [self._map_to_relation(r) for r in data["relations"] if r["to_id"] == entry_id]

    def get_out_relations(self, entry_id: str) -> List[Relation]:
        data = self._read_data()
        return [self._map_to_relation(r) for r in data["relations"] if r["from_id"] == entry_id]

    def delete(self, entry_id: str) -> bool:
        data = self._read_data()
        if entry_id not in data["entries"]:
            return False

        data["relations"] = [
            r for r in data["relations"] 
            if r["from_id"] != entry_id and r["to_id"] != entry_id
        ]
        del data["entries"][entry_id]
        self._write_data(data)
        return True

    def check_relation(self, relation: Relation) -> bool:
        data = self._read_data()
        return self._check_relation_in_data(data, relation)

    def get_by_ids(self, entry_ids: List[str]) -> List[Entry]:
        data = self._read_data()
        return [
            self._map_to_entry(data["entries"][eid]) 
            for eid in entry_ids if eid in data["entries"]
        ]

    def get_by_tag(self, tag: str) -> List[Entry]:
        data = self._read_data()
        return [self._map_to_entry(e) for e in data["entries"].values() if tag in e.get("tags", [])]

    def get_by_category(self, category: str) -> List[Entry]:
        data = self._read_data()
        return [self._map_to_entry(e) for e in data["entries"].values() if e.get("category") == category]

    def get_by_date_range(self, start: datetime, end: datetime) -> List[Entry]:
        data = self._read_data()
        results = []
        for e in data["entries"].values():
            # orjson puede devolver el string ISO, lo convertimos para el dominio
            created_at = datetime.fromisoformat(e["created_at"])
            if start <= created_at <= end:
                results.append(self._map_to_entry(e))
        return results

    def delete_relation(self, from_id: str, to_id: str, connection_type: Optional[str] = None) -> bool:
        data = self._read_data()
        initial_count = len(data["relations"])
        data["relations"] = [
            r for r in data["relations"]
            if not (r["from_id"] == from_id and r["to_id"] == to_id and 
                   (connection_type is None or r["connection_type"] == connection_type))
        ]
        if len(data["relations"]) < initial_count:
            self._write_data(data)
            return True
        return False

    # --- Helpers Privados ---

    def _check_relation_in_data(self, data: Dict, relation: Relation) -> bool:
        return any(
            r["from_id"] == relation.from_id and 
            r["to_id"] == relation.to_id and 
            r["connection_type"] == relation.connection_type
            for r in data["relations"]
        )

    def _map_to_entry(self, d: Dict) -> Entry:
        return Entry(
            id=d["id"],
            title=d["title"],
            content=d["content"],
            tags=d["tags"],
            category=d["category"],
            created_at=datetime.fromisoformat(d["created_at"]) if isinstance(d["created_at"], str) else d["created_at"],
            updated_at=datetime.fromisoformat(d["updated_at"]) if isinstance(d["updated_at"], str) else d["updated_at"],
            metadata=d.get("metadata", {}),
        )

    def _map_to_relation(self, d: Dict) -> Relation:
        return Relation(
            from_id=d["from_id"],
            to_id=d["to_id"],
            connection_type=d["connection_type"],
            metadata=d.get("metadata", {}),
        )