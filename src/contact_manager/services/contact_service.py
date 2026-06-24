"""The :class:`ContactService` — the application's business logic.

This layer sits between the UI and the repository. It owns the in-memory
collection of contacts, enforces the rules (names are unique, fields are
valid) and is the *only* place that turns raw user input into validated
:class:`~contact_manager.models.Contact` objects. The UI talks exclusively to
this service and never touches the repository or the validators directly,
which keeps presentation and business logic cleanly separated.
"""

from __future__ import annotations

from contact_manager.exceptions import (
    ContactNotFoundError,
    DuplicateContactError,
)
from contact_manager.models import Contact
from contact_manager.repositories.base import ContactRepository
from contact_manager.utils.validators import (
    normalize_email,
    normalize_name,
    normalize_phone,
)


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

    def add(self, name: str, number: str, email: str = "") -> Contact:
        """Validate, store and persist a new contact.

        Args:
            name: The contact's unique name (required).
            number: The contact's phone number (required).
            email: An optional e-mail address.

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
        )
        if contact.name in self._contacts:
            raise DuplicateContactError(
                f"A contact named '{contact.name}' already exists."
            )

        self._contacts[contact.name] = contact
        self._persist()
        return contact

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
