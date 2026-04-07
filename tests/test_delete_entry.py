import pytest


def test_delete_entry_success(codex, mock_repo):
    """Debe eliminar una entrada existente y retornar True."""
    # 1. Preparar: Crear una entrada
    entry = codex.create_entry(title="Entrada a eliminar", content="Contenido efímero")
    entry_id = entry.id

    # 2. Ejecutar: Eliminar
    result = codex.delete_entry(entry_id)

    # 3. Verificar
    assert result is True
    assert mock_repo.get_by_id(entry_id) is None


def test_delete_entry_non_existent(codex):
    """Debe retornar False si se intenta eliminar un ID que no existe."""
    result = codex.delete_entry("id_inexistente")
    assert result is False


def test_delete_entry_invalid_id_type(codex):
    """Debe lanzar ValueError si el ID no es un string o es nulo."""
    with pytest.raises(ValueError, match="Se requiere un ID de entrada válido"):
        codex.delete_entry(None)

    with pytest.raises(ValueError, match="Se requiere un ID de entrada válido"):
        codex.delete_entry(123)  # Tipo incorrecto


def test_delete_entry_removes_relations(codex, mock_repo):
    """
    Debe asegurar que al eliminar una entrada, el Lexicon también
    limpie las relaciones asociadas (evitar huérfanos).
    """
    # 1. Preparar: Crear dos entradas y relacionarlas
    e1 = codex.create_entry(title="Origen", content="...")
    e2 = codex.create_entry(title="Destino", content="...")
    codex.create_relation(from_id=e1.id, to_id=e2.id)

    # Verificar que la relación existe en el mock_repo
    assert len(mock_repo.relations) == 1

    # 2. Ejecutar: Eliminar una de las entradas
    codex.delete_entry(e1.id)

    # 3. Verificar: La relación donde participaba e1 debe haber desaparecido
    # (Siguiendo el contrato definido en Lexicon.delete)
    assert len(mock_repo.relations) == 0
    assert mock_repo.get_by_id(e1.id) is None
    assert mock_repo.get_by_id(e2.id) is not None  # La otra entrada sigue viva
