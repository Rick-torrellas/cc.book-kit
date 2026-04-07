def test_truncate_string_shorter_than_limit(codex):
    """Debe devolver el texto íntegro si es más corto que el límite."""
    text = "Hola"
    result = codex._truncate_string(text, 10)
    assert result == "Hola"
    assert len(result) == 4


def test_truncate_string_exactly_limit(codex):
    """Debe devolver el texto íntegro si mide exactamente lo mismo que el límite."""
    text = "12345"
    result = codex._truncate_string(text, 5)
    assert result == "12345"
    assert len(result) == 5


def test_truncate_string_exceeds_limit(codex):
    """Debe cortar el texto a la longitud máxima permitida."""
    text = "Este es un texto muy largo"
    limit = 10
    result = codex._truncate_string(text, limit)

    assert result == "Este es un"
    assert len(result) == limit


def test_truncate_string_with_none_limit(codex):
    """Debe devolver el texto íntegro si el límite es None."""
    text = "Texto sin límites"
    result = codex._truncate_string(text, None)
    assert result == text


def test_truncate_string_empty_string(codex):
    """Debe manejar correctamente un string vacío."""
    result = codex._truncate_string("", 5)
    assert result == ""


def test_truncate_string_zero_limit(codex):
    """Debe devolver un string vacío si el límite es 0."""
    result = codex._truncate_string("Cualquier cosa", 0)
    assert result == ""
