"""Unit tests for the field validators."""

from __future__ import annotations

import pytest

from contact_manager.exceptions import ValidationError
from contact_manager.utils.validators import (
    normalize_birthday,
    normalize_email,
    normalize_name,
    normalize_phone,
    normalize_tags,
    normalize_text,
    normalize_website,
)


class TestNormalizeName:
    def test_trims_surrounding_whitespace(self) -> None:
        assert normalize_name("  Ada  ") == "Ada"

    @pytest.mark.parametrize("value", ["", "   ", "\t\n"])
    def test_rejects_blank_names(self, value: str) -> None:
        with pytest.raises(ValidationError):
            normalize_name(value)


class TestNormalizePhone:
    @pytest.mark.parametrize(
        "value",
        ["+44 20 7946 0958", "(555) 123-4567", "12345"],
    )
    def test_accepts_plausible_numbers(self, value: str) -> None:
        assert normalize_phone(value) == value.strip()

    def test_requires_a_value(self) -> None:
        with pytest.raises(ValidationError):
            normalize_phone("  ")

    def test_rejects_letters(self) -> None:
        with pytest.raises(ValidationError):
            normalize_phone("call-me")

    def test_rejects_too_few_digits(self) -> None:
        with pytest.raises(ValidationError):
            normalize_phone("123")


class TestNormalizeEmail:
    def test_lowercases_and_trims(self) -> None:
        assert normalize_email("  Ada@Example.COM ") == "ada@example.com"

    def test_empty_is_allowed(self) -> None:
        assert normalize_email("") == ""

    @pytest.mark.parametrize("value", ["nope", "a@b", "@example.com", "a@@b.com"])
    def test_rejects_malformed_addresses(self, value: str) -> None:
        with pytest.raises(ValidationError):
            normalize_email(value)


class TestNormalizeText:
    def test_trims(self) -> None:
        assert normalize_text("  Rear Admiral  ") == "Rear Admiral"

    def test_empty_is_allowed(self) -> None:
        assert normalize_text("   ") == ""


class TestNormalizeWebsite:
    def test_trims_and_keeps_form(self) -> None:
        assert normalize_website("  nyx.cs.yale.edu ") == "nyx.cs.yale.edu"

    def test_empty_is_allowed(self) -> None:
        assert normalize_website("") == ""

    def test_rejects_internal_whitespace(self) -> None:
        with pytest.raises(ValidationError):
            normalize_website("not a url")


class TestNormalizeBirthday:
    @pytest.mark.parametrize("value", ["12-09", "1906-12-09", "  02-29 "])
    def test_accepts_valid_dates(self, value: str) -> None:
        assert normalize_birthday(value) == value.strip()

    def test_empty_is_allowed(self) -> None:
        assert normalize_birthday("") == ""

    @pytest.mark.parametrize("value", ["02-30", "13-01", "1906/12/09", "December"])
    def test_rejects_impossible_or_malformed(self, value: str) -> None:
        with pytest.raises(ValidationError):
            normalize_birthday(value)


class TestNormalizeTags:
    def test_splits_lowercases_and_dedupes_a_string(self) -> None:
        assert normalize_tags("Work, family, work ,  ") == ("work", "family")

    def test_accepts_an_iterable(self) -> None:
        assert normalize_tags(["Legends", "legends", "WORK"]) == ("legends", "work")

    def test_empty_yields_empty_tuple(self) -> None:
        assert normalize_tags("") == ()
        assert normalize_tags([]) == ()
