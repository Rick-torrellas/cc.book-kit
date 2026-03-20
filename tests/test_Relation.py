import pytest
from dataclasses import FrozenInstanceError
from CapsuleCore_book.core.Relation import (
    Relation,
)  # Reemplaza 'tu_archivo' con el nombre real


def test_relation_creation():
    """Verifica que los atributos se asignen correctamente al instanciar."""
    rel = Relation(from_id="A", to_id="B", connection_type="referencia")

    assert rel.from_id == "A"
    assert rel.to_id == "B"
    assert rel.connection_type == "referencia"


def test_relation_immutability():
    """Verifica que no se puedan modificar los atributos (frozen=True)."""
    rel = Relation(from_id="A", to_id="B", connection_type="depende de")

    with pytest.raises(FrozenInstanceError):
        rel.from_id = "C"


def test_relation_equality():
    """Verifica que dos instancias con los mismos datos sean iguales."""
    rel1 = Relation("1", "2", "tipo")
    rel2 = Relation("1", "2", "tipo")

    assert rel1 == rel2


def test_relation_hashable():
    """Verifica que, al ser frozen, se puede usar en sets o como llaves de dict."""
    rel = Relation("A", "B", "vínculo")
    mi_set = {rel}

    assert rel in mi_set
