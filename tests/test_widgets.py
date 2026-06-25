"""Unit tests for the pure presentation helpers in :mod:`ui.widgets`.

These functions hold no Textual state, so they are tested directly without the
pilot harness.
"""

from __future__ import annotations

from datetime import date, timedelta

from contact_manager.models import Contact
from contact_manager.ui.widgets import (
    avatar_for,
    birthday_phrase,
    contact_matches,
    days_until_birthday,
    upcoming_birthdays,
)


def _with_birthday(value: str) -> Contact:
    return Contact("Someone", "12345", birthday=value)


def test_days_until_birthday_today_is_zero() -> None:
    today = date(2026, 6, 25)
    contact = _with_birthday(today.strftime("%m-%d"))
    assert days_until_birthday(contact, today=today) == 0


def test_days_until_birthday_tomorrow_is_one() -> None:
    today = date(2026, 6, 25)
    tomorrow = today + timedelta(days=1)
    contact = _with_birthday(tomorrow.strftime("%m-%d"))
    assert days_until_birthday(contact, today=today) == 1


def test_days_until_birthday_wraps_to_next_year() -> None:
    today = date(2026, 6, 25)
    yesterday = today - timedelta(days=1)
    contact = _with_birthday(yesterday.strftime("%m-%d"))
    assert days_until_birthday(contact, today=today) == 364


def test_days_until_birthday_handles_full_date() -> None:
    today = date(2026, 6, 25)
    contact = _with_birthday("1906-06-27")
    assert days_until_birthday(contact, today=today) == 2


def test_days_until_birthday_leap_day_folds_onto_march_first() -> None:
    today = date(2026, 2, 28)  # 2026 is not a leap year
    contact = _with_birthday("02-29")
    assert days_until_birthday(contact, today=today) == 1


def test_days_until_birthday_none_when_missing_or_unparseable() -> None:
    assert days_until_birthday(_with_birthday("")) is None
    assert days_until_birthday(_with_birthday("not-a-date")) is None


def test_birthday_phrase_wording() -> None:
    assert birthday_phrase(0) == "today"
    assert birthday_phrase(1) == "tomorrow"
    assert birthday_phrase(5) == "in 5 days"


def test_upcoming_birthdays_filters_and_sorts() -> None:
    today = date(2026, 6, 25)
    soon = Contact("Soon", "1", birthday=(today + timedelta(days=2)).strftime("%m-%d"))
    sooner = Contact("Sooner", "2", birthday=today.strftime("%m-%d"))
    far = Contact("Far", "3", birthday=(today + timedelta(days=40)).strftime("%m-%d"))
    none = Contact("None", "4")

    result = upcoming_birthdays([soon, sooner, far, none], today=today)
    assert result == [("Sooner", 0), ("Soon", 2)]


def test_contact_matches_across_fields() -> None:
    contact = Contact("Ada", "12345", company="Analytical Engine", tags=("legends",))
    assert contact_matches(contact, "analytical")
    assert contact_matches(contact, "LEGENDS")
    assert not contact_matches(contact, "navy")


def test_avatar_for_is_stable_and_uses_initials() -> None:
    initials, colour = avatar_for("Grace Hopper")
    assert initials == "GH"
    assert avatar_for("Grace Hopper") == (initials, colour)
