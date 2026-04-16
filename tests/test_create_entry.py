import pytest
from cc_book_kit.core import Entry


def test_create_entry_success(codex):
    """Verifica que una entrada se cree correctamente con datos válidos."""
    title = "Mi Primera Entrada"
    content = "Contenido de prueba"
    tags = ["python", "tests"]
    category = "Desarrollo"

    entry = codex.create_entry(
        title=title,
        content=content,
        tags=tags,
        category=category,
        metadata={"prioridad": "alta"},
    )

    # Verificaciones básicas
    assert isinstance(entry, Entry)
    assert entry.title == title
    assert entry.content == content
    assert "python" in entry.tags
    assert entry.category == category
    assert entry.metadata["prioridad"] == "alta"
    assert entry.id is not None


def test_create_entry_policy_cleaning(codex):
    """Verifica que se apliquen las reglas de limpieza (strip, lowercase, capitalize)."""
    # El título tiene espacios, los tags están en mayúsculas y la categoría en minúsculas
    entry = codex.create_entry(
        title="  Título con Espacios  ",
        content="...",
        tags=["PYTHON ", " ARCH "],
        category="proyectos",
    )

    # Según CodexPolicy: title_strip=True, tags_lowercase=True, category_capitalize=True
    assert entry.title == "Título con Espacios"
    assert "python" in entry.tags
    assert "arch" in entry.tags
    assert entry.category == "Proyectos"


def test_create_entry_duplicate_title_error(codex):
    """Verifica que la política de títulos únicos lance una excepción."""
    title = "Título Único"
    codex.create_entry(title=title, content="Contenido 1")

    # Intentar crear otra entrada con el mismo título debería fallar
    with pytest.raises(
        ValueError, match=f"Ya existe una entrada con el título: '{title}'"
    ):
        codex.create_entry(title=title, content="Contenido 2")


def test_create_entry_default_category(codex):
    """Verifica que se asigne la categoría por defecto si no se provee una."""
    entry = codex.create_entry(title="Sin Categoría", content="...")

    # Según CodexPolicy: category_default = "General"
    assert entry.category == "General"


def test_create_entry_empty_title_error(codex):
    """Verifica que falle si el título es requerido y se envía vacío."""
    with pytest.raises(ValueError, match="El título es requerido"):
        codex.create_entry(title="", content="Contenido sin título")


def test_create_entry_tags_uniqueness_and_sort(codex):
    """Verifica que los tags sean únicos y se ordenen alfabéticamente."""
    entry = codex.create_entry(
        title="Tags Test", content="...", tags=["b", "a", "b", "c"]
    )

    # Debería resultar en ['a', 'b', 'c']
    assert entry.tags == ["a", "b", "c"]


def test_create_entry_persistence(codex, mock_repo):
    """Verifica que la entrada realmente se guarde en el repositorio (Lexicon)."""
    entry = codex.create_entry(title="Persistencia", content="Guardado")

    saved_entry = mock_repo.get_by_id(entry.id)
    assert saved_entry is not None
    assert saved_entry.title == "Persistencia"
