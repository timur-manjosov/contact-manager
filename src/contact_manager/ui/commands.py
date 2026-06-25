"""A command-palette provider for the contact manager.

Registered on :class:`~contact_manager.ui.app.ContactApp`, this lets the user
press ``Ctrl+P`` and fuzzily jump to any contact by name or run the common
actions (copy phone/email, toggle favorite) on the highlighted one — all
through the same service-backed methods the key bindings use.
"""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from textual.command import Hit, Hits, Provider

if TYPE_CHECKING:
    from contact_manager.ui.app import ContactApp


class ContactCommands(Provider):
    """Surface contacts and per-contact actions in the command palette."""

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        app: ContactApp = self.app  # type: ignore[assignment]

        for contact in app.contacts():
            command = f"Go to {contact.name}"
            score = matcher.match(command)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(command),
                    partial(app.goto_contact, contact.name),
                    help="Jump to this contact",
                )

        actions = (
            ("Copy phone number", app.action_copy_phone, "Copy the highlighted phone"),
            ("Copy email address", app.action_copy_email, "Copy the highlighted email"),
            ("Toggle favorite", app.action_toggle_favorite, "Star the highlighted one"),
        )
        for label, callback, help_text in actions:
            score = matcher.match(label)
            if score > 0:
                yield Hit(score, matcher.highlight(label), callback, help=help_text)
