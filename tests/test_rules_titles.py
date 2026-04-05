import pytest

from CapsuleCore_book.core import Codex

def test_rules_title_stripping(codex: Codex):
    # Test que limpia espacios
    result = codex._rules_title("  Título Sucio  ")
    assert result == "Título Sucio"

def test_rules_title_max_length_exceeded(codex: Codex):
    # Test de límite de caracteres
    long_title = "a" * 151 # El default en tu Policy es 150
    with pytest.raises(ValueError, match="Exceeds maximum length"):
        codex._rules_title(long_title)

def test_rules_title_uniqueness_error(codex, mock_repo):
    # Configurar el mock con una entrada existente
    from CapsuleCore_book.core import Entry
    existing = Entry(title="Existente", content="...")
    mock_repo.save(existing)
    
    with pytest.raises(ValueError, match="Ya existe una entrada"):
        codex._rules_title("Existente")

def test_rules_title_allow_same_id_on_edit(codex: Codex, mock_repo):
    # Validar que si es la misma entrada (edición), permita el mismo título
    from CapsuleCore_book.core import Entry
    existing = Entry(title="Original", content="...")
    mock_repo.save(existing)
    
    # No debería lanzar error porque el ID coincide
    result = codex._rules_title("Original", current_entry_id=existing.id)
    assert result == "Original"