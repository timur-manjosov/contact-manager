"""Modal screens for the contact manager.

:class:`AddContactScreen` is the form for creating a contact. It talks to the
:class:`~contact_manager.services.ContactService` (the public business-logic
seam) to validate and persist — never to the validators or repository directly
— and reports validation failures inline while keeping the user's input.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from contact_manager.exceptions import ContactManagerError
from contact_manager.models import Contact
from contact_manager.services import ContactService

# (input id, label, placeholder). The first two ids map to the positional
# ``add(name, number, ...)`` arguments; the rest are keyword arguments.
_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("name", "NAME *", "Grace Hopper"),
    ("nickname", "NICKNAME", "Amazing Grace"),
    ("number", "PHONE *", "+1 202 555 0143"),
    ("email", "EMAIL", "grace@navy.mil"),
    ("company", "COMPANY", "US Navy"),
    ("title", "TITLE", "Rear Admiral"),
    ("location", "LOCATION", "Arlington, VA"),
    ("website", "WEBSITE", "nyx.cs.yale.edu"),
    ("birthday", "BIRTHDAY", "MM-DD or YYYY-MM-DD"),
    ("tags", "TAGS", "work, legends"),
    ("notes", "NOTES", "Coined “debugging”."),
)


class AddContactScreen(ModalScreen[Contact | None]):
    """A centred dialog that creates a new contact.

    Dismisses with the created :class:`Contact` on success, or ``None`` when
    cancelled.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, service: ContactService) -> None:
        super().__init__()
        self._service = service

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="dialog"):
            yield Label("New contact", id="dialog-title")
            for field_id, label, placeholder in _FIELDS:
                with Horizontal(classes="field-row"):
                    yield Label(label, classes="field-label")
                    yield Input(placeholder=placeholder, id=field_id)
            yield Label("", id="form-error")
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="cancel")
                yield Button("Save", id="save", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#name", Input).focus()

    # -- Events ----------------------------------------------------------

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self._save()
        else:
            self.dismiss(None)

    def on_input_submitted(self) -> None:
        self._save()

    def action_cancel(self) -> None:
        self.dismiss(None)

    # -- Helpers ---------------------------------------------------------

    def _value(self, field_id: str) -> str:
        return self.query_one(f"#{field_id}", Input).value

    def _save(self) -> None:
        """Create the contact, or surface a validation error inline."""
        try:
            contact = self._service.add(
                self._value("name"),
                self._value("number"),
                self._value("email"),
                nickname=self._value("nickname"),
                company=self._value("company"),
                title=self._value("title"),
                location=self._value("location"),
                website=self._value("website"),
                birthday=self._value("birthday"),
                tags=self._value("tags"),
                notes=self._value("notes"),
            )
        except ContactManagerError as error:
            self.query_one("#form-error", Label).update(str(error))
            return
        self.dismiss(contact)
