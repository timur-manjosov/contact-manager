"""Integration tests for the Textual UI via Textual's pilot harness.

These exercise the wiring between the UI and the service without asserting on
pixels: they drive real key/click input and check the resulting application
state, which is exactly the seam most likely to regress.
"""

from __future__ import annotations

from textual.widgets import Button, Input, ListView

from contact_manager.repositories import JsonContactRepository
from contact_manager.services import ContactService
from contact_manager.ui import ContactApp
from contact_manager.ui.screens import (
    AddContactScreen,
    ConfirmScreen,
    EditContactScreen,
)
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


async def test_delete_asks_for_confirmation_before_removing(
    repository: JsonContactRepository,
) -> None:
    ContactService(repository).add("Ada", "12345")
    app = make_app(repository)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert len(app.query(ContactListItem)) == 1

        await pilot.press("d")  # opens the confirm dialog, deletes nothing yet
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        assert "Ada" in app._service  # type: ignore[attr-defined]

        app.screen.query_one("#confirm", Button).press()  # confirm
        await pilot.pause()
        await pilot.pause()
        assert len(app.query(ContactListItem)) == 0
        assert "Ada" not in app._service  # type: ignore[attr-defined]


async def test_cancelling_delete_keeps_the_contact(
    repository: JsonContactRepository,
) -> None:
    ContactService(repository).add("Ada", "12345")
    app = make_app(repository)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("d")
        await pilot.pause()
        await pilot.press("escape")  # dismiss the confirm dialog
        await pilot.pause()
        await pilot.pause()
        assert len(app.query(ContactListItem)) == 1
        assert "Ada" in app._service  # type: ignore[attr-defined]


async def test_undo_restores_a_deleted_contact(
    repository: JsonContactRepository,
) -> None:
    ContactService(repository).add("Ada", "12345", favorite=True)
    app = make_app(repository)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("d")
        await pilot.pause()
        app.screen.query_one("#confirm", Button).press()
        await pilot.pause()
        await pilot.pause()
        assert "Ada" not in app._service  # type: ignore[attr-defined]

        await pilot.press("u")
        await pilot.pause()
        await pilot.pause()
        assert len(app.query(ContactListItem)) == 1
        assert app._service.get("Ada").favorite is True  # type: ignore[attr-defined]


async def test_edit_updates_an_existing_contact(
    repository: JsonContactRepository,
) -> None:
    ContactService(repository).add("Ada", "12345", company="Old Co")
    app = make_app(repository)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("e")  # open the edit dialog
        await pilot.pause()
        assert isinstance(app.screen, EditContactScreen)
        # The name is the key and must be locked.
        assert app.screen.query_one("#name", Input).disabled is True

        app.screen.query_one("#company", Input).value = "New Co"
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()
        assert app._service.get("Ada").company == "New Co"  # type: ignore[attr-defined]
        assert "Ada" in app._service  # type: ignore[attr-defined]


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


async def test_search_filters_the_list(
    repository: JsonContactRepository,
) -> None:
    service = ContactService(repository)
    service.add("Ada Lovelace", "11111", company="Analytical Engine")
    service.add("Grace Hopper", "22222", company="US Navy")
    app = make_app(repository)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert len(app.query(ContactListItem)) == 2

        app.query_one("#search", Input).value = "navy"
        await pilot.pause()
        await pilot.pause()
        items = app.query(ContactListItem)
        assert len(items) == 1
        assert items.first().contact.name == "Grace Hopper"


async def test_clearing_search_restores_the_list(
    repository: JsonContactRepository,
) -> None:
    service = ContactService(repository)
    service.add("Ada", "11111")
    service.add("Grace", "22222")
    app = make_app(repository)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.query_one("#search", Input).value = "zzz"
        await pilot.pause()
        await pilot.pause()
        assert len(app.query(ContactListItem)) == 0

        await pilot.press("escape")
        await pilot.pause()
        await pilot.pause()
        assert len(app.query(ContactListItem)) == 2


async def test_favorites_filter_shows_only_favorites(
    repository: JsonContactRepository,
) -> None:
    service = ContactService(repository)
    service.add("Ada", "11111")
    service.add("Grace", "22222", favorite=True)
    app = make_app(repository)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert len(app.query(ContactListItem)) == 2

        await pilot.press("F")
        await pilot.pause()
        await pilot.pause()
        items = app.query(ContactListItem)
        assert len(items) == 1
        assert items.first().contact.name == "Grace"


async def test_copy_phone_puts_the_number_on_the_clipboard(
    repository: JsonContactRepository,
) -> None:
    ContactService(repository).add("Ada", "12345", "ada@example.com")
    app = make_app(repository)
    copied: list[str] = []
    app.copy_to_clipboard = copied.append  # type: ignore[method-assign]
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()
        assert copied == ["12345"]
        await pilot.press("Y")
        await pilot.pause()
        assert copied == ["12345", "ada@example.com"]


async def test_goto_contact_clears_filters_and_selects(
    repository: JsonContactRepository,
) -> None:
    service = ContactService(repository)
    service.add("Ada", "11111")
    service.add("Grace", "22222")
    app = make_app(repository)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.query_one("#search", Input).value = "ada"  # filter away Grace
        await pilot.pause()
        await pilot.pause()
        assert len(app.query(ContactListItem)) == 1

        app.goto_contact("Grace")
        await pilot.pause()
        await pilot.pause()
        # The filter is cleared and Grace is now highlighted.
        assert len(app.query(ContactListItem)) == 2
        card = app.query_one(ContactCard)
        assert card.contact is not None
        assert card.contact.name == "Grace"


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
