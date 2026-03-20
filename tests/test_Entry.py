from datetime import datetime
from CapsuleCore_book.core.Entry import Entry  # Asegúrate de importar desde tu archivo


def test_entry_creation_defaults():
    """Valida que una entrada se cree correctamente con valores por defecto."""
    content = "Hola Mundo"
    entry = Entry(content=content)

    assert entry.content == content
    assert entry.title is None
    assert isinstance(entry.id, str)
    assert isinstance(entry.created_at, datetime)
    assert entry.tags == []
    assert entry.metadata == {}
    assert entry.updated_at is None


def test_entry_custom_values():
    """Valida la asignación de valores personalizados."""
    custom_id = "123-abc"
    entry = Entry(
        content="Contenido",
        title="Mi Título",
        tags=["python", "test"],
        id=custom_id,
        metadata={"author": "AI"},
    )

    assert entry.id == custom_id
    assert "python" in entry.tags
    assert entry.metadata["author"] == "AI"


def test_update_content_logic():
    """Verifica que el contenido cambie y se registre la fecha de actualización."""
    entry = Entry(content="Original")
    assert entry.updated_at is None

    original_created_at = entry.created_at
    new_text = "Editado"

    entry.update_content(new_text)

    assert entry.content == new_text
    assert isinstance(entry.updated_at, datetime)
    # El tiempo de creación no debería cambiar
    assert entry.created_at == original_created_at


def test_unique_ids():
    """Asegura que cada instancia genere un ID único."""
    entry1 = Entry(content="E1")
    entry2 = Entry(content="E2")
    assert entry1.id != entry2.id
