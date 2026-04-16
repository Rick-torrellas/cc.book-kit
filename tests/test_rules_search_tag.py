from cc_book_kit.core import Codex, CodexPolicy


def test_rules_search_tag_empty_input(codex):
    """Debe retornar un string vacío si la entrada es None o vacía."""
    assert codex._rules_search_tag(None) == ""
    assert codex._rules_search_tag("") == ""


def test_rules_search_tag_strip_policy(mock_repo):
    """Debe limpiar espacios en blanco si la política title_strip está activa."""
    # Política con strip activado (por defecto)
    policy = CodexPolicy(tags_strip=True)
    codex = Codex(repository=mock_repo, policy=policy)

    assert codex._rules_search_tag("  python  ") == "python"

    # Política con strip desactivado
    policy_no_strip = CodexPolicy(tags_strip=False)
    codex_no_strip = Codex(repository=mock_repo, policy=policy_no_strip)

    assert codex_no_strip._rules_search_tag("  python  ") == "  python  "


def test_rules_search_tag_lowercase_policy(mock_repo):
    """Debe normalizar a minúsculas si la política tags_lowercase está activa."""
    # Política con lowercase activado (por defecto)
    policy = CodexPolicy(tags_lowercase=True)
    codex = Codex(repository=mock_repo, policy=policy)

    assert codex._rules_search_tag("PyThOn") == "python"

    # Política con lowercase desactivado
    policy_no_lower = CodexPolicy(tags_lowercase=False)
    codex_no_lower = Codex(repository=mock_repo, policy=policy_no_lower)

    assert codex_no_lower._rules_search_tag("PyThOn") == "PyThOn"


def test_rules_search_tag_combined_normalization(mock_repo):
    """Debe aplicar múltiples transformaciones simultáneamente."""
    policy = CodexPolicy(tags_strip=True, tags_lowercase=True)
    codex = Codex(repository=mock_repo, policy=policy)

    # Limpia espacios Y pasa a minúsculas
    assert codex._rules_search_tag("  DATA Science  ") == "data science"


def test_rules_search_tag_consistency_with_storage(codex):
    """
    Verifica que la normalización de búsqueda coincida con
    la normalización de creación de entradas.
    """
    raw_tag = "  MachineLearning  "

    # Creamos una entrada (esto usa _rules_tags internamente)
    entry = codex.create_entry(title="AI", content="...", tags=[raw_tag])
    stored_tag = entry.tags[0]

    # Normalizamos el mismo tag para búsqueda
    search_tag = codex._rules_search_tag(raw_tag)

    # El tag guardado y el tag de búsqueda deben ser idénticos
    assert stored_tag == search_tag
    assert search_tag == "machinelearning"
