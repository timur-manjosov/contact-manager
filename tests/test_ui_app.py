"""Integration tests for the Textual UI via Textual's pilot harness.

These exercise the wiring between the UI and the service without asserting on
pixels: they drive real key/click input and check the resulting application
state, which is exactly the seam most likely to regress.
"""

from __future__ import annotations

from textual.widgets import DataTable, Input

from contact_manager.repositories import JsonContactRepository
from contact_manager.services import ContactService
from contact_manager.ui import ContactApp


def make_app(repository: JsonContactRepository) -> ContactApp:
    return ContactApp(ContactService(repository))


async def test_adding_a_contact_creates_a_row(
    repository: JsonContactRepository,
) -> None:
    app = make_app(repository)
    async with app.run_test() as pilot:
        app.query_one("#name", Input).value = "Ada"
        app.query_one("#number", Input).value = "12345"
        app.query_one("#email", Input).value = "ada@example.com"
        await pilot.click("#add")
        await pilot.pause()

        table = app.query_one(DataTable)
        assert table.row_count == 1
        assert "Ada" in app._service  # type: ignore[attr-defined]


async def test_invalid_contact_is_rejected(
    repository: JsonContactRepository,
) -> None:
    app = make_app(repository)
    async with app.run_test() as pilot:
        app.query_one("#number", Input).value = "12345"  # name left blank
        await pilot.click("#add")
        await pilot.pause()

        assert app.query_one(DataTable).row_count == 0


async def test_delete_binding_removes_selected_contact(
    repository: JsonContactRepository,
) -> None:
    ContactService(repository).add("Ada", "12345")
    app = make_app(repository)
    async with app.run_test() as pilot:
        assert app.query_one(DataTable).row_count == 1
        await pilot.press("d")
        await pilot.pause()
        assert app.query_one(DataTable).row_count == 0
