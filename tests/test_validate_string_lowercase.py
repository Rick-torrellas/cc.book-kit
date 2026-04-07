from CapsuleCore_book.core import Codex


def test_validate_string_lowercase_conversion(codex: Codex):
    # Caso simple: Mayúsculas a minúsculas
    assert codex._validate_string_lowercase("MÉXICO") == "méxico"

    # Caso mixto: Letras y números
    assert codex._validate_string_lowercase("User_123") == "user_123"


def test_validate_string_lowercase_already_lower(codex: Codex):
    # No debería hacer nada si ya está en minúsculas
    assert codex._validate_string_lowercase("python") == "python"


def test_validate_string_lowercase_empty(codex: Codex):
    # Debería manejar strings vacíos sin romperse
    assert codex._validate_string_lowercase("") == ""
