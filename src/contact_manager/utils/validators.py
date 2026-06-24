"""Validation and normalisation helpers for contact fields.

Each function takes raw, user-supplied text and returns a cleaned value,
raising :class:`~contact_manager.exceptions.ValidationError` when the input
cannot be accepted. Keeping these as small pure functions makes them trivial
to unit-test and lets every layer share a single definition of "valid".
"""

from __future__ import annotations

import re

from contact_manager.exceptions import ValidationError

# A deliberately permissive e-mail pattern: enough to catch obvious typos
# (missing "@", missing domain) without rejecting the many valid-but-unusual
# addresses that a strict RFC 5322 regex would also reject.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Phone numbers vary wildly by region, so we only require that, once common
# formatting characters are stripped, what remains is a sensible run of digits.
_PHONE_ALLOWED_RE = re.compile(r"^\+?[\d\s().-]+$")
_PHONE_DIGITS_RE = re.compile(r"\d")

MIN_PHONE_DIGITS = 5
MAX_PHONE_DIGITS = 15  # E.164 upper bound.


def normalize_name(value: str) -> str:
    """Return a trimmed contact name or raise if it is empty.

    The name is the primary key for a contact, so it must always be present.
    """
    name = value.strip()
    if not name:
        raise ValidationError("Name is required.")
    return name


def normalize_phone(value: str) -> str:
    """Return a trimmed phone number, validating its rough shape.

    A number is required and must contain a plausible quantity of digits.
    Formatting characters (spaces, dashes, parentheses, a leading ``+``) are
    permitted and preserved so the user's preferred presentation survives.
    """
    number = value.strip()
    if not number:
        raise ValidationError("Phone number is required.")
    if not _PHONE_ALLOWED_RE.match(number):
        raise ValidationError("Phone number contains invalid characters.")

    digit_count = len(_PHONE_DIGITS_RE.findall(number))
    if not MIN_PHONE_DIGITS <= digit_count <= MAX_PHONE_DIGITS:
        raise ValidationError(
            f"Phone number must have between {MIN_PHONE_DIGITS} and "
            f"{MAX_PHONE_DIGITS} digits."
        )
    return number


def normalize_email(value: str) -> str:
    """Return a trimmed, lower-cased e-mail address.

    E-mail is optional; an empty value is accepted and returned as ``""``.
    Anything non-empty must look like an address.
    """
    email = value.strip().lower()
    if not email:
        return ""
    if not _EMAIL_RE.match(email):
        raise ValidationError(f"'{value}' is not a valid e-mail address.")
    return email
