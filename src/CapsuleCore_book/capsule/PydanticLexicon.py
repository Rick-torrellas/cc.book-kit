from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from .Lexicon import Lexicon
from ..core import Entry, Relation

class EntrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    title: Optional[str]
    content: str
    tags: List[str] = []
    category: Optional[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

class RelationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    from_id: str
    to_id: str
    connection_type: str
    metadata: Dict[str, Any] = {}

class CodexStorageSchema(BaseModel):
    """Esquema de la base de datos completa"""
    entries: Dict[str, EntrySchema] = {}
    relations: List[RelationSchema] = []

class PydanticLexicon(Lexicon):
    def __init__(self, storage_path: str = "codex_pydantic.json"):
        self.storage_path = Path(storage_path)
        self._initialize_storage()

    def _initialize_storage(self):
        if not self.storage_path.exists():
            self._write_data(CodexStorageSchema())

    def _read_data(self) -> CodexStorageSchema:
        """Lee y valida el archivo completo contra el esquema."""
        try:
            if not self.storage_path.exists():
                return CodexStorageSchema()
            
            with open(self.storage_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                # La magia: Valida toda la estructura al leer
                return CodexStorageSchema(**raw_data)
        except (json.JSONDecodeError, FileNotFoundError, Exception):
            return CodexStorageSchema()

    def _write_data(self, storage: CodexStorageSchema):
        """Serializa usando el método model_dump_json de Pydantic."""
        with open(self.storage_path, "w", encoding="utf-8") as f:
            # model_dump_json maneja automáticamente datetimes a ISO strings
            f.write(storage.model_dump_json(indent=4))

    # --- Implementación Lexicon ---

    def save(self, entry: Entry) -> None:
        storage = self._read_data()
        
        # Convertimos Dataclass -> Pydantic Model
        entry_schema = EntrySchema.model_validate(entry)
        
        storage.entries[entry.id] = entry_schema
        self._write_data(storage)

    def get_by_id(self, entry_id: str) -> Optional[Entry]:
        storage = self._read_data()
        schema = storage.entries.get(entry_id)
        return self._map_to_core_entry(schema) if schema else None

    def save_relation(self, relation: Relation) -> None:
        storage = self._read_data()
        if not self.check_relation(relation):
            rel_schema = RelationSchema.model_validate(relation)
            storage.relations.append(rel_schema)
            self._write_data(storage)

    def check_relation(self, relation: Relation) -> bool:
        storage = self._read_data()
        return any(
            r.from_id == relation.from_id and 
            r.to_id == relation.to_id and 
            r.connection_type == relation.connection_type
            for r in storage.relations
        )

    def delete(self, entry_id: str) -> bool:
        storage = self._read_data()
        if entry_id not in storage.entries:
            return False

        # Limpieza de relaciones
        storage.relations = [
            r for r in storage.relations 
            if r.from_id != entry_id and r.to_id != entry_id
        ]
        
        del storage.entries[entry_id]
        self._write_data(storage)
        return True

    def get_by_title(self, title: str) -> Optional[Entry]:
        storage = self._read_data()
        for e in storage.entries.values():
            if e.title == title:
                return self._map_to_core_entry(e)
        return None

    def get_by_ids(self, entry_ids: List[str]) -> List[Entry]:
        storage = self._read_data()
        return [
            self._map_to_core_entry(storage.entries[eid])
            for eid in entry_ids if eid in storage.entries
        ]

    def get_by_tag(self, tag: str) -> List[Entry]:
        storage = self._read_data()
        return [
            self._map_to_core_entry(e)
            for e in storage.entries.values()
            if tag in e.tags
        ]

    def get_by_category(self, category: str) -> List[Entry]:
        storage = self._read_data()
        return [
            self._map_to_core_entry(e)
            for e in storage.entries.values()
            if e.category == category
        ]

    def get_by_date_range(self, start: datetime, end: datetime) -> List[Entry]:
        storage = self._read_data()
        return [
            self._map_to_core_entry(e)
            for e in storage.entries.values()
            if start <= e.created_at <= end
        ]

    def get_in_relations(self, entry_id: str) -> List[Relation]:
        storage = self._read_data()
        return [
            self._map_to_core_relation(r)
            for r in storage.relations
            if r.to_id == entry_id
        ]

    def get_out_relations(self, entry_id: str) -> List[Relation]:
        storage = self._read_data()
        return [
            self._map_to_core_relation(r)
            for r in storage.relations
            if r.from_id == entry_id
        ]

    def delete_relation(self, from_id: str, to_id: str, connection_type: Optional[str] = None) -> bool:
        storage = self._read_data()
        initial_count = len(storage.relations)
        
        storage.relations = [
            r for r in storage.relations
            if not (
                r.from_id == from_id and 
                r.to_id == to_id and 
                (connection_type is None or r.connection_type == connection_type)
            )
        ]
        
        if len(storage.relations) < initial_count:
            self._write_data(storage)
            return True
        return False

    # --- Helpers de Mapeo (Pydantic -> Core Dataclass) ---

    def _map_to_core_entry(self, schema: EntrySchema) -> Entry:
        # Convertimos de vuelta a tu dataclass original
        return Entry(**schema.model_dump())

    def _map_to_core_relation(self, schema: RelationSchema) -> Relation:
        return Relation(**schema.model_dump())

    # Los métodos get_by_tag, get_by_category, etc. 
    # siguen la misma lógica filtrando sobre storage.entries.values()