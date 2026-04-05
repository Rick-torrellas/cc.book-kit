import pytest
from CapsuleCore_book.core import Entry, Codex
from CapsuleCore_book.capsule import Lexicon

def test_create_entry_success(codex: Codex, mock_repo: Lexicon):
    """
    Verifica que una entrada se cree correctamente con datos válidos
    y se guarde en el repositorio.
    """
    # 1. Datos de prueba
    title = "  Mi Primera Nota  "
    content = "Contenido de prueba"
    tags = ["Python", "  TEST  "]
    category = "Desarrollo"

    # 2. Ejecutar acción
    entry = codex.create_entry(
        title=title, 
        content=content, 
        tags=tags, 
        category=category,
        metadata={"priority": "high"}
    )

    # 3. Verificaciones de la instancia retornada
    assert isinstance(entry, Entry)
    assert entry.id is not None
    # Verifica que se aplicó el strip del título (según CodexPolicy)
    assert entry.title == "Mi Primera Nota"
    assert entry.content == content
    # Verifica que los tags se normalizaron (lowercase y strip según política)
    assert "python" in entry.tags
    assert "test" in entry.tags
    assert entry.category == "Desarrollo"
    assert entry.metadata["priority"] == "high"

    # 4. Verificar persistencia en el repositorio (mock_repo)
    saved_entry = mock_repo.get_by_id(entry.id)
    assert saved_entry is not None
    assert saved_entry.title == entry.title

def test_create_entry_duplicate_title_error(codex: Codex):
    """
    Verifica que la política de títulos únicos lance una excepción
    si intentamos crear una entrada con un título ya existente.
    """
    title = "Título Único"
    codex.create_entry(title=title, content="Primer contenido")

    # Intentar crear otra con el mismo título debería fallar
    with pytest.raises(ValueError, match=f"Ya existe una entrada con el título: '{title}'"):
        codex.create_entry(title=title, content="Segundo contenido")

def test_create_entry_default_category(codex: Codex):
    """
    Verifica que si no se proporciona categoría, se asigne la 
    categoría por defecto definida en CodexPolicy ("General").
    """
    entry = codex.create_entry(title="Nota sin categoría", content="...")
    
    assert entry.category == "General"

def test_create_entry_policy_validation_error(codex: Codex):
    """
    Verifica que si el título es requerido y se envía vacío, lance un error.
    """
    with pytest.raises(ValueError, match="El título es requerido"):
        codex.create_entry(title="", content="Contenido sin título")