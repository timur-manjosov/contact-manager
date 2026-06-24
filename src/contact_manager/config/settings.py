"""Application settings, resolved once at start-up.

Centralising configuration keeps environment lookups out of the rest of the
code base and gives tests a single, explicit seam to override.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

#: Environment variable that overrides where contacts are stored.
DATA_FILE_ENV = "CONTACTS_FILE"

#: Default storage location, relative to the current working directory. This
#: preserves the historical behaviour of the app while remaining overridable.
DEFAULT_DATA_FILE = Path("contacts.json")


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable bundle of resolved runtime settings.

    Attributes:
        data_file: Absolute path to the JSON file backing the address book.
    """

    data_file: Path

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        """Build settings from the process environment.

        Args:
            env: Mapping to read from; defaults to :data:`os.environ`. Passing
                an explicit mapping makes the resolution easy to test.
        """
        environ = os.environ if env is None else env
        raw_path = environ.get(DATA_FILE_ENV)
        data_file = Path(raw_path) if raw_path else DEFAULT_DATA_FILE
        return cls(data_file=data_file.expanduser().resolve())


def get_settings() -> Settings:
    """Return settings resolved from the current environment."""
    return Settings.from_env()
