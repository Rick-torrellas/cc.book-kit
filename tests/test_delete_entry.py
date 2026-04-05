import pytest
from CapsuleCore_book.core import Codex

def test_delete_entry_success(codex: Codex, mock_repo):
    # 1. Preparación: Crear una entrada
    entry = codex.create_entry(title="Nota a eliminar", content="Contenido efímero")
    entry_id = entry.id
    
    # Verificar que existe en el repositorio antes de borrar
    assert mock_repo.get_by_id(entry_id) is not None

    # 2. Ejecución: Llamar a delete_entry
    result = codex.delete_entry(entry_id)

    # 3. Aserciones
    assert result is True, "Debería retornar True tras un borrado exitoso"
    
    # En un entorno real, el mock_repo debería haber eliminado el objeto.
    # Nota: Tu InMemoryLexicon actual en conftest.py retorna True pero no borra 
    # físicamente del dict self.entries. Para un test riguroso, podrías 
    # actualizar el mock o verificar la llamada.
    
def test_delete_entry_non_existent(codex: Codex):
    # Intentar borrar algo que no existe
    result = codex.delete_entry("id_imaginario")
    
    assert result is False, "Debería retornar False si la entrada no existe"

def test_delete_entry_invalid_id(codex: Codex):
    # Validar que lanza error con entradas inválidas (según la lógica de tu Codex.py)
    with pytest.raises(ValueError, match="Se requiere un ID de entrada válido"):
        codex.delete_entry(None)
    
    with pytest.raises(ValueError, match="Se requiere un ID de entrada válido"):
        codex.delete_entry(123) # No es string

def test_delete_entry_atomic_logic(codex: Codex, mock_repo):
    """
    Verifica que se llame al método delete del repositorio, 
    el cual según el contrato de Lexicon.py, debe ser atómico.
    """
    entry = codex.create_entry(title="Nota con Relaciones", content="...")
    
    # Simulamos que el repositorio borra de verdad para esta prueba
    def mock_delete(eid):
        if eid in mock_repo.entries:
            del mock_repo.entries[eid]
            return True
        return False
    
    mock_repo.delete = mock_delete
    
    codex.delete_entry(entry.id)
    assert mock_repo.get_by_id(entry.id) is None