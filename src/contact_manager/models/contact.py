"""The :class:`Contact` domain model."""

from __future__ import annotations

from dataclasses import dataclass
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

    Attributes:
        name: The contact's display name and unique key.
        number: A phone number, stored exactly as the user formatted it.
        email: An optional e-mail address (``""`` when not provided).
    """

    name: str
    number: str
    email: str = ""

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serialisable representation of this contact."""
        return {"name": self.name, "number": self.number, "email": self.email}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Contact:
        """Build a :class:`Contact` from a stored mapping.

        Missing optional keys fall back to empty strings so that older or
        partially-written records still load instead of crashing the app.
        """
        return cls(
            name=str(data["name"]),
            number=str(data.get("number", "")),
            email=str(data.get("email", "")),
        )
