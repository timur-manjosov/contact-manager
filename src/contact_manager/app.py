"""Composition root — wires the layers together and starts the app.

This is the single place where concrete implementations are chosen and
injected. Keeping construction here (rather than scattered through the code)
means the rest of the package depends only on abstractions, and swapping a
backend or front-end is a one-line change in :func:`build_app`.
"""

from __future__ import annotations

from contact_manager.config import Settings, get_settings
from contact_manager.repositories import JsonContactRepository
from contact_manager.services import ContactService
from contact_manager.ui import ContactApp


def build_app(settings: Settings | None = None) -> ContactApp:
    """Construct a fully wired :class:`ContactApp`.

    Args:
        settings: Resolved configuration; defaults to reading the environment.

    Returns:
        A ready-to-run application with its service and repository attached.
    """
    settings = settings or get_settings()
    repository = JsonContactRepository(settings.data_file)
    service = ContactService(repository)
    return ContactApp(service)


def main() -> None:
    """Entry point for the ``contacts`` console script."""
    build_app().run()


if __name__ == "__main__":
    main()
