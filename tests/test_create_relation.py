import pytest
from CapsuleCore_book.core import Relation


def test_create_relation_success(codex, mock_repo):
    # Setup: Necesitamos dos entradas existentes para relacionarlas
    e1 = codex.create_entry(title="Entrada Origen", content="Contenido 1")
    e2 = codex.create_entry(title="Entrada Destino", content="Contenido 2")

    # Action
    relation = codex.create_relation(
        from_id=e1.id,
        to_id=e2.id,
        connection_type="Relacion-Prueba",
        metadata={"importancia": "alta"},
    )

    # Assert
    assert isinstance(relation, Relation)
    assert relation.from_id == e1.id
    assert relation.to_id == e2.id
    assert (
        relation.connection_type == "relacion-prueba"
    )  # Verifica normalización (strip/lower)
    assert relation.metadata["importancia"] == "alta"

    # Verificar persistencia en el repositorio
    assert mock_repo.check_relation(relation) is True


def test_create_relation_missing_origin_raises_error(codex):
    # Setup: Solo creamos el destino
    e2 = codex.create_entry(title="Destino", content="...")

    # Action & Assert
    with pytest.raises(
        ValueError, match="No se puede crear la relación. Faltan: Origen"
    ):
        codex.create_relation(from_id="id-inexistente", to_id=e2.id)


def test_create_relation_missing_target_raises_error(codex):
    # Setup: Solo creamos el origen
    e1 = codex.create_entry(title="Origen", content="...")

    # Action & Assert
    with pytest.raises(
        ValueError, match="No se puede crear la relación. Faltan: Destino"
    ):
        codex.create_relation(from_id=e1.id, to_id="id-inexistente")


def test_create_relation_duplicate_raises_error(codex):
    # Setup: Crear relación inicial
    e1 = codex.create_entry(title="A", content="...")
    e2 = codex.create_entry(title="B", content="...")
    codex.create_relation(from_id=e1.id, to_id=e2.id, connection_type="link")

    # Action & Assert: Intentar crear la misma relación exacta
    with pytest.raises(ValueError, match="Ya existe una relación"):
        codex.create_relation(from_id=e1.id, to_id=e2.id, connection_type="link")


def test_create_relation_default_type(codex):
    # Setup
    e1 = codex.create_entry(title="A", content="...")
    e2 = codex.create_entry(title="B", content="...")

    # Action: No pasamos connection_type
    relation = codex.create_relation(from_id=e1.id, to_id=e2.id)

    # Assert
    assert relation.connection_type == "relation"


def test_create_relation_normalization(codex):
    # Setup
    e1 = codex.create_entry(title="A", content="...")
    e2 = codex.create_entry(title="B", content="...")

    # Action: Enviamos tipo con espacios y mayúsculas
    relation = codex.create_relation(
        from_id=e1.id, to_id=e2.id, connection_type="  FRIEND  "
    )

    # Assert
    assert relation.connection_type == "friend"
