import pytest
from CapsuleCore_book.core import Codex


def test_validate_string_content_success(codex: Codex):
    # Caso positivo: devuelve el string si tiene contenido
    text = "Contenido válido"
    assert codex._validate_string_content(text) == text


def test_validate_string_content_empty(codex: Codex):
    # Caso negativo: string vacío
    with pytest.raises(ValueError, match="cannot be empty"):
        codex._validate_string_content("")
