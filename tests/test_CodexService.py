import pytest
from unittest.mock import MagicMock
from dataclasses import dataclass, field
from typing import List, Dict

from CapsuleCore_book.capsule.CodexService import CodexService


# --- Mocks de las entidades (basado en tu código) ---
@dataclass
class Entry:
    title: str
    content: str
    id: str = "123"
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def update_content(self, new_content):
        self.content = new_content


@dataclass
class Relation:
    from_id: str
    to_id: str
    connection_type: str


# --- Tests para CodexService ---


class TestCodexService:
    @pytest.fixture
    def mock_repo(self):
        """Fixture para crear un repositorio simulado."""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_repo):
        """Fixture para instanciar el servicio con el mock."""
        return CodexService(mock_repo)

    ## Tests de Ingesta y Creación
    ## --------------------------

    def test_create_page_success(self, service, mock_repo):
        # 1. Configuración
        mock_repo.get_by_id.return_value = None

        # 2. Ejecución (Usando AI y ai para forzar el duplicado)
        service.create_page("Título Válido", "Contenido", [" AI ", "ai", "Python"])

        # 3. Verificación
        assert mock_repo.save.called
        saved_entry = mock_repo.save.call_args[0][0]

        # Ahora sí coinciden los datos:
        assert len(saved_entry.tags) == 2
        assert "ai" in saved_entry.tags  # <-- Cambiado de "ia" a "ai"
        assert "python" in saved_entry.tags

    def test_ingest_duplicate_error(self, service, mock_repo):
        # Configuración: el repo ya tiene ese ID
        mock_repo.get_by_id.return_value = Entry("Existente", "...", id="1")

        entry = Entry("Nuevo", "...", id="1")
        with pytest.raises(ValueError, match="Esta página ya existe"):
            service.ingest(entry)

    ## Tests de Edición
    ## ----------------

    def test_edit_page_updates_metadata(self, service, mock_repo):
        # Configuración: existe una entrada previa
        existing_entry = Entry(
            "Orig", "Contenido viejo", id="abc", metadata={"edit_count": 1}
        )
        mock_repo.get_by_id.return_value = existing_entry

        service.edit_page("abc", "Nuevo contenido")

        assert existing_entry.content == "Nuevo contenido"
        assert existing_entry.metadata["edit_count"] == 2
        mock_repo.save.assert_called_with(existing_entry)

    ## Tests de Relaciones
    ## -------------------

    def test_connect_pages_same_id_error(self, service):
        with pytest.raises(ValueError, match="consigo misma"):
            service.connect_pages("A", "A", "link")

    def test_connect_pages_missing_target_error(self, service, mock_repo):
        # Solo existe el origen, no el destino
        mock_repo.get_by_id.side_effect = [Entry("A", ""), None]

        with pytest.raises(ValueError, match="Ambas páginas deben existir"):
            service.connect_pages("id_1", "id_2", "ref")

    ## Tests de Eliminación y Desconexión
    ## ----------------------------------

    def test_delete_page_cleans_relations(self, service, mock_repo):
        mock_repo.get_by_id.return_value = Entry("A", "")

        service.delete_page("A")

        mock_repo.remove_all_relations_to.assert_called_once_with("A")
        mock_repo.delete.assert_called_once_with("A")

    def test_disconnect_non_existent_relation_error(self, service, mock_repo):
        mock_repo.check_relation.return_value = False

        with pytest.raises(ValueError, match="No existe una relación previa"):
            service.disconnect_pages("A", "B")
