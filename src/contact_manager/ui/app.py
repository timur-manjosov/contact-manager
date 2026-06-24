"""The Textual front-end for the contact manager.

This module is intentionally thin. It is responsible only for presentation
and input handling: every rule about what makes a contact valid or unique
lives in :class:`~contact_manager.services.ContactService`. The app catches
the service's domain exceptions and translates them into on-screen
notifications, which keeps UI concerns and business logic firmly separated.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, DataTable, Footer, Header, Input

from contact_manager.exceptions import ContactManagerError
from contact_manager.models import Contact
from contact_manager.services import ContactService

_STYLES = Path(__file__).with_name("styles.tcss")

# Column layout for the contact table: (header, render width).
_COLUMNS: tuple[tuple[str, int], ...] = (
    ("Name", 28),
    ("Number", 22),
    ("Email", 36),
)


class ContactApp(App[None]):
    """A keyboard-driven address book rendered with Textual."""

    CSS_PATH = _STYLES
    TITLE = "Contacts"
    SUB_TITLE = "AddressBook v1"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "delete_contact", "Delete"),
    ]

    def __init__(self, service: ContactService) -> None:
        """Args:
        service: The business-logic layer the UI delegates all
            contact operations to.
        """
        super().__init__()
        self._service = service

    # -- Layout ----------------------------------------------------------

    def compose(self) -> ComposeResult:
        """Build the widget tree."""
        yield Header()
        yield DataTable(cursor_type="row", zebra_stripes=True)
        with Horizontal(id="add-bar"):
            yield Input(placeholder="Name", id="name")
            yield Input(placeholder="Number", id="number")
            yield Input(placeholder="Email", id="email")
            yield Button("Add", id="add", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        """Populate the table and play the fade-in once mounted."""
        table = self._table
        for header, width in _COLUMNS:
            table.add_column(header, width=width)
        for contact in self._service.list_contacts():
            self._append_row(contact)

        table.border_title = "◆ CONTACTS"
        self.query_one("#add-bar").border_title = "◆ NEW ENTRY"

        self.styles.opacity = 0.0
        self.styles.animate("opacity", value=1.0, duration=0.5)

    # -- Actions & events ------------------------------------------------

    def action_delete_contact(self) -> None:
        """Delete the contact under the cursor, if any."""
        table = self._table
        if table.row_count == 0:
            return

        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        name = row_key.value
        try:
            self._service.delete(name)
        except ContactManagerError as error:
            self.notify(str(error), severity="error")
            return

        table.remove_row(row_key)
        self.notify(f"Removed {name}", severity="warning")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle the **Add** button."""
        if event.button.id == "add":
            self._add_contact()

    def on_input_submitted(self) -> None:
        """Allow submitting the form by pressing Enter in any field."""
        self._add_contact()

    # -- Helpers ---------------------------------------------------------

    def _add_contact(self) -> None:
        """Read the input fields and ask the service to add a contact."""
        name = self.query_one("#name", Input).value
        number = self.query_one("#number", Input).value
        email = self.query_one("#email", Input).value

        try:
            contact = self._service.add(name, number, email)
        except ContactManagerError as error:
            self.notify(str(error), severity="error")
            return

        self._append_row(contact)
        self._clear_inputs()
        self.query_one("#name", Input).focus()
        self.notify(f"Added {contact.name}", severity="information")

    def _append_row(self, contact: Contact) -> None:
        """Add a single contact as a row keyed by its name."""
        self._table.add_row(
            contact.name, contact.number, contact.email, key=contact.name
        )

    def _clear_inputs(self) -> None:
        """Reset every input field to empty."""
        for field in self.query(Input):
            field.value = ""

    @property
    def _table(self) -> DataTable:
        """The single contact table; resolved lazily to keep call sites tidy."""
        return self.query_one(DataTable)
