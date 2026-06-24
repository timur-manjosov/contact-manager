"""A JSON-file implementation of :class:`ContactRepository`."""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import suppress
from pathlib import Path

from contact_manager.exceptions import RepositoryError
from contact_manager.models import Contact
from contact_manager.repositories.base import ContactRepository


class JsonContactRepository(ContactRepository):
    """Store contacts as a JSON object keyed by contact name.

    Writes are atomic: data is written to a temporary file in the same
    directory and then renamed over the target, so an interrupted save can
    never leave a half-written, corrupt ``contacts.json`` behind.
    """

    def __init__(self, path: Path) -> None:
        """Args:
        path: Location of the backing JSON file. The file need not exist
            yet; its parent directory is created on first save.
        """
        self._path = path

    @property
    def path(self) -> Path:
        """The file this repository reads from and writes to."""
        return self._path

    def load(self) -> list[Contact]:
        """Return stored contacts, or an empty list if none exist.

        A missing file is a normal first-run condition. A file that exists
        but cannot be parsed is reported as a :class:`RepositoryError` so the
        caller can decide how to react rather than silently losing data.
        """
        try:
            raw = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return []
        except OSError as exc:  # pragma: no cover - filesystem dependent
            raise RepositoryError(f"Could not read {self._path}: {exc}") from exc

        if not raw.strip():
            return []

        try:
            data: dict[str, dict[str, str]] = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RepositoryError(
                f"{self._path} is not valid JSON: {exc}"
            ) from exc

        return [Contact.from_dict(entry) for entry in data.values()]

    def save(self, contacts: list[Contact]) -> None:
        """Atomically persist ``contacts`` to disk, keyed by name."""
        payload = {contact.name: contact.to_dict() for contact in contacts}
        self._path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self._atomic_write(json.dumps(payload, indent=2, ensure_ascii=False))
        except OSError as exc:  # pragma: no cover - filesystem dependent
            raise RepositoryError(f"Could not write {self._path}: {exc}") from exc

    def _atomic_write(self, text: str) -> None:
        """Write ``text`` to :attr:`path` via a temp-file-and-rename swap."""
        directory = self._path.parent
        fd, tmp_name = tempfile.mkstemp(dir=directory, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                tmp.write(text)
                tmp.flush()
                os.fsync(tmp.fileno())
            os.replace(tmp_name, self._path)
        except BaseException:
            # Clean up the partial temp file before re-raising.
            with suppress(OSError):
                os.unlink(tmp_name)
            raise
