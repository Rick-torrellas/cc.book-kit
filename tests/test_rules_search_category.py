from CapsuleCore_book.core import CodexPolicy


def test_rules_search_category_basic(codex):
    """Verifica que limpie espacios y aplique capitalización por defecto."""
    # La política por defecto tiene category_strip=True y category_capitalize=True
    result = codex._rules_search_category("  proyectos  ")
    assert result == "Proyectos"


def test_rules_search_category_empty_returns_empty_string(codex):
    """
    Verifica que si la categoría es None o vacía, retorna un string vacío
    sin lanzar errores (a diferencia de _rules_category).
    """
    assert codex._rules_search_category(None) == ""
    assert codex._rules_search_category("") == ""


def test_rules_search_category_max_length(codex, mock_repo):
    """Verifica que respete el truncado definido en la política."""
    # Creamos un Codex con una política de longitud muy corta (5 caracteres)
    short_policy = CodexPolicy(category_max_length=5, category_capitalize=False)
    from CapsuleCore_book.core import Codex

    custom_codex = Codex(repository=mock_repo, policy=short_policy)

    result = custom_codex._rules_search_category("categoria_larga")
    assert result == "categ"
    assert len(result) == 5


def test_rules_search_category_no_capitalize(codex, mock_repo):
    """Verifica el comportamiento cuando la capitalización está desactivada."""
    no_cap_policy = CodexPolicy(category_capitalize=False)
    from CapsuleCore_book.core import Codex

    custom_codex = Codex(repository=mock_repo, policy=no_cap_policy)

    result = custom_codex._rules_search_category("mantenimiento")
    assert result == "mantenimiento"


def test_rules_search_category_no_strip(codex, mock_repo):
    """Verifica el comportamiento cuando el strip está desactivado."""
    no_strip_policy = CodexPolicy(category_strip=False, category_capitalize=False)
    from CapsuleCore_book.core import Codex

    custom_codex = Codex(repository=mock_repo, policy=no_strip_policy)

    result = custom_codex._rules_search_category("  espacios  ")
    assert result == "  espacios  "
