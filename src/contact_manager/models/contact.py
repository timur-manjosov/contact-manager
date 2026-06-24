"""The :class:`Contact` domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Contact:
    """A single address-book entry.

    Instances are immutable value objects: ``name`` is the contact's unique
    identity, and two contacts compare equal when all of their fields match.
    The model performs *no* validation — that is the
    :class:`~contact_manager.services.ContactService`'s responsibility — so a
    ``Contact`` is a pure data container that is cheap to create and to
    serialise.

    The model carries a small, deliberately *personal* set of fields (the
    sort of thing you keep about a person, not a sales lead). Everything but
    ``name`` is optional and has a sensible empty default, which keeps
    construction cheap and lets older, sparser records load unchanged.

    Attributes:
        name: The contact's display name and unique key.
        number: A phone number, stored exactly as the user formatted it.
        email: An e-mail address (``""`` when not provided).
        nickname: An informal name ("what I actually call them").
        company: The organisation the contact is associated with.
        title: A job title or role; pairs with ``company`` as a headline.
        location: A free-form place, e.g. ``"Arlington, VA"``.
        website: A personal or company URL, stored as typed.
        birthday: ``"MM-DD"`` or ``"YYYY-MM-DD"`` (``""`` when unknown).
        tags: Lower-cased, de-duplicated labels for grouping and filtering.
        notes: Free-form text about the contact.
        favorite: Whether the contact is pinned as a favourite.
        updated_at: ISO-8601 timestamp of the last mutation, stamped by the
            service (``""`` for records that predate the field).
    """

    name: str
    number: str = ""
    email: str = ""
    nickname: str = ""
    company: str = ""
    title: str = ""
    location: str = ""
    website: str = ""
    birthday: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""
    favorite: bool = False
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation of this contact.

        ``tags`` becomes a list (JSON has no tuple) and ``favorite`` a bool;
        every other field is a string.
        """
        return {
            "name": self.name,
            "number": self.number,
            "email": self.email,
            "nickname": self.nickname,
            "company": self.company,
            "title": self.title,
            "location": self.location,
            "website": self.website,
            "birthday": self.birthday,
            "tags": list(self.tags),
            "notes": self.notes,
            "favorite": self.favorite,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Contact:
        """Build a :class:`Contact` from a stored mapping.

        Missing optional keys fall back to empty defaults so that older or
        partially-written records — including the original
        ``{name, number, email}`` shape — still load instead of crashing the
        app. ``tags`` is coerced back into a tuple of strings.
        """
        return cls(
            name=str(data["name"]),
            number=str(data.get("number", "")),
            email=str(data.get("email", "")),
            nickname=str(data.get("nickname", "")),
            company=str(data.get("company", "")),
            title=str(data.get("title", "")),
            location=str(data.get("location", "")),
            website=str(data.get("website", "")),
            birthday=str(data.get("birthday", "")),
            tags=tuple(str(tag) for tag in data.get("tags", ())),
            notes=str(data.get("notes", "")),
            favorite=bool(data.get("favorite", False)),
            updated_at=str(data.get("updated_at", "")),
        )
