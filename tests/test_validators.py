"""Unit tests for the field validators."""

from __future__ import annotations

import pytest

from contact_manager.exceptions import ValidationError
from contact_manager.utils.validators import (
    normalize_email,
    normalize_name,
    normalize_phone,
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
