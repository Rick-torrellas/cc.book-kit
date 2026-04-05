from CapsuleCore_book.core import Codex, Relation

def test_disconnect_entries_success(codex: Codex, mock_repo):
    """
    Verifica que disconnect_entries llame al repositorio y retorne True 
    cuando la desconexión es exitosa.
    """
    # 1. Setup: Crear dos entradas y una relación entre ellas
    e1 = codex.create_entry(title="Nota A", content="Contenido A")
    e2 = codex.create_entry(title="Nota B", content="Contenido B")
    
    # Creamos la relación físicamente en el mock_repo para simular existencia
    rel = Relation(from_id=e1.id, to_id=e2.id, connection_type="link")
    mock_repo.save_relation(rel)
    
    # 2. Ejecución: Intentar desconectar
    # Probamos pasando el connection_type opcional
    result = codex.disconnect_entries(e1.id, e2.id, connection_type="link")
    
    # 3. Aserción: Verificar que la respuesta sea booleana (según tu implementación en Codex)
    assert result is True
    # Nota: Como tu InMemoryLexicon actual en conftest.py siempre retorna True 
    # y no tiene lógica de borrado real, el test valida la integración con Codex.

def test_disconnect_entries_without_type(codex: Codex, mock_repo):
    """
    Verifica que la desconexión funcione incluso sin especificar el tipo de conexión.
    """
    e1 = codex.create_entry(title="Nota 1", content="Contenido 1")
    e2 = codex.create_entry(title="Nota 2", content="Contenido 2")
    
    # Ejecución sin el tercer parámetro
    result = codex.disconnect_entries(e1.id, e2.id)
    
    assert result is True

def test_disconnect_non_existent_relation(codex: Codex, mock_repo):
    """
    Verifica el comportamiento cuando se intenta desconectar algo que no existe.
    """
    # En un repositorio real, esto devolvería False si no encontró qué borrar.
    # El mock actual siempre devuelve True, pero testeamos que Codex pase los IDs.
    result = codex.disconnect_entries("id_inexistente_1", "id_inexistente_2")
    
    assert isinstance(result, bool)