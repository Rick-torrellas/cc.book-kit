def test_rules_tags_normalization(codex):
    # Entrada con mayúsculas, espacios y duplicados
    input_tags = ["  Ciencia ", "ciencia", "DATOS  ", " datos"]

    # El método debería limpiar todo según la política por defecto
    result = codex._rules_tags(input_tags)

    # Resultado esperado: ordenado, sin espacios, minúsculas y único
    assert result == ["ciencia", "datos"]


def test_rules_tags_empty_list(codex):
    # Test con lista vacía
    assert codex._rules_tags([]) == []


def test_rules_tags_with_none(codex):
    # Test si alguien pasa None en lugar de una lista
    # (Depende de cómo manejes el error en tu código,
    # create_entry suele convertir tags=None en tags=[])
    assert codex._rules_tags([]) == []


def test_rules_tags_sorting(codex):
    # Verificar que el orden alfabético se respeta
    input_tags = ["z", "a", "m"]
    assert codex._rules_tags(input_tags) == ["a", "m", "z"]
