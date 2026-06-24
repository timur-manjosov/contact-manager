"""Domain-specific exceptions.

A small, explicit exception hierarchy lets each layer raise meaningful
errors that callers can catch precisely. The UI, for example, can render a
:class:`ValidationError` differently from a :class:`DuplicateContactError`
without inspecting error strings.
"""

from __future__ import annotations


class ContactManagerError(Exception):
    """Base class for every error raised by this package."""


class ValidationError(ContactManagerError):
    """Raised when user-supplied contact data fails validation."""


class ContactNotFoundError(ContactManagerError):
    """Raised when an operation references a contact that does not exist."""


class DuplicateContactError(ContactManagerError):
    """Raised when adding a contact whose name is already taken."""


class RepositoryError(ContactManagerError):
    """Raised when the storage backend cannot read or write data."""
