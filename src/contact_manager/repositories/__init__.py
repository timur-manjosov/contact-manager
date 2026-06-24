"""Persistence layer — storage behind a swappable interface."""

from __future__ import annotations

from contact_manager.repositories.base import ContactRepository
from contact_manager.repositories.json_repository import JsonContactRepository

__all__ = ["ContactRepository", "JsonContactRepository"]
