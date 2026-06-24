"""Reusable, dependency-free helper functions."""

from __future__ import annotations

from contact_manager.utils.validators import (
    normalize_email,
    normalize_name,
    normalize_phone,
)

__all__ = ["normalize_email", "normalize_name", "normalize_phone"]
