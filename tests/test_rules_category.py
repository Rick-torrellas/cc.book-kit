import pytest

from CapsuleCore_book.core import Codex
from CapsuleCore_book.core import CodexPolicy

def test_rules_category_default_assignment(codex: Codex):
    # Si enviamos None, debe devolver el valor por defecto de la Policy
    result = codex._rules_category(None)
    assert result == "General"

def test_rules_category_formatting(codex: Codex):
    # Test de limpieza de espacios y capitalización
    # "  biología  " -> "Biología"
    result = codex._rules_category("  biología  ")
    assert result == "Biología"

def test_rules_category_max_length(codex: Codex):
    # Verificar que respeta el límite de la política (ej. 50 caracteres)
    long_category = "x" * 51
    with pytest.raises(ValueError, match="Exceeds maximum length"):
        codex._rules_category(long_category)

def test_rules_category_custom_policy(mock_repo):
    # Test con una política donde la categoría NO es obligatoria y no tiene default
    custom_policy = CodexPolicy(category_required=False, category_default="")
    from CapsuleCore_book.core import Codex
    custom_codex = Codex(repository=mock_repo, policy=custom_policy)
    
    assert custom_codex._rules_category(None) == ""