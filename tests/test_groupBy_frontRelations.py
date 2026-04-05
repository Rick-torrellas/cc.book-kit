from CapsuleCore_book.core import Codex

def test_group_by_front_relations_success(codex: Codex, mock_repo):
    """
    Debe retornar todas las entradas a las que apunta la entrada origen.
    Si A -> B y A -> C, entonces groupBy_frontRelations(A) debe retornar [B, C].
    """
    # 1. Preparar: Crear las entradas
    entry_origin = codex.create_entry(title="Nota Raíz", content="Yo apunto a otras")
    entry_b = codex.create_entry(title="Nota B", content="Soy un destino")
    entry_c = codex.create_entry(title="Nota C", content="Soy otro destino")
    
    # Nota D no está conectada
    codex.create_entry(title="Nota D", content="Nadie me conoce")

    # 2. Crear relaciones salientes desde 'entry_origin'
    codex.create_relation(from_id=entry_origin.id, to_id=entry_b.id)
    codex.create_relation(from_id=entry_origin.id, to_id=entry_c.id)

    # 3. Configurar el Mock:
    # Debemos asegurar que get_out_relations filtre correctamente por 'from_id'
    def mock_get_out_relations(entry_id):
        return [r for r in mock_repo.relations if r.from_id == entry_id]
    
    mock_repo.get_out_relations = mock_get_out_relations

    # 4. Ejecutar: Obtener hacia dónde apunta 'entry_origin'
    front_relations = codex.groupBy_frontRelations(entry_origin.id)

    # 5. Validar
    assert len(front_relations) == 2
    titles = [e.title for e in front_relations]
    assert "Nota B" in titles
    assert "Nota C" in titles
    assert "Nota Raíz" not in titles # No debe incluirse a sí misma a menos que sea autorreferencia

def test_group_by_front_relations_empty(codex: Codex, mock_repo):
    """Debe retornar una lista vacía si la nota no apunta a ninguna otra."""
    entry = codex.create_entry(title="Nota Final", content="No apunto a nadie")
    
    # Forzamos que el repositorio no encuentre relaciones de salida
    mock_repo.get_out_relations = lambda id: []
    
    results = codex.groupBy_frontRelations(entry.id)
    
    assert results == []
    assert isinstance(results, list)