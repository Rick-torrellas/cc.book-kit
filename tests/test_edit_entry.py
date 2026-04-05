import pytest
from datetime import datetime
from CapsuleCore_book.core import Codex

def test_edit_entry_success(codex: Codex, mock_repo):
    # 1. Preparar: Crear una entrada original
    original = codex.create_entry(title="Titulo Original", content="Contenido viejo", category="Tech")
    entry_id = original.id

    # 2. Actuar: Editar contenido y tags
    new_tags = ["python", "testing"]
    updated = codex.edit_entry(entry_id, content="Contenido nuevo", tags=new_tags)

    # 3. Asertar
    assert updated.content == "Contenido nuevo"
    assert "python" in updated.tags
    assert updated.updated_at > original.updated_at
    # Verificar que persiste en el repositorio
    assert mock_repo.get_by_id(entry_id).content == "Contenido nuevo"

def test_edit_entry_immutable_fields(codex: Codex):
    original = codex.create_entry(title="Intocable", content="...")
    
    # Intentar cambiar el ID y la fecha de creación (deben ser ignorados)
    future_date = datetime(2099, 1, 1)
    updated = codex.edit_entry(original.id, id="HACK-ID", created_at=future_date)

    assert updated.id == original.id
    assert updated.created_at == original.created_at

def test_edit_entry_title_uniqueness_validation(codex: Codex):
    # Crear dos entradas
    codex.create_entry(title="Ocupado", content="...")
    target = codex.create_entry(title="Disponible", content="...")

    # Intentar cambiar el título de la segunda al de la primera
    with pytest.raises(ValueError, match="Ya existe una entrada con el título: 'Ocupado'"):
        codex.edit_entry(target.id, title="Ocupado")

def test_edit_entry_same_title_allowed_for_same_id(codex: Codex):
    # Regla: Puedes editar una entrada con su propio título sin disparar error de unicidad
    original = codex.create_entry(title="Mi Titulo", content="...")
    
    # Editamos el contenido pero mandamos el mismo título
    updated = codex.edit_entry(original.id, title="  Mi Titulo  ", content="Cambio")
    
    assert updated.title == "Mi Titulo"
    assert updated.content == "Cambio"

def test_edit_entry_no_changes_logic(codex: Codex):
    original = codex.create_entry(title="Estatico", content="Igual", tags=["a"])
    
    # Mandar los mismos datos (los tags se limpian/ordenan por política)
    updated = codex.edit_entry(original.id, title="Estatico", tags=["a"])

    # Según la norma en Codex.py: "Si no hay cambios reales, retornamos el original"
    # Esto significa que el updated_at NO debe cambiar
    assert updated.updated_at == original.updated_at

def test_edit_entry_not_found(codex: Codex):
    with pytest.raises(ValueError, match="No se encontró la entrada"):
        codex.edit_entry("id-inexistente", content="...")

def test_edit_entry_category_policy(codex: Codex):
    original = codex.create_entry(title="Nota", content="...", category="General")
    
    # La política suele capitalizar categorías ("ciencia" -> "Ciencia")
    updated = codex.edit_entry(original.id, category="ciencia")
    
    assert updated.category == "Ciencia"