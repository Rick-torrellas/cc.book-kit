from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid


@dataclass(kw_only=True, frozen=True)
class Entry:
    content: str
    title: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    # El diccionario de metadatos para flexibilidad total
    metadata: Dict[str, Any] = field(default_factory=dict)
