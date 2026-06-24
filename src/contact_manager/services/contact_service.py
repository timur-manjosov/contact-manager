"""The :class:`ContactService` — the application's business logic.

This layer sits between the UI and the repository. It owns the in-memory
collection of contacts, enforces the rules (names are unique, fields are
valid) and is the *only* place that turns raw user input into validated
:class:`~contact_manager.models.Contact` objects. The UI talks exclusively to
this service and never touches the repository or the validators directly,
which keeps presentation and business logic cleanly separated.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from datetime import datetime, timezone

from contact_manager.exceptions import (
    ContactNotFoundError,
    DuplicateContactError,
)
from contact_manager.models import Contact
from contact_manager.repositories.base import ContactRepository
from contact_manager.utils.validators import (
    normalize_birthday,
    normalize_email,
    normalize_name,
    normalize_phone,
    normalize_tags,
    normalize_text,
    normalize_website,
)


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string (second precision)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class ContactService:
    """Manage contacts on top of a :class:`ContactRepository`.

    Contacts are cached in an insertion-ordered dict keyed by name, giving
    O(1) duplicate checks, lookups and deletions while preserving a stable
    display order. The cache is loaded once from the repository on
    construction; every mutation updates the cache and immediately persists,
    so the on-disk file and memory never drift apart.
    """

    def __init__(self, repository: ContactRepository) -> None:
        """Args:
        repository: Backend used to load the initial contacts and to
            persist every subsequent change.
        """
        self._repository = repository
        self._contacts: dict[str, Contact] = {
            contact.name: contact for contact in repository.load()
        }

    def list_contacts(self) -> list[Contact]:
        """Return all contacts in insertion order."""
        return list(self._contacts.values())

    def __len__(self) -> int:
        """Return how many contacts are stored."""
        return len(self._contacts)

    def __contains__(self, name: object) -> bool:
        """Return whether a contact with ``name`` exists."""
        return name in self._contacts

    def get(self, name: str) -> Contact:
        """Return the contact called ``name``.

        Raises:
            ContactNotFoundError: If no such contact exists.
        """
        try:
            return self._contacts[name]
        except KeyError:
            raise ContactNotFoundError(f"No contact named '{name}'.") from None

    def add(
        self,
        name: str,
        number: str,
        email: str = "",
        *,
        nickname: str = "",
        company: str = "",
        title: str = "",
        location: str = "",
        website: str = "",
        birthday: str = "",
        tags: str | Iterable[str] = (),
        notes: str = "",
        favorite: bool = False,
    ) -> Contact:
        """Validate, store and persist a new contact.

        Only ``name`` and ``number`` are required; every other field is
        optional. The new contact is stamped with the current time in
        ``updated_at``.

        Args:
            name: The contact's unique name (required).
            number: The contact's phone number (required).
            email: An optional e-mail address.
            nickname: An informal name.
            company: The contact's organisation.
            title: A job title or role.
            location: A free-form place.
            website: A personal or company URL.
            birthday: ``"MM-DD"`` or ``"YYYY-MM-DD"``.
            tags: Comma-separated string or iterable of labels.
            notes: Free-form text.
            favorite: Whether to pin the contact as a favourite.

        Returns:
            The newly created :class:`Contact`.

        Raises:
            ValidationError: If any field fails validation.
            DuplicateContactError: If ``name`` is already in use.
        """
        contact = Contact(
            name=normalize_name(name),
            number=normalize_phone(number),
            email=normalize_email(email),
            nickname=normalize_text(nickname),
            company=normalize_text(company),
            title=normalize_text(title),
            location=normalize_text(location),
            website=normalize_website(website),
            birthday=normalize_birthday(birthday),
            tags=normalize_tags(tags),
            notes=normalize_text(notes),
            favorite=favorite,
            updated_at=_now_iso(),
        )
        if contact.name in self._contacts:
            raise DuplicateContactError(
                f"A contact named '{contact.name}' already exists."
            )

        self._contacts[contact.name] = contact
        self._persist()
        return contact

    #: Validators keyed by the field they clean, used when updating in place.
    _FIELD_NORMALIZERS = {
        "number": normalize_phone,
        "email": normalize_email,
        "nickname": normalize_text,
        "company": normalize_text,
        "title": normalize_text,
        "location": normalize_text,
        "website": normalize_website,
        "birthday": normalize_birthday,
        "tags": normalize_tags,
        "notes": normalize_text,
    }

    def update(self, name: str, /, **changes: object) -> Contact:
        """Validate and apply field changes to an existing contact.

        ``name`` is the primary key and cannot be changed here — rename by
        deleting and re-adding. ``favorite`` is taken as-is; every other field
        is run through the same validator :meth:`add` uses, so the rules stay
        in one place. The contact's ``updated_at`` is refreshed on success.

        Args:
            name: The contact to modify.
            **changes: Field/value pairs to overwrite.

        Returns:
            The updated :class:`Contact`.

        Raises:
            ContactNotFoundError: If no such contact exists.
            ValidationError: If any changed field fails validation.
            ValueError: If an unknown or non-editable field is supplied.
        """
        current = self.get(name)

        cleaned: dict[str, object] = {}
        for field_name, value in changes.items():
            if field_name == "favorite":
                cleaned[field_name] = bool(value)
            elif field_name in self._FIELD_NORMALIZERS:
                cleaned[field_name] = self._FIELD_NORMALIZERS[field_name](value)  # type: ignore[operator]
            else:
                raise ValueError(f"Cannot update field '{field_name}'.")

        updated = replace(current, updated_at=_now_iso(), **cleaned)
        self._contacts[name] = updated
        self._persist()
        return updated

    def toggle_favorite(self, name: str) -> Contact:
        """Flip a contact's favourite flag and persist the change.

        Returns:
            The updated :class:`Contact`.

        Raises:
            ContactNotFoundError: If no such contact exists.
        """
        return self.update(name, favorite=not self.get(name).favorite)

    def delete(self, name: str) -> Contact:
        """Remove the contact called ``name`` and persist the change.

        Returns:
            The contact that was removed.

        Raises:
            ContactNotFoundError: If no such contact exists.
        """
        try:
            contact = self._contacts.pop(name)
        except KeyError:
            raise ContactNotFoundError(f"No contact named '{name}'.") from None

        self._persist()
        return contact

    def _persist(self) -> None:
        """Write the current set of contacts back to the repository."""
        self._repository.save(list(self._contacts.values()))
