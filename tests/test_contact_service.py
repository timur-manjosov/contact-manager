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


def test_add_accepts_and_normalises_rich_fields(
    service: ContactService, repository: JsonContactRepository
) -> None:
    contact = service.add(
        "Grace Hopper",
        "+1 202 555 0143",
        company="US Navy",
        title="Rear Admiral",
        birthday="12-09",
        tags="Work, legends, work",
        favorite=True,
    )

    assert contact.company == "US Navy"
    assert contact.tags == ("work", "legends")
    assert contact.favorite is True
    assert contact.updated_at  # stamped on creation
    # Rich fields survive a round trip through the repository.
    assert ContactService(repository).get("Grace Hopper") == contact


def test_add_rejects_invalid_rich_field(service: ContactService) -> None:
    with pytest.raises(ValidationError):
        service.add("Ada", "12345", birthday="02-30")


def test_update_changes_fields_and_restamps(service: ContactService) -> None:
    original = service.add("Ada", "12345")
    updated = service.update("Ada", company="Analytical Engine Co", tags="math, work")

    assert updated.company == "Analytical Engine Co"
    assert updated.tags == ("math", "work")
    assert updated.name == "Ada"  # key is unchanged
    assert updated.updated_at >= original.updated_at


def test_update_persists(
    service: ContactService, repository: JsonContactRepository
) -> None:
    service.add("Ada", "12345")
    service.update("Ada", email="ada@example.com")
    assert ContactService(repository).get("Ada").email == "ada@example.com"


def test_update_validates(service: ContactService) -> None:
    service.add("Ada", "12345")
    with pytest.raises(ValidationError):
        service.update("Ada", email="not-an-email")


def test_update_rejects_unknown_field(service: ContactService) -> None:
    service.add("Ada", "12345")
    with pytest.raises(ValueError):
        service.update("Ada", name="Grace")


def test_update_unknown_contact_raises(service: ContactService) -> None:
    with pytest.raises(ContactNotFoundError):
        service.update("Nobody", company="Acme")


def test_toggle_favorite_flips_and_persists(
    service: ContactService, repository: JsonContactRepository
) -> None:
    service.add("Ada", "12345")
    assert service.toggle_favorite("Ada").favorite is True
    assert service.toggle_favorite("Ada").favorite is False
    assert ContactService(repository).get("Ada").favorite is False


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
