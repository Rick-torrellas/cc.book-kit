import pytest
from CapsuleCore_book.core import Entry, Codex
from CapsuleCore_book.capsule import Lexicon


def test_validate_title_uniqueness_new_duplicate(codex: Codex, mock_repo: Lexicon):
    # 1. Preparamos el terreno: guardamos una entrada existente
    existing_entry = Entry(title="Receta de Pan", content="...")
    mock_repo.save(existing_entry)
    
    # 2. Intentamos validar el mismo título para una entrada NUEVA (current_entry_id = None)
    with pytest.raises(ValueError, match="Ya existe una entrada con el título: 'Receta de Pan'"):
        codex._validate_title_uniqueness("Receta de Pan")

def test_validate_title_uniqueness_same_id_success(codex: Codex, mock_repo: Lexicon):
    # 1. Guardamos una entrada
    existing_entry = Entry(title="Diario", content="...")
    mock_repo.save(existing_entry)
    
    # 2. Validamos el mismo título pero pasando su ID (simulando una edición)
    # NO debe lanzar excepción
    codex._validate_title_uniqueness("Diario", current_entry_id=existing_entry.id)

def test_validate_title_uniqueness_different_id_fails(codex: Codex, mock_repo: Lexicon):
    # 1. Tenemos la entrada A
    entry_a = Entry(title="Secreto", content="...", id="id-123")
    mock_repo.save(entry_a)
    
    # 2. Intentamos ponerle el título "Secreto" a la entrada B (id-999)
    with pytest.raises(ValueError, match="Ya existe"):
        codex._validate_title_uniqueness("Secreto", current_entry_id="id-999")