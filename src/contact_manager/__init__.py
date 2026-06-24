"""Contact Manager — a keyboard-driven terminal address book.

The package is organised into clearly separated layers so that business
logic never depends on the user interface:

* :mod:`contact_manager.models`       — plain, immutable domain records.
* :mod:`contact_manager.repositories` — persistence behind an interface.
* :mod:`contact_manager.services`     — validation and business rules.
* :mod:`contact_manager.ui`           — the Textual front-end.
* :mod:`contact_manager.config`       — runtime configuration.
* :mod:`contact_manager.utils`        — small, dependency-free helpers.
"""

from __future__ import annotations

from importlib import metadata

try:
    __version__ = metadata.version("contact-manager")
except metadata.PackageNotFoundError:  # pragma: no cover - source checkout
    __version__ = "0.0.0+local"

__all__ = ["__version__"]
