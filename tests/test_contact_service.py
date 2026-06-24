"""Tests for the business-logic layer."""

from __future__ import annotations

import pytest

from contact_manager.exceptions import (
    ContactNotFoundError,
    DuplicateContactError,
    ValidationError,
)
from contact_manager.repositories import JsonContactRepository
from contact_manager.services import ContactService


def test_add_normalises_and_persists(
    service: ContactService, repository: JsonContactRepository
) -> None:
    contact = service.add("  Ada  ", "+44 20 7946 0958", "Ada@Example.com")

    assert contact.name == "Ada"
    assert contact.email == "ada@example.com"
    # A fresh service reading the same file sees the persisted contact.
    assert ContactService(repository).get("Ada") == contact


def test_add_rejects_duplicate_names(service: ContactService) -> None:
    service.add("Ada", "12345")
    with pytest.raises(DuplicateContactError):
        service.add("Ada", "67890")


def test_add_rejects_invalid_input(service: ContactService) -> None:
    with pytest.raises(ValidationError):
        service.add("", "12345")


def test_delete_removes_and_returns_contact(service: ContactService) -> None:
    service.add("Ada", "12345")
    removed = service.delete("Ada")
    assert removed.name == "Ada"
    assert "Ada" not in service


def test_delete_unknown_raises(service: ContactService) -> None:
    with pytest.raises(ContactNotFoundError):
        service.delete("Nobody")


def test_get_unknown_raises(service: ContactService) -> None:
    with pytest.raises(ContactNotFoundError):
        service.get("Nobody")


def test_list_preserves_insertion_order(service: ContactService) -> None:
    service.add("Ada", "11111")
    service.add("Grace", "22222")
    service.add("Edsger", "33333")
    assert [c.name for c in service.list_contacts()] == ["Ada", "Grace", "Edsger"]
