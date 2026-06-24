"""Tests for the JSON repository implementation."""

from __future__ import annotations

from pathlib import Path

import pytest

from contact_manager.exceptions import RepositoryError
from contact_manager.models import Contact
from contact_manager.repositories import JsonContactRepository


def test_load_missing_file_returns_empty(repository: JsonContactRepository) -> None:
    assert repository.load() == []


def test_save_then_load_round_trips(repository: JsonContactRepository) -> None:
    contacts = [Contact("Ada", "12345", "ada@example.com"), Contact("Grace", "67890")]
    repository.save(contacts)
    assert repository.load() == contacts


def test_save_is_atomic_and_leaves_no_temp_files(
    repository: JsonContactRepository, data_file: Path
) -> None:
    repository.save([Contact("Ada", "12345")])
    leftovers = list(data_file.parent.glob("*.tmp"))
    assert leftovers == []


def test_empty_file_loads_as_empty(
    repository: JsonContactRepository, data_file: Path
) -> None:
    data_file.write_text("")
    assert repository.load() == []


def test_corrupt_file_raises(
    repository: JsonContactRepository, data_file: Path
) -> None:
    data_file.write_text("{not json")
    with pytest.raises(RepositoryError):
        repository.load()


def test_save_creates_missing_parent_directories(tmp_path: Path) -> None:
    nested = tmp_path / "deeply" / "nested" / "contacts.json"
    repository = JsonContactRepository(nested)
    repository.save([Contact("Ada", "12345")])
    assert nested.exists()
