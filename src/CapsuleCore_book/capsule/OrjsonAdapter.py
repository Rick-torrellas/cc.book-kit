import orjson
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from dataclasses import asdict

from .Lexicon import Lexicon
from ..core import Entry, Relation


class OrjsonAdapter(Lexicon):
    def __init__(self, storage_path: str = "./data/codex"):
        self.storage_path = Path(storage_path)
        self.relations_path = self.storage_path / "relations.json"

        # Crear directorios de persistencia si no existen
        self.storage_path.mkdir(parents=True, exist_ok=True)
        if not self.relations_path.exists():
            self._write_relations([])

    def _get_entry_path(self, entry_id: str) -> Path:
        return self.storage_path / f"{entry_id}.json"

    # --- Implementación del Contrato ---

    def save(self, entry: Entry) -> None:
        file_path = self._get_entry_path(entry.id)
        # OPT_SERIALIZE_DATACLASS: permite volcar la dataclass directamente
        # OPT_NAIVE_UTC: asegura que los datetime se guarden en formato ISO compatible
        data = orjson.dumps(
            entry,
            option=orjson.OPT_INDENT_2
            | orjson.OPT_SERIALIZE_DATACLASS
            | orjson.OPT_NAIVE_UTC,
        )
        with open(file_path, "wb") as f:
            f.write(data)

    def get_by_id(self, entry_id: str) -> Optional[Entry]:
        file_path = self._get_entry_path(entry_id)
        if not file_path.exists():
            return None

        with open(file_path, "rb") as f:
            raw_data = orjson.loads(f.read())

            # Re-hidratación de fechas (orjson carga fechas como strings ISO)
            if raw_data.get("created_at"):
                raw_data["created_at"] = datetime.fromisoformat(raw_data["created_at"])
            if raw_data.get("updated_at"):
                raw_data["updated_at"] = datetime.fromisoformat(raw_data["updated_at"])

            return Entry(**raw_data)

    def delete(self, entry_id: str) -> bool:
        """Elimina la entrada y limpia sus relaciones."""
        file_path = self._get_entry_path(entry_id)
        if not file_path.exists():
            return False

        # 1. Eliminar archivo de la entrada
        file_path.unlink()

        # 2. Limpiar relaciones donde el ID sea origen o destino
        relations = self._read_relations()
        filtered_relations = [
            r for r in relations if r["from_id"] != entry_id and r["to_id"] != entry_id
        ]

        if len(relations) != len(filtered_relations):
            self._write_relations(filtered_relations)

        return True

    def find_by_tag(self, tag: str) -> List[Entry]:
        results = []
        target_tag = tag.lower().strip()

        for file in self.storage_path.glob("*.json"):
            if file.name == "relations.json":
                continue

            entry = self.get_by_id(file.stem)
            if entry and any(target_tag == t.lower() for t in entry.tags):
                results.append(entry)
        return results

    # --- Gestión de Relaciones ---

    def _read_relations(self) -> List[dict]:
        try:
            with open(self.relations_path, "rb") as f:
                return orjson.loads(f.read())
        except orjson.JSONDecodeError, FileNotFoundError:
            return []

    def _write_relations(self, relations: List[dict]):
        with open(self.relations_path, "wb") as f:
            f.write(orjson.dumps(relations, option=orjson.OPT_INDENT_2))

    def add_relation(self, relation: Relation) -> None:
        relations = self._read_relations()
        rel_dict = asdict(relation)

        # Evitar duplicados exactos en la lista de relaciones
        if rel_dict not in relations:
            relations.append(rel_dict)
            self._write_relations(relations)

    def remove_relation(self, relation: Relation) -> None:
        relations = self._read_relations()
        rel_dict = asdict(relation)

        # Filtramos para quitar la relación específica
        new_relations = [r for r in relations if r != rel_dict]

        if len(relations) != len(new_relations):
            self._write_relations(new_relations)
