def test_validate_string_capitalize(codex):
    """
    Prueba que el helper _validate_string_capitalize transforme correctamente
    el texto: Primera letra en mayúscula y el resto en minúscula.
    """

    # Caso 1: Todo en minúsculas
    assert codex._validate_string_capitalize("python") == "Python"

    # Caso 2: Todo en mayúsculas
    assert codex._validate_string_capitalize("PYTHON") == "Python"

    # Caso 3: Mezcla de mayúsculas y minúsculas (CamelCase o desordenado)
    assert codex._validate_string_capitalize("pYtHoN") == "Python"

    # Caso 4: Texto con espacios (la capitalización solo afecta a la primera letra del string)
    # Nota: Este método no hace strip(), solo capitaliza.
    assert codex._validate_string_capitalize("hola mundo") == "Hola mundo"


def test_category_use_case_with_capitalize(codex):
    """
    Un test de integración pequeño que verifica cómo la política de
    capitalización afecta a la creación de una entrada a través de Codex.
    """
    # Por defecto, CodexPolicy tiene category_capitalize = True
    entry = codex.create_entry(
        title="Test Entry", content="Contenido", category="proyectos personales"
    )

    # El resultado debería estar capitalizado gracias a que _rules_category
    # utiliza el helper internamente.
    assert entry.category == "Proyectos personales"
