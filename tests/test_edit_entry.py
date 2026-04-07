import pytest
from datetime import datetime


def test_edit_entry_success(codex, mock_repo):
    """Verifica que se pueden editar campos permitidos (content, category)."""
    # 1. Crear entrada original
    original = codex.create_entry(
        title="Nota Original", content="Contenido viejo", category="General"
    )
    entry_id = original.id

    # 2. Editar
    updated = codex.edit_entry(
        entry_id, content="Contenido nuevo", category="Proyectos"
    )

    # 3. Aserciones
    assert updated.id == entry_id
    assert updated.content == "Contenido nuevo"
    assert updated.category == "Proyectos"
    assert updated.updated_at > original.updated_at
    # Verificar persistencia en el repo
    assert mock_repo.get_by_id(entry_id).content == "Contenido nuevo"


def test_edit_entry_immutable_fields(codex):
    """Verifica que campos como 'id' o 'created_at' no se pueden modificar."""
    original = codex.create_entry(title="Inmutable", content="Test")
    old_id = original.id
    old_created_at = original.created_at

    # Intentar cambiar campos protegidos
    updated = codex.edit_entry(
        old_id,
        id="nuevo-id-falso",
        created_at=datetime(2000, 1, 1),
        content="Cuerpo cambiado",
    )

    assert updated.id == old_id
    assert updated.created_at == old_created_at
    assert updated.content == "Cuerpo cambiado"


def test_edit_entry_title_uniqueness(codex):
    """Verifica que no se puede cambiar un título a uno que ya existe."""
    codex.create_entry(title="Ocupado", content="Soy el 1")
    target = codex.create_entry(title="Disponible", content="Soy el 2")

    with pytest.raises(
        ValueError, match="Ya existe una entrada con el título: 'Ocupado'"
    ):
        codex.edit_entry(target.id, title="Ocupado")


def test_edit_entry_no_changes(codex):
    """Si los datos son idénticos, no debe actualizar el timestamp (según política del Codex)."""
    original = codex.create_entry(
        title="Estatico", content="Sin cambios", tags=["tag1"]
    )

    # Editamos con los mismos valores
    updated = codex.edit_entry(
        original.id, title="Estatico", content="Sin cambios", tags=["tag1"]
    )

    assert updated.updated_at == original.updated_at
    assert (
        updated is original
    )  # En la implementación actual devuelve el mismo objeto si no hay cambios


def test_edit_entry_tags_normalization(codex):
    """Verifica que las reglas de tags (limpieza, minúsculas) se apliquen en la edición."""
    original = codex.create_entry(title="Tags Test", content="...", tags=["Python"])

    # Enviamos tags desordenados, con espacios y mayúsculas
    updated = codex.edit_entry(original.id, tags=["  JAVA  ", "python", "  java "])

    # El resultado debe estar limpio, en minúsculas, único y ordenado (por CodexPolicy)
    assert updated.tags == ["java", "python"]


def test_edit_entry_not_found(codex):
    """Error al intentar editar un ID inexistente."""
    with pytest.raises(ValueError, match="No se encontró la entrada con ID"):
        codex.edit_entry("id-fantasma", content="hola")


def test_edit_entry_metadata(codex):
    """Verifica la actualización del diccionario de metadatos."""
    original = codex.create_entry(title="Meta", content="...", metadata={"autor": "Yo"})

    new_metadata = {"autor": "Yo", "version": 2.0}
    updated = codex.edit_entry(original.id, metadata=new_metadata)

    assert updated.metadata["version"] == 2.0
    assert "autor" in updated.metadata
