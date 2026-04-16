from cc_book_kit.core import Entry


def test_group_by_tags_success(codex):
    """
    Verifica que se recuperen correctamente las entradas que contienen un tag específico.
    """
    # 1. Preparar datos
    codex.create_entry(
        title="Entrada 1", content="Contenido 1", tags=["python", "coding"]
    )
    codex.create_entry(
        title="Entrada 2", content="Contenido 2", tags=["python", "tests"]
    )
    codex.create_entry(title="Entrada 3", content="Contenido 3", tags=["java"])

    # 2. Ejecutar búsqueda
    results = codex.groupBy_tags("python")

    # 3. Validar
    assert len(results) == 2
    titles = [e.title for e in results]
    assert "Entrada 1" in titles
    assert "Entrada 2" in titles
    assert "Entrada 3" not in titles


def test_group_by_tags_normalization(codex):
    """
    Verifica que la búsqueda respete las reglas de normalización de la política
    (strip y lowercase por defecto en CodexPolicy).
    """
    # Guardamos con un formato específico
    codex.create_entry(title="Clean Code", content="...", tags=["Refactoring"])

    # Buscamos con espacios y mayúsculas distintas
    # Según CodexPolicy: tags_lowercase=True, tags_strip=True
    results = codex.groupBy_tags("  REFACTORING  ")

    assert len(results) == 1
    assert results[0].title == "Clean Code"
    assert "refactoring" in results[0].tags


def test_group_by_tags_empty_results(codex):
    """
    Verifica que devuelva una lista vacía si el tag no existe.
    """
    codex.create_entry(title="Solo Python", content="...", tags=["python"])

    results = codex.groupBy_tags("rust")

    assert isinstance(results, list)
    assert len(results) == 0


def test_group_by_tags_invalid_input(codex):
    """
    Verifica el comportamiento con inputs nulos o vacíos según la implementación de Codex.
    """
    # El código de Codex devuelve [] si no hay tag
    assert codex.groupBy_tags(None) == []
    assert codex.groupBy_tags("") == []


def test_group_by_tags_multiple_entries_consistency(codex):
    """
    Asegura que los objetos retornados sean instancias de Entry y mantengan su integridad.
    """
    tag_buscado = "importante"
    codex.create_entry(title="Nota A", content="Nota urgente", tags=[tag_buscado])

    results = codex.groupBy_tags(tag_buscado)

    assert len(results) == 1
    assert isinstance(results[0], Entry)
    assert results[0].content == "Nota urgente"
