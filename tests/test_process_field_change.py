import pytest

from CapsuleCore_book.core import Codex
from CapsuleCore_book.capsule import Lexicon

def test_process_field_change_title_success(codex: Codex, mock_repo: Lexicon):
    # Setup: Crear una entrada original
    entry = codex.create_entry(title="Titulo Original", content="Contenido")
    
    # Test: Cambiar a un título nuevo (debe ser procesado por _rules_title)
    new_title = "  TITULO NUEVO  "
    # El resultado esperado debe estar limpio (strip) según la política por defecto
    result = codex._process_field_change('title', new_title, entry)
    
    assert result == "TITULO NUEVO"

def test_process_field_change_title_no_change(codex: Codex):
    entry = codex.create_entry(title="Igual", content="Contenido")
    
    # Test: Intentar cambiar al mismo título
    result = codex._process_field_change('title', "Igual", entry)
    
    # Debe retornar None porque no hay cambios reales
    assert result is None

def test_process_field_change_tags_logic(codex: Codex):
    entry = codex.create_entry(title="Tags Test", content="...", tags=["python", "ai"])
    
    # Test 1: Cambiar el orden o duplicar (la política debería normalizar)
    # Tags originales: ['ai', 'python'] (por el sort de la política)
    result = codex._process_field_change('tags', ["python", "python", "AI "], entry)
    
    # Si el resultado normalizado es igual al actual, debe ser None
    # 'python', 'python', 'AI ' -> ['ai', 'python']
    assert result is None

    # Test 2: Cambio real en tags
    result_new = codex._process_field_change('tags', ["rust", "python"], entry)
    assert "rust" in result_new
    assert isinstance(result_new, list)

@pytest.mark.skip(reason="TODO: Implementar lógica de inmutabilidad para metadata y testear que se crea una nueva referencia")
def test_process_field_change_metadata_immutability(codex: Codex):
    original_meta = {"key": "value"}
    entry = codex.create_entry(title="Meta Test", content="...", metadata=original_meta)
    
    new_meta = {"key": "new_value", "extra": 1}
    result = codex._process_field_change('metadata', new_meta, entry)
    
    # Verificar que se creó una nueva referencia (tu "filosofía de recipiente vacío")
    assert result == new_meta
    assert result is not new_meta  # No deben ser el mismo objeto en memoria

def test_process_field_change_category(codex: Codex):
    entry = codex.create_entry(title="Cat Test", content="...", category="General")
    
    # Test: La política por defecto hace Capitalize y Strip
    result = codex._process_field_change('category', "  proyectos  ", entry)
    
    assert result == "Proyectos"

def test_process_field_change_ignore_unknown_or_immutable(codex: Codex):
    entry = codex.create_entry(title="Immutable Test", content="...")
    
    # Aunque edit_entry filtra esto, _process_field_change debe manejar 
    # la lógica de "no hay cambios" si el campo no es especial
    result = codex._process_field_change('content', "...", entry)
    assert result is None
    
    # Si cambia el contenido
    result_content = codex._process_field_change('content', "Nuevo contenido", entry)
    assert result_content == "Nuevo contenido"

def test_process_field_change_title_uniqueness_conflict(codex, mock_repo):
    # Setup: Dos entradas
    codex.create_entry(title="Ocupado", content="...")
    entry_to_edit = codex.create_entry(title="Original", content="...")
    
    # Test: Intentar cambiar el título a uno que ya existe
    with pytest.raises(ValueError, match="Ya existe una entrada con el título"):
        codex._process_field_change('title', "Ocupado", entry_to_edit)