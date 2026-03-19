from typing import List

from ..core import Entry,Relation
from .KnowledgeRepository import KnowledgeRepository


class CodexService:
    def __init__(self, repository: KnowledgeRepository):
        self.repository = repository

    def ingest(self, entry: Entry):
        # REGLA 1: Normalización de etiquetas
        entry = self._normalize_tags(entry)
        
        # REGLA 2: Evitar duplicados
        if self.repository.get_by_id(entry.id):
            raise ValueError("Esta página ya existe en el códice.")
            
        self.repository.save(entry)
        
    def _normalize_tags(self, entry: Entry):
        """Regla interna: Limpieza de etiquetas."""
        entry.tags = list(set(t.lower().strip() for t in entry.tags))

    def create_page(self, title: str, content: str, tags: List[str] = None) -> Entry:
        """Caso de Uso: Crear un nuevo conocimiento con reglas de validación."""
        if not title.strip():
            raise ValueError("El título no puede estar vacío.")
            
        new_entry = Entry(title=title, content=content, tags=tags or [])
        self._normalize_tags(new_entry)
        
        self.repository.save(new_entry)
        return new_entry

    def edit_page(self, entry_id: str, new_content: str):
        """Caso de Uso: Editar contenido y actualizar metadatos de auditoría."""
        entry = self.repository.get_by_id(entry_id)
        if not entry:
            raise ValueError(f"No existe la página con ID {entry_id}")
        
        # 1. Aplicamos el cambio al Core
        entry.update_content(new_content)
        
        # 2. Lógica de Metadatos: Contador de ediciones
        edits = entry.metadata.get("edit_count", 0)
        entry.metadata["edit_count"] = edits + 1
        
        # 3. Persistimos
        self.repository.save(entry)
    def connect_pages(self, from_id: str, to_id: str, connection_type: str):
        """Caso de Uso: Crear una relación validando la existencia de ambos nodos."""
        if from_id == to_id:
            raise ValueError("No puedes relacionar una página consigo misma.")

        # Validamos que ambos existan antes de crear la relación
        origin = self.repository.get_by_id(from_id)
        target = self.repository.get_by_id(to_id)

        if not origin or not target:
            raise ValueError("Ambas páginas deben existir para ser relacionadas.")

        relation = Relation(from_id=from_id, to_id=to_id, connection_type=connection_type)
        self.repository.add_relation(relation)      