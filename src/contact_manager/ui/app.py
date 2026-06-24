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

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header, ListView

from contact_manager.exceptions import ContactManagerError
from contact_manager.models import Contact
from contact_manager.services import ContactService
from contact_manager.ui.screens import AddContactScreen
from contact_manager.ui.widgets import ContactCard, ContactListItem

_STYLES = Path(__file__).with_name("styles.tcss")


class ContactApp(App[None]):
    """A keyboard-driven address book rendered with Textual."""

    CSS_PATH = _STYLES
    TITLE = "Contacts"

    BINDINGS = [
        ("a", "add_contact", "Add"),
        ("f", "toggle_favorite", "Favorite"),
        ("d", "delete_contact", "Delete"),
        ("q", "quit", "Quit"),
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
        with Horizontal(id="body"):
            yield ListView(id="contact-list")
            yield ContactCard(id="card")
        yield Footer()

    def on_mount(self) -> None:
        """Populate the list, focus it, and play a gentle fade-in."""
        self._reload_list()
        self.query_one(ListView).focus()
        self.styles.opacity = 0.0
        self.styles.animate("opacity", value=1.0, duration=0.4)

    # -- Actions ---------------------------------------------------------

    def action_add_contact(self) -> None:
        """Open the new-contact dialog."""
        self.push_screen(AddContactScreen(self._service), self._after_add)

    def action_delete_contact(self) -> None:
        """Delete the highlighted contact, if any."""
        contact = self._highlighted_contact()
        if contact is None:
            return
        try:
            self._service.delete(contact.name)
        except ContactManagerError as error:
            self.notify(str(error), severity="error")
            return
        self._reload_list()
        self.notify(f"Removed {contact.name}", severity="warning")

    def action_toggle_favorite(self) -> None:
        """Pin or unpin the highlighted contact as a favourite."""
        contact = self._highlighted_contact()
        if contact is None:
            return
        updated = self._service.toggle_favorite(contact.name)
        self._reload_list(select=updated.name)
        verb = "Favorited" if updated.favorite else "Unfavorited"
        self.notify(f"{verb} {updated.name}")

    # -- Events ----------------------------------------------------------

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

    def _highlighted_contact(self) -> Contact | None:
        """The contact under the list cursor, or ``None`` when the list is empty."""
        item = self.query_one(ListView).highlighted_child
        return item.contact if isinstance(item, ContactListItem) else None

    def _reload_list(self, select: str | None = None) -> None:
        """Rebuild the sidebar from the service and restore a selection.

        Children mount asynchronously, so the actual highlight is applied after
        the next refresh (see :meth:`_select`).
        """
        contacts = self._service.list_contacts()
        favorites = sum(contact.favorite for contact in contacts)

        list_view = self.query_one(ListView)
        list_view.clear()
        list_view.extend(ContactListItem(contact) for contact in contacts)

        card = self.query_one(ContactCard)
        card.total = len(contacts)
        self.sub_title = f"{len(contacts)} contacts · {favorites} ★"

        if contacts:
            self.call_after_refresh(self._select, select)
        else:
            card.contact = None

    def _select(self, name: str | None) -> None:
        """Highlight ``name`` (or the first contact) once items are mounted."""
        list_view = self.query_one(ListView)
        names = [item.contact.name for item in list_view.query(ContactListItem)]
        if not names:
            return
        list_view.index = names.index(name) if name in names else 0
