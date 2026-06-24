"""The repository interface that every storage backend implements.

Defining persistence as an abstract interface (the Repository pattern) lets
the service layer depend on an abstraction rather than on JSON files. Swapping
in a SQLite or remote backend later means writing a new subclass — no other
code needs to change. This is the Dependency Inversion Principle in practice.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from contact_manager.models import Contact


class ContactRepository(ABC):
    """Abstract store for :class:`~contact_manager.models.Contact` records."""

    @abstractmethod
    def load(self) -> list[Contact]:
        """Return every stored contact.

        Implementations must treat missing storage as an empty collection
        rather than an error, so a first run starts cleanly.
        """

    @abstractmethod
    def save(self, contacts: list[Contact]) -> None:
        """Persist the given contacts, replacing any previous content."""
