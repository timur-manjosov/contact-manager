"""Unit tests for the :class:`Contact` model."""

from __future__ import annotations

from contact_manager.models import Contact


def test_round_trips_through_dict() -> None:
    contact = Contact("Ada", "12345", "ada@example.com")
    assert Contact.from_dict(contact.to_dict()) == contact


def test_from_dict_defaults_missing_optionals() -> None:
    contact = Contact.from_dict({"name": "Ada"})
    assert contact == Contact("Ada", "", "")


def test_round_trips_all_fields() -> None:
    contact = Contact(
        name="Grace Hopper",
        number="+1 202 555 0143",
        email="grace@navy.mil",
        nickname="Amazing Grace",
        company="US Navy",
        title="Rear Admiral",
        location="Arlington, VA",
        website="nyx.cs.yale.edu",
        birthday="12-09",
        tags=("work", "legends"),
        notes="Coined 'debugging'.",
        favorite=True,
        updated_at="2026-06-24T00:00:00+00:00",
    )
    assert Contact.from_dict(contact.to_dict()) == contact


def test_from_dict_coerces_tags_to_tuple() -> None:
    contact = Contact.from_dict({"name": "Ada", "tags": ["work", "math"]})
    assert contact.tags == ("work", "math")


def test_legacy_record_still_loads() -> None:
    contact = Contact.from_dict(
        {"name": "Ada", "number": "12345", "email": "ada@example.com"}
    )
    assert contact.name == "Ada"
    assert contact.tags == ()
    assert contact.favorite is False
    assert contact.updated_at == ""


def test_is_immutable() -> None:
    contact = Contact("Ada", "12345")
    try:
        contact.name = "Grace"  # type: ignore[misc]
    except AttributeError:
        return
    raise AssertionError("Contact should be frozen")
