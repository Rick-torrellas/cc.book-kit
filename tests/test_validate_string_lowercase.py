def test_validate_string_lowercase_conversion(codex):
    # Caso simple: Mayúsculas a minúsculas
    assert codex._validate_string_lowercase("MÉXICO") == "méxico"

    # Caso mixto: Letras y números
    assert codex._validate_string_lowercase("User_123") == "user_123"


def test_validate_string_lowercase_already_lower(codex):
    # No debería hacer nada si ya está en minúsculas
    assert codex._validate_string_lowercase("python") == "python"


def test_validate_string_lowercase_empty(codex):
    # Debería manejar strings vacíos sin romperse
    assert codex._validate_string_lowercase("") == ""
