from CapsuleCore_book.core import Codex

def test_validate_string_whitespaces_basic(codex: Codex):
    # Caso estándar
    assert codex._validate_string_whitespaces("  contenido  ") == "contenido"

def test_validate_string_whitespaces_tabs_newlines(codex: Codex):
    # Caso con tabuladores y saltos de línea
    assert codex._validate_string_whitespaces("\n\timportante\t\n") == "importante"

def test_validate_string_whitespaces_keep_internal(codex: Codex):
    # Asegurar que no rompe frases
    assert codex._validate_string_whitespaces("  frase con espacios  ") == "frase con espacios"

def test_validate_string_whitespaces_only_spaces(codex: Codex):
    # Caso de string "fantasma"
    assert codex._validate_string_whitespaces("      ") == ""