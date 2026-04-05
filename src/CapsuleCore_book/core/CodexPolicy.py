from dataclasses import dataclass

@dataclass(frozen=True)
class CodexPolicy:
    # Configuración de Título
    title_required: bool = True
    title_unique: bool = True
    title_max_length: int = 150
    title_strip: bool = True
    
    # Configuración de Tags (Folksonomía: Flexible y conectiva)
    tags_lowercase: bool = True
    tags_strip: bool = True
    tags_unique: bool = True
    tags_sort: bool = True
    tags_allow_empty: bool = True
    
    # Configuración de Categoría (Taxonomía: Estructural y organizativa)
    category_required: bool = True
    category_default: str = "General"
    category_capitalize: bool = True
    category_strip: bool = True
    category_max_length: int = 50