"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from contact_manager.repositories import JsonContactRepository
from contact_manager.services import ContactService


@pytest.fixture
def data_file(tmp_path: Path) -> Path:
    """Path to a throwaway contacts file inside a temporary directory."""
    return tmp_path / "contacts.json"


@pytest.fixture
def repository(data_file: Path) -> JsonContactRepository:
    """A JSON repository backed by the temporary :func:`data_file`."""
    return JsonContactRepository(data_file)


@pytest.fixture
def service(repository: JsonContactRepository) -> ContactService:
    """A contact service wired to the temporary repository."""
    return ContactService(repository)
