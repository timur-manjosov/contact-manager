"""Validation and normalisation helpers for contact fields.

Each function takes raw, user-supplied text and returns a cleaned value,
raising :class:`~contact_manager.exceptions.ValidationError` when the input
cannot be accepted. Keeping these as small pure functions makes them trivial
to unit-test and lets every layer share a single definition of "valid".
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime

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


def normalize_text(value: str) -> str:
    """Return free-form optional text with surrounding whitespace trimmed.

    Used for fields that have no shape to enforce — nickname, company, title,
    location, notes. Empty is always acceptable.
    """
    return value.strip()


def normalize_website(value: str) -> str:
    """Return a trimmed website, rejecting only obvious junk.

    A URL is optional and stored exactly as typed (no scheme is added or
    stripped) so the user's preferred form survives; we merely reject values
    containing whitespace, which can never be a single valid URL.
    """
    website = value.strip()
    if not website:
        return ""
    if any(char.isspace() for char in website):
        raise ValidationError(f"'{value}' is not a valid website.")
    return website


def normalize_birthday(value: str) -> str:
    """Return a validated birthday, or ``""`` when not provided.

    Two shapes are accepted: ``"MM-DD"`` for a recurring day with no year, and
    full ISO ``"YYYY-MM-DD"`` when the year is known. The value is parsed to
    guarantee a real calendar date (so ``"02-30"`` is rejected) and returned
    unchanged on success.
    """
    birthday = value.strip()
    if not birthday:
        return ""
    # Year-less dates are validated against a leap year (2000) so that 02-29 is
    # accepted; pinning the year also avoids strptime's ambiguous-default warning.
    candidates = (birthday, f"2000-{birthday}") if "-" in birthday else ()
    for candidate in candidates:
        try:
            datetime.strptime(candidate, "%Y-%m-%d")
        except ValueError:
            continue
        return birthday
    raise ValidationError(
        f"'{value}' is not a valid birthday (use MM-DD or YYYY-MM-DD)."
    )


def normalize_tags(value: str | Iterable[str]) -> tuple[str, ...]:
    """Return clean, de-duplicated tags as a tuple.

    Accepts either a comma-separated string (``"work, Family, work"``) or any
    iterable of strings. Tags are trimmed, lower-cased and de-duplicated while
    preserving first-seen order; blanks are dropped. Tags never fail
    validation — anything unusable is simply discarded.
    """
    raw = value.split(",") if isinstance(value, str) else value

    seen: set[str] = set()
    tags: list[str] = []
    for item in raw:
        tag = item.strip().lower()
        if tag and tag not in seen:
            seen.add(tag)
            tags.append(tag)
    return tuple(tags)
