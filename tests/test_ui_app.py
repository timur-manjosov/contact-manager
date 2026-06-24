"""Integration tests for the Textual UI via Textual's pilot harness.

These exercise the wiring between the UI and the service without asserting on
pixels: they drive real key/click input and check the resulting application
state, which is exactly the seam most likely to regress.
"""

from __future__ import annotations

from textual.widgets import Input, ListView

from contact_manager.repositories import JsonContactRepository
from contact_manager.services import ContactService
from contact_manager.ui import ContactApp
from contact_manager.ui.screens import AddContactScreen
from contact_manager.ui.widgets import ContactCard, ContactListItem


def make_app(repository: JsonContactRepository) -> ContactApp:
    return ContactApp(ContactService(repository))


async def test_adding_a_contact_creates_a_list_item(
    repository: JsonContactRepository,
) -> None:
    app = make_app(repository)
    async with app.run_test() as pilot:
        await pilot.press("a")  # open the add dialog
        await pilot.pause()
        app.screen.query_one("#name", Input).value = "Ada"
        app.screen.query_one("#number", Input).value = "12345"
        app.screen.query_one("#email", Input).value = "ada@example.com"
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()

        assert len(app.query(ContactListItem)) == 1
        assert "Ada" in app._service  # type: ignore[attr-defined]


async def test_invalid_contact_keeps_dialog_open(
    repository: JsonContactRepository,
) -> None:
    app = make_app(repository)
    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.pause()
        app.screen.query_one("#number", Input).value = "12345"  # name left blank
        await pilot.press("enter")
        await pilot.pause()

        # Nothing was added and the dialog stays open on the error.
        assert len(app._service) == 0  # type: ignore[attr-defined]
        assert isinstance(app.screen, AddContactScreen)


async def test_delete_binding_removes_highlighted_contact(
    repository: JsonContactRepository,
) -> None:
    ContactService(repository).add("Ada", "12345")
    app = make_app(repository)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert len(app.query(ContactListItem)) == 1
        await pilot.press("d")
        await pilot.pause()
        await pilot.pause()
        assert len(app.query(ContactListItem)) == 0
        assert "Ada" not in app._service  # type: ignore[attr-defined]


async def test_favorite_binding_toggles_and_persists(
    repository: JsonContactRepository,
) -> None:
    ContactService(repository).add("Ada", "12345")
    app = make_app(repository)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("f")
        await pilot.pause()
        await pilot.pause()
        assert app._service.get("Ada").favorite is True  # type: ignore[attr-defined]


async def test_highlighting_a_contact_updates_the_card(
    repository: JsonContactRepository,
) -> None:
    service = ContactService(repository)
    service.add("Ada", "12345")
    service.add("Grace", "67890")
    app = make_app(repository)
    async with app.run_test() as pilot:
        await pilot.pause()
        card = app.query_one(ContactCard)
        assert card.contact is not None
        first = card.contact.name

        app.query_one(ListView).index = 1
        await pilot.pause()
        assert card.contact is not None
        assert card.contact.name != first
