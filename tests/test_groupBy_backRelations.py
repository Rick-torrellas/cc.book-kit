def test_group_by_back_relations_success(codex, mock_repo):
    """
    Debe retornar todas las entradas que apuntan HACIA la entrada objetivo.
    Si A -> B y C -> B, entonces groupBy_backRelations(B) debe retornar [A, C].
    """
    # 1. Preparar: Crear las entradas
    entry_a = codex.create_entry(title="Nota A", content="Soy el origen 1")
    entry_c = codex.create_entry(title="Nota C", content="Soy el origen 2")
    entry_target = codex.create_entry(
        title="Nota Destino", content="Soy el punto focal"
    )

    # Nota D no estará relacionada
    codex.create_entry(title="Nota D", content="No tengo nada que ver")

    # 2. Crear relaciones manuales en el mock_repo para simular la persistencia
    # (Codex.create_relation usa repository.save_relation internamente)
    codex.create_relation(from_id=entry_a.id, to_id=entry_target.id)
    codex.create_relation(from_id=entry_c.id, to_id=entry_target.id)

    # 3. Configurar el Mock:
    # El InMemoryLexicon en tu conftest.py tiene get_in_relations como 'return []'.
    # Debemos sobreescribir ese comportamiento para este test o ajustar el mock.
    # Como tu InMemoryLexicon ya guarda las relaciones en self.relations,
    # actualizamos el método para que funcione de verdad:
    def mock_get_in_relations(entry_id):
        return [r for r in mock_repo.relations if r.to_id == entry_id]

    mock_repo.get_in_relations = mock_get_in_relations

    # 4. Ejecutar: Obtener quienes apuntan a 'entry_target'
    back_relations = codex.groupBy_backRelations(entry_target.id)

    # 5. Validar
    assert len(back_relations) == 2
    titles = [e.title for e in back_relations]
    assert "Nota A" in titles
    assert "Nota C" in titles
    assert "Nota D" not in titles


def test_group_by_back_relations_empty(codex, mock_repo):
    """Debe retornar una lista vacía si nadie apunta a la entrada."""
    entry = codex.create_entry(title="Nota Solitaria", content="Nadie me quiere")

    # Aseguramos que el mock retorne lista vacía
    mock_repo.get_in_relations = lambda id: []

    results = codex.groupBy_backRelations(entry.id)

    assert results == []
    assert isinstance(results, list)
