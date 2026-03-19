from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

@dataclass
class Entry:
    content: str
    title: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    # El diccionario de metadatos para flexibilidad total
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_content(self, new_content: str):
        self.content = new_content
        self.updated_at = datetime.now()