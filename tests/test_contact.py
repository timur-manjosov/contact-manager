"""Unit tests for the :class:`Contact` model."""

from __future__ import annotations

from contact_manager.models import Contact


def test_round_trips_through_dict() -> None:
    contact = Contact("Ada", "12345", "ada@example.com")
    assert Contact.from_dict(contact.to_dict()) == contact


def test_from_dict_defaults_missing_optionals() -> None:
    contact = Contact.from_dict({"name": "Ada"})
    assert contact == Contact("Ada", "", "")


def test_is_immutable() -> None:
    contact = Contact("Ada", "12345")
    try:
        contact.name = "Grace"  # type: ignore[misc]
    except AttributeError:
        return
    raise AssertionError("Contact should be frozen")
