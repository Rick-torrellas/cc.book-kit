import pytest


def test_validate_title_uniqueness_success(codex):
    """Debe permitir un título que no existe en el repositorio."""
    # No debe lanzar ninguna excepción
    codex._validate_title_uniqueness("Título Único")


def test_validate_title_uniqueness_duplicate_raises_error(codex):
    """Debe lanzar ValueError si el título ya está ocupado por otra entrada."""
    codex.create_entry(title="Existente", content="Contenido original")

    with pytest.raises(
        ValueError, match="Ya existe una entrada con el título: 'Existente'"
    ):
        codex._validate_title_uniqueness("Existente")


def test_validate_title_uniqueness_same_entry_id(codex):
    """
    Debe permitir el mismo título si el ID proporcionado coincide con el de la
    entrada existente (caso típico de edición sin cambiar el título).
    """
    entry = codex.create_entry(title="Mi Titulo", content="...")

    # Si pasamos el ID de la entrada actual, no debería dar error aunque el título coincida
    codex._validate_title_uniqueness("Mi Titulo", current_entry_id=entry.id)


def test_validate_title_uniqueness_different_id_conflict(codex):
    """Debe lanzar error si el título coincide con OTRA entrada (ID diferente)."""
    codex.create_entry(title="Ocupado", content="...")
    otra_entry = codex.create_entry(title="Libre", content="...")

    # Intentamos validar el título 'Ocupado' para la entrada que se llama 'Libre'
    with pytest.raises(ValueError, match="Ya existe una entrada con el título"):
        codex._validate_title_uniqueness("Ocupado", current_entry_id=otra_entry.id)


def test_validate_title_uniqueness_case_sensitive(codex, mock_repo):
    """
    Verifica si la unicidad es sensible a mayúsculas/minúsculas
    (depende de la implementación del Lexicon).
    """
    codex.create_entry(title="PROYECTO", content="...")

    # Si el repo/policy no normaliza, esto debería pasar.
    # Si el repo es case-insensitive, esto debería fallar.
    # Basado en tu InMemoryLexicon, es case-sensitive:
    codex._validate_title_uniqueness("proyecto")
