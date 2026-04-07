def test_validate_string_whitespaces_normal_case(codex):
    """Prueba que elimina espacios al inicio y al final de un string normal."""
    input_str = "  hola mundo  "
    expected = "hola mundo"
    # Accedemos al método privado para la prueba unitaria
    assert codex._validate_string_whitespaces(input_str) == expected


def test_validate_string_whitespaces_only_spaces(codex):
    """Prueba que un string de solo espacios resulta en un string vacío."""
    input_str = "     "
    expected = ""
    assert codex._validate_string_whitespaces(input_str) == expected


def test_validate_string_whitespaces_no_spaces(codex):
    """Prueba que si no hay espacios, el string se mantiene igual."""
    input_str = "python"
    expected = "python"
    assert codex._validate_string_whitespaces(input_str) == expected


def test_validate_string_whitespaces_tabs_and_newlines(codex):
    """Prueba que también limpia tabulaciones y saltos de línea."""
    input_str = "\t\n contenido \r"
    expected = "contenido"
    assert codex._validate_string_whitespaces(input_str) == expected


def test_integration_with_create_entry_title(codex):
    """
    Prueba de integración indirecta: verifica que create_entry
    use el helper para limpiar el título según la política por defecto.
    """
    entry = codex.create_entry(title="  Título Sucio  ", content="Contenido")
    assert entry.title == "Título Sucio"
