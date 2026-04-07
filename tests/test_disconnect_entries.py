class TestDisconnectEntries:
    def test_disconnect_existing_relation_returns_true(self, codex, mock_repo):
        # Setup: Crear dos entradas y conectarlas
        e1 = codex.create_entry(title="Origen", content="Contenido 1")
        e2 = codex.create_entry(title="Destino", content="Contenido 2")
        codex.create_relation(e1.id, e2.id, connection_type="link")

        # Ejecución: Desconectar
        result = codex.disconnect_entries(e1.id, e2.id, connection_type="link")

        # Verificación
        assert result is True
        # Verificar que ya no existe en el repositorio
        assert len(mock_repo.get_out_relations(e1.id)) == 0

    def test_disconnect_non_existent_relation_returns_false(self, codex):
        # Intentar desconectar IDs que no tienen relación
        result = codex.disconnect_entries("id_inexistente_1", "id_inexistente_2")

        assert result is False

    def test_disconnect_specific_type_only(self, codex, mock_repo):
        # Setup: Dos relaciones entre los mismos nodos pero de distinto tipo
        e1 = codex.create_entry(title="A", content="...")
        e2 = codex.create_entry(title="B", content="...")

        codex.create_relation(e1.id, e2.id, connection_type="amigo")
        codex.create_relation(e1.id, e2.id, connection_type="bloqueado")

        # Ejecución: Desconectar solo 'bloqueado'
        result = codex.disconnect_entries(e1.id, e2.id, connection_type="bloqueado")

        # Verificación
        assert result is True
        relations = mock_repo.get_out_relations(e1.id)
        assert len(relations) == 1
        assert relations[0].connection_type == "amigo"

    def test_disconnect_without_type_removes_all_matching_directions(
        self, codex, mock_repo
    ):
        # Setup: Varias relaciones de distintos tipos entre los mismos IDs
        e1 = codex.create_entry(title="A", content="...")
        e2 = codex.create_entry(title="B", content="...")

        codex.create_relation(e1.id, e2.id, connection_type="tipo1")
        codex.create_relation(e1.id, e2.id, connection_type="tipo2")

        # Ejecución: Desconectar sin especificar tipo
        # Nota: Según la implementación de InMemoryLexicon en tu conftest,
        # si connection_type es None, filtra todas las que coincidan en IDs.
        result = codex.disconnect_entries(e1.id, e2.id)

        assert result is True
        assert len(mock_repo.get_out_relations(e1.id)) == 0

    def test_disconnect_is_directional(self, codex, mock_repo):
        # Setup: Relación de A -> B
        e1 = codex.create_entry(title="A", content="...")
        e2 = codex.create_entry(title="B", content="...")
        codex.create_relation(e1.id, e2.id, connection_type="rel")

        # Ejecución: Intentar borrar de B -> A (sentido opuesto)
        result = codex.disconnect_entries(e2.id, e1.id)

        # Verificación: No debería borrar nada porque el origen/destino no coinciden
        assert result is False
        assert len(mock_repo.get_out_relations(e1.id)) == 1
