from CapsuleCore_book.core import Codex


def test_group_by_relations_bidirectional_and_unique(codex: Codex, mock_repo):
    """
    Verifica que groupBy_relations encuentre conexiones en ambos sentidos
    y elimine duplicados si existe más de una relación entre los mismos IDs.
    """
    # 1. Preparar las entradas
    # La entrada central
    root = codex.create_entry(title="Root", content="Nodo central")

    # Entradas conectadas
    e_out = codex.create_entry(title="Hacia afuera", content="Relación de salida")
    e_in = codex.create_entry(title="Hacia adentro", content="Relación de entrada")
    e_both = codex.create_entry(title="Doble", content="Relación en ambos sentidos")

    # 2. Establecer relaciones en el repositorio
    # Relación de salida: Root -> e_out
    codex.create_relation(from_id=root.id, to_id=e_out.id, connection_type="links_to")

    # Relación de entrada: e_in -> Root
    codex.create_relation(from_id=e_in.id, to_id=root.id, connection_type="references")

    # Relación doble (para probar unicidad): Root -> e_both Y e_both -> Root
    codex.create_relation(
        from_id=root.id, to_id=e_both.id, connection_type="collaboration"
    )
    codex.create_relation(
        from_id=e_both.id, to_id=root.id, connection_type="collaboration"
    )

    # 3. Ejecutar la lógica de agrupación
    # IMPORTANTE: El mock_repo en conftest.py debe tener implementados
    # get_in_relations y get_out_relations para que esto funcione.

    # Sobrescribimos brevemente los métodos del mock para este test específico
    # si es que el conftest.py solo tiene "return []"
    mock_repo.get_out_relations = lambda eid: [
        r for r in mock_repo.relations if r.from_id == eid
    ]
    mock_repo.get_in_relations = lambda eid: [
        r for r in mock_repo.relations if r.to_id == eid
    ]

    related_entries = codex.groupBy_relations(root.id)

    # 4. Validaciones
    # Deben haber 3 entradas relacionadas (e_out, e_in, e_both)
    assert len(related_entries) == 3

    # Verificamos que los títulos estén presentes
    titles = [e.title for e in related_entries]
    assert "Hacia afuera" in titles
    assert "Hacia adentro" in titles
    assert "Doble" in titles

    # Verificar que no hay duplicados (el set de IDs debe ser igual a la lista de IDs)
    ids = [e.id for e in related_entries]
    assert len(ids) == len(set(ids)), "Existen IDs duplicados en el resultado"


def test_group_by_relations_empty(codex):
    """Verifica que retorne lista vacía si no hay relaciones."""
    alone = codex.create_entry(title="Solitario", content="Sin amigos")

    results = codex.groupBy_relations(alone.id)

    assert isinstance(results, list)
    assert len(results) == 0
