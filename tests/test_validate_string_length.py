import pytest


def test_validate_string_length_success(codex):
    # Caso normal: string corto
    text = "Hola mundo"
    assert codex._validate_string_length(text, max_length=20) == text


def test_validate_string_length_exact_limit(codex):
    # Caso límite: tiene exactamente el largo permitido
    text = "a" * 150
    assert codex._validate_string_length(text, max_length=150) == text


def test_validate_string_length_exceeded(codex):
    # Caso de error: se pasa por uno
    text = "a" * 151
    with pytest.raises(ValueError, match="Exceeds maximum length"):
        codex._validate_string_length(text, max_length=150)


def test_validate_string_length_default_value(codex):
    # Probar que si no pasas el segundo argumento, usa el default (255)
    text = "a" * 256
    with pytest.raises(ValueError):
        codex._validate_string_length(text)
