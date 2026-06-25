"""Modal screens for the contact manager.

The form screens (:class:`AddContactScreen`, :class:`EditContactScreen`) talk to
the :class:`~contact_manager.services.ContactService` — the public business-logic
seam — to validate and persist, never to the validators or repository directly.
:class:`ConfirmScreen` is a small reusable yes/no dialog used to guard
destructive actions. All of them report problems inline and keep the user's
input intact.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
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

# The editable, keyword-only fields shared by the add and edit forms.
_KEYWORD_FIELDS: tuple[str, ...] = (
    "nickname",
    "company",
    "title",
    "location",
    "website",
    "birthday",
    "tags",
    "notes",
)


class _ContactForm(ModalScreen[Contact | None]):
    """Shared scaffolding for the add and edit dialogs.

    Subclasses provide the dialog title, the initial focus and a :meth:`_save`
    implementation; everything else (layout, cancel, inline errors) is common.
    Dismisses with the resulting :class:`Contact` on success, or ``None`` when
    cancelled.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    _title = "Contact"
    _focus_field = "name"

    def __init__(self, service: ContactService) -> None:
        super().__init__()
        self._service = service

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="dialog"):
            yield Label(self._title, id="dialog-title")
            for field_id, label, placeholder in _FIELDS:
                with Horizontal(classes="field-row"):
                    yield Label(label, classes="field-label")
                    yield Input(placeholder=placeholder, id=field_id)
            yield Label("", id="form-error")
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="cancel")
                yield Button("Save", id="save", variant="primary")

    def on_mount(self) -> None:
        self._populate()
        self.query_one(f"#{self._focus_field}", Input).focus()

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

    def _populate(self) -> None:
        """Fill the form before it is shown. The add form leaves it blank."""

    def _value(self, field_id: str) -> str:
        return self.query_one(f"#{field_id}", Input).value

    def _show_error(self, message: str) -> None:
        self.query_one("#form-error", Label).update(message)

    def _keyword_values(self) -> dict[str, str]:
        """Collect the optional keyword fields shared by both forms."""
        return {field: self._value(field) for field in _KEYWORD_FIELDS}

    def _save(self) -> None:
        raise NotImplementedError


class AddContactScreen(_ContactForm):
    """A centred dialog that creates a new contact."""

    _title = "New contact"
    _focus_field = "name"

    def _save(self) -> None:
        """Create the contact, or surface a validation error inline."""
        try:
            contact = self._service.add(
                self._value("name"),
                self._value("number"),
                self._value("email"),
                **self._keyword_values(),
            )
        except ContactManagerError as error:
            self._show_error(str(error))
            return
        self.dismiss(contact)


class EditContactScreen(_ContactForm):
    """A centred dialog that edits an existing contact.

    The name is the primary key and cannot be changed here, so its field is
    pre-filled and disabled — rename by deleting and re-adding.
    """

    _title = "Edit contact"
    _focus_field = "number"

    def __init__(self, service: ContactService, contact: Contact) -> None:
        super().__init__(service)
        self._contact = contact

    def _populate(self) -> None:
        contact = self._contact
        name = self.query_one("#name", Input)
        name.value = contact.name
        name.disabled = True  # the name is the key; it cannot be edited
        self.query_one("#number", Input).value = contact.number
        self.query_one("#email", Input).value = contact.email
        self.query_one("#nickname", Input).value = contact.nickname
        self.query_one("#company", Input).value = contact.company
        self.query_one("#title", Input).value = contact.title
        self.query_one("#location", Input).value = contact.location
        self.query_one("#website", Input).value = contact.website
        self.query_one("#birthday", Input).value = contact.birthday
        self.query_one("#tags", Input).value = ", ".join(contact.tags)
        self.query_one("#notes", Input).value = contact.notes

    def _save(self) -> None:
        """Apply the changes, or surface a validation error inline."""
        try:
            contact = self._service.update(
                self._contact.name,
                number=self._value("number"),
                email=self._value("email"),
                **self._keyword_values(),
            )
        except ContactManagerError as error:
            self._show_error(str(error))
            return
        self.dismiss(contact)


class ConfirmScreen(ModalScreen[bool]):
    """A small yes/no dialog. Dismisses ``True`` only when confirmed.

    The cancelling button takes focus so an accidental ``Enter`` is harmless.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, message: str, confirm_label: str = "Delete") -> None:
        super().__init__()
        self._message = message
        self._confirm_label = confirm_label

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Label(self._message, id="confirm-message")
            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="cancel")
                yield Button(self._confirm_label, id="confirm", variant="error")

    def on_mount(self) -> None:
        self.query_one("#cancel", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")

    def action_cancel(self) -> None:
        self.dismiss(False)
