"""The Textual front-end for the contact manager.

This module is intentionally thin. It is responsible only for presentation
and input handling: every rule about what makes a contact valid or unique
lives in :class:`~contact_manager.services.ContactService`. The app catches
the service's domain exceptions and translates them into on-screen
notifications, which keeps UI concerns and business logic firmly separated.

The layout is master/detail: a sidebar :class:`~textual.widgets.ListView` of
contacts on the left and a :class:`ContactCard` profile on the right.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, ListView

from contact_manager.exceptions import ContactManagerError
from contact_manager.models import Contact
from contact_manager.services import ContactService
from contact_manager.ui.commands import ContactCommands
from contact_manager.ui.screens import (
    AddContactScreen,
    ConfirmScreen,
    EditContactScreen,
)
from contact_manager.ui.widgets import (
    ContactCard,
    ContactListItem,
    birthday_phrase,
    contact_matches,
    upcoming_birthdays,
)

_STYLES = Path(__file__).with_name("styles.tcss")


class ContactApp(App[None]):
    """A keyboard-driven address book rendered with Textual."""

    CSS_PATH = _STYLES
    TITLE = "Contacts"

    COMMANDS = App.COMMANDS | {ContactCommands}

    BINDINGS = [
        ("a", "add_contact", "Add"),
        ("e", "edit_contact", "Edit"),
        ("slash", "focus_search", "Search"),
        ("f", "toggle_favorite", "Favorite"),
        ("F", "toggle_favorites_filter", "Favorites"),
        ("d", "delete_contact", "Delete"),
        Binding("u", "undo_delete", "Undo", show=False),
        Binding("y", "copy_phone", "Copy phone", show=False),
        Binding("Y", "copy_email", "Copy email", show=False),
        ("escape", "clear_search", ""),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, service: ContactService) -> None:
        """Args:
        service: The business-logic layer the UI delegates all
            contact operations to.
        """
        super().__init__()
        self._service = service
        self._query = ""
        self._favorites_only = False
        self._undo: Contact | None = None
        self._suppress_search = False

    # -- Layout ----------------------------------------------------------

    def compose(self) -> ComposeResult:
        """Build the widget tree."""
        yield Header()
        with Horizontal(id="body"):
            with Vertical(id="sidebar"):
                yield Input(placeholder="Search contacts…", id="search")
                yield ListView(id="contact-list")
            yield ContactCard(id="card")
        yield Footer()

    def on_mount(self) -> None:
        """Populate the list, focus it, and play a gentle fade-in."""
        self._reload_list()
        self.query_one(ListView).focus()
        self.styles.opacity = 0.0
        self.styles.animate("opacity", value=1.0, duration=0.4)
        self._announce_birthdays()

    # -- Actions ---------------------------------------------------------

    def action_add_contact(self) -> None:
        """Open the new-contact dialog."""
        self.push_screen(AddContactScreen(self._service), self._after_add)

    def action_edit_contact(self) -> None:
        """Open the edit dialog for the highlighted contact, if any."""
        contact = self._highlighted_contact()
        if contact is None:
            return
        self.push_screen(EditContactScreen(self._service, contact), self._after_edit)

    def action_delete_contact(self) -> None:
        """Ask before deleting the highlighted contact."""
        contact = self._highlighted_contact()
        if contact is None:
            return
        self.push_screen(
            ConfirmScreen(f"Delete {contact.name}?"),
            lambda confirmed: self._delete(contact) if confirmed else None,
        )

    def action_undo_delete(self) -> None:
        """Restore the most recently deleted contact, if any."""
        contact = self._undo
        if contact is None:
            return
        try:
            restored = self._service.add(
                contact.name,
                contact.number,
                contact.email,
                nickname=contact.nickname,
                company=contact.company,
                title=contact.title,
                location=contact.location,
                website=contact.website,
                birthday=contact.birthday,
                tags=contact.tags,
                notes=contact.notes,
                favorite=contact.favorite,
            )
        except ContactManagerError as error:
            self.notify(str(error), severity="error")
            return
        self._undo = None
        self._reload_list(select=restored.name)
        self.notify(f"Restored {restored.name}")

    def action_toggle_favorite(self) -> None:
        """Pin or unpin the highlighted contact as a favourite."""
        contact = self._highlighted_contact()
        if contact is None:
            return
        updated = self._service.toggle_favorite(contact.name)
        self._reload_list(select=updated.name)
        verb = "Favorited" if updated.favorite else "Unfavorited"
        self.notify(f"{verb} {updated.name}")

    def action_copy_phone(self) -> None:
        """Copy the highlighted contact's phone number to the clipboard."""
        self._copy_field("phone", lambda contact: contact.number)

    def action_copy_email(self) -> None:
        """Copy the highlighted contact's e-mail to the clipboard."""
        self._copy_field("e-mail", lambda contact: contact.email)

    def action_focus_search(self) -> None:
        """Jump to the search box so the user can start filtering."""
        self.query_one("#search", Input).focus()

    def action_toggle_favorites_filter(self) -> None:
        """Show only favourites, or all contacts again."""
        self._favorites_only = not self._favorites_only
        self._reload_list()
        state = "on" if self._favorites_only else "off"
        self.notify(f"Favorites filter {state}")

    def action_clear_search(self) -> None:
        """Clear the search box and any filter, then return to the list."""
        if not (self._query or self._favorites_only):
            return
        search = self.query_one("#search", Input)
        search.value = ""  # fires on_input_changed, which reloads the list
        self._favorites_only = False
        self._reload_list()
        self.query_one(ListView).focus()

    # -- Events ----------------------------------------------------------

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter the sidebar live as the user types in the search box."""
        if event.input.id != "search":
            return
        if self._suppress_search:
            # A programmatic clear (e.g. goto_contact) already handled the reload.
            self._suppress_search = False
            return
        self._query = event.value
        self._reload_list()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Pressing Enter in the search box moves focus into the results."""
        if event.input.id == "search":
            self.query_one(ListView).focus()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Render the highlighted contact in the detail card."""
        item = event.item
        self.query_one(ContactCard).contact = (
            item.contact if isinstance(item, ContactListItem) else None
        )

    # -- Helpers ---------------------------------------------------------

    def _after_add(self, contact: Contact | None) -> None:
        """Callback for the add dialog; refresh the list on success."""
        if contact is None:
            return
        self._reload_list(select=contact.name)
        self.notify(f"Added {contact.name}", severity="information")

    def _after_edit(self, contact: Contact | None) -> None:
        """Callback for the edit dialog; refresh the list on success."""
        if contact is None:
            return
        self._reload_list(select=contact.name)
        self.notify(f"Updated {contact.name}", severity="information")

    def _delete(self, contact: Contact) -> None:
        """Remove a contact and offer to undo it."""
        try:
            self._service.delete(contact.name)
        except ContactManagerError as error:
            self.notify(str(error), severity="error")
            return
        self._undo = contact
        self._reload_list()
        self.notify(f"Removed {contact.name} · press u to undo", severity="warning")

    def _highlighted_contact(self) -> Contact | None:
        """The contact under the list cursor, or ``None`` when the list is empty."""
        item = self.query_one(ListView).highlighted_child
        return item.contact if isinstance(item, ContactListItem) else None

    def contacts(self) -> list[Contact]:
        """All contacts — used by the command palette provider."""
        return self._service.list_contacts()

    def goto_contact(self, name: str) -> None:
        """Clear any filter and jump to ``name`` (used by the command palette)."""
        self._favorites_only = False
        self._query = ""
        search = self.query_one("#search", Input)
        if search.value:
            # Clearing fires on_input_changed; suppress its reload so it does
            # not stomp the selection we are about to make below.
            self._suppress_search = True
            search.value = ""
        self._reload_list(select=name)
        self.query_one(ListView).focus()

    def _copy_field(
        self, label: str, getter: Callable[[Contact], str]
    ) -> None:
        """Copy one field of the highlighted contact, with feedback either way."""
        contact = self._highlighted_contact()
        if contact is None:
            return
        value = getter(contact)
        if not value:
            self.notify(f"No {label} to copy for {contact.name}", severity="warning")
            return
        self.copy_to_clipboard(value)
        self.notify(f"Copied {label}: {value}")

    def _announce_birthdays(self) -> None:
        """On launch, gently flag any birthdays coming up this week."""
        upcoming = upcoming_birthdays(self._service.list_contacts())
        if not upcoming:
            return
        summary = ", ".join(
            f"{name} ({birthday_phrase(days)})" for name, days in upcoming[:3]
        )
        self.notify(f"🎂 Upcoming birthdays: {summary}", timeout=8)

    def _reload_list(self, select: str | None = None) -> None:
        """Rebuild the sidebar from the service and restore a selection.

        Children mount asynchronously, so the actual highlight is applied after
        the next refresh (see :meth:`_select`).
        """
        contacts = self._service.list_contacts()
        favorites = sum(contact.favorite for contact in contacts)
        visible = self._visible_contacts(contacts)
        filtering = bool(self._query.strip()) or self._favorites_only

        list_view = self.query_one(ListView)
        list_view.clear()
        list_view.extend(ContactListItem(contact) for contact in visible)

        card = self.query_one(ContactCard)
        card.total = len(contacts)
        card.filter_active = filtering
        if filtering:
            self.sub_title = f"{len(visible)} of {len(contacts)} · {favorites} ★"
        else:
            self.sub_title = f"{len(contacts)} contacts · {favorites} ★"

        if visible:
            self.call_after_refresh(self._select, select)
        else:
            card.contact = None

    def _visible_contacts(self, contacts: list[Contact]) -> list[Contact]:
        """Apply the active favourites filter and search query, in that order."""
        result = contacts
        if self._favorites_only:
            result = [contact for contact in result if contact.favorite]
        query = self._query.strip()
        if query:
            result = [
                contact for contact in result if contact_matches(contact, query)
            ]
        return result

    def _select(self, name: str | None) -> None:
        """Highlight ``name`` (or the first contact) once items are mounted."""
        list_view = self.query_one(ListView)
        names = [item.contact.name for item in list_view.query(ContactListItem)]
        if not names:
            return
        list_view.index = names.index(name) if name in names else 0
