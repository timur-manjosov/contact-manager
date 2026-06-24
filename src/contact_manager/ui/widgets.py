"""Presentation widgets for the master/detail layout.

These are pure view objects: they render a :class:`Contact` and hold no
business logic. The :class:`ContactApp` feeds them data and reacts to their
messages; they never touch the service, repository or validators.
"""

from __future__ import annotations

from datetime import datetime

from rich.align import Align
from rich.console import Group, RenderableType
from rich.markup import escape
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Label, ListItem, Static

from contact_manager.models import Contact

# Muted, recognisable palette for initials avatars. A contact is always shown
# in "their" colour because it is chosen deterministically from the name.
_AVATAR_COLORS: tuple[str, ...] = (
    "#c4a7e7",  # iris
    "#9ccfd8",  # foam
    "#f6c177",  # gold
    "#eb6f92",  # love
    "#3e8fb0",  # pine
    "#ea9a97",  # rose
)

_TEXT = "#e0def4"
_SUBTLE = "#908caa"
_MUTED = "#6e6a86"
_GOLD = "#f6c177"
_FOAM = "#9ccfd8"
_SURFACE = "#2a273f"
_BG = "#232136"


def avatar_for(name: str) -> tuple[str, str]:
    """Return ``(initials, colour)`` for a contact name.

    Up to two initials are taken from the first words of the name; the colour
    is a stable choice from :data:`_AVATAR_COLORS` so a person keeps the same
    avatar across runs.
    """
    initials = "".join(part[0] for part in name.split()[:2]).upper() or "?"
    colour = _AVATAR_COLORS[sum(map(ord, name)) % len(_AVATAR_COLORS)]
    return initials, colour


def _headline(contact: Contact) -> str:
    """Return the one-line "who is this" summary under the name."""
    if contact.title and contact.company:
        return f"{contact.title} · {contact.company}"
    return contact.title or contact.company or contact.nickname


def _pretty_birthday(value: str) -> str:
    """Render a stored birthday as e.g. ``"Dec 9"`` or ``"Dec 9, 1906"``."""
    try:
        if len(value) == 5:  # MM-DD
            parsed = datetime.strptime(f"2000-{value}", "%Y-%m-%d")
        else:  # YYYY-MM-DD
            parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return value
    pretty = parsed.strftime("%b %d").replace(" 0", " ")
    return f"{pretty}, {value[:4]}" if len(value) > 5 else pretty


def _relative_time(iso: str) -> str:
    """Return a short "2d ago" style string for an ISO timestamp."""
    if not iso:
        return ""
    try:
        then = datetime.fromisoformat(iso)
    except ValueError:
        return ""
    now = datetime.now(then.tzinfo)
    seconds = int((now - then).total_seconds())
    minutes, hours, days = seconds // 60, seconds // 3600, seconds // 86400
    if seconds < 60:
        return "just now"
    if minutes < 60:
        return f"{minutes}m ago"
    if hours < 24:
        return f"{hours}h ago"
    if days < 30:
        return f"{days}d ago"
    return then.date().isoformat()


def _list_secondary(contact: Contact) -> str:
    """The dim second line shown beneath a name in the sidebar."""
    return _headline(contact) or contact.number or contact.email


class ContactListItem(ListItem):
    """A single row in the sidebar list, carrying its :class:`Contact`."""

    def __init__(self, contact: Contact) -> None:
        super().__init__()
        self.contact = contact

    def compose(self) -> ComposeResult:
        # A Textual markup *string* (not a Rich Text object) so the row
        # background shows through and the highlight colour applies cleanly.
        contact = self.contact
        star = f"[{_GOLD}]★[/] " if contact.favorite else "  "
        content = f"{star}[b]{escape(contact.name)}[/]"
        secondary = _list_secondary(contact)
        if secondary:
            content += f"\n  [{_SUBTLE}]{escape(secondary)}[/]"
        yield Label(content)


class ContactCard(Static):
    """The detail pane: a rich profile of the highlighted contact.

    Assigning :attr:`contact` re-renders the card; :attr:`total` lets it tell
    the difference between "nothing selected" and "no contacts exist yet" so
    each empty state reads correctly.
    """

    contact: reactive[Contact | None] = reactive(None, layout=True)
    total: reactive[int] = reactive(0)

    def render(self) -> RenderableType:
        if self.contact is None:
            body = self._empty_state()
        else:
            body = self._profile(self.contact)
        # Paint the card background across the whole pane: a bare Rich renderable
        # only colours the cells it occupies, leaving the rest of the widget black.
        return Padding(body, 0, style=f"on {_BG}", expand=True)

    # -- Rendering helpers ----------------------------------------------

    def _profile(self, contact: Contact) -> RenderableType:
        initials, colour = avatar_for(contact.name)

        header = Table.grid(padding=(0, 2))
        header.add_column()
        header.add_column()
        avatar = Text(f"  {initials}  ", style=f"bold {_BG} on {colour}")
        info = Text()
        info.append(f"{contact.name}\n", style=f"bold {_TEXT}")
        headline = _headline(contact)
        if headline:
            info.append(f"{headline}\n", style=_SUBTLE)
        if contact.favorite:
            info.append("★ favorite", style=_GOLD)
        header.add_row(avatar, info)

        meta = Table.grid(padding=(0, 2))
        meta.add_column(style=_SUBTLE, justify="left", width=9)
        meta.add_column(style=_TEXT)
        birthday = _pretty_birthday(contact.birthday) if contact.birthday else ""
        for label, value in (
            ("PHONE", contact.number),
            ("EMAIL", contact.email),
            ("WEB", contact.website),
            ("LOCATION", contact.location),
            ("BIRTHDAY", birthday),
        ):
            if value:
                meta.add_row(label, value)

        parts: list[RenderableType] = [header, Text(), meta]

        if contact.tags:
            tags = Text()
            for tag in contact.tags:
                tags.append(f" #{tag} ", style=f"{_FOAM} on {_SURFACE}")
                tags.append("  ")
            parts += [Text(), tags]

        if contact.notes:
            parts += [
                Text(),
                Text("── NOTES ──", style=f"bold {_SUBTLE}"),
                Text(contact.notes, style=_TEXT),
            ]

        relative = _relative_time(contact.updated_at)
        if relative:
            parts += [Text(), Text(f"updated {relative}", style=f"italic {_MUTED}")]

        return Group(*parts)

    def _empty_state(self) -> RenderableType:
        if self.total == 0:
            body = Group(
                Text("╭────╮", justify="center", style=_MUTED),
                Text("│ ·· │", justify="center", style=_MUTED),
                Text("╰────╯", justify="center", style=_MUTED),
                Text(),
                Text("No contacts yet.", justify="center", style=f"bold {_TEXT}"),
                Text(),
                Text(
                    "Press  a  to add your first one.",
                    justify="center",
                    style=_SUBTLE,
                ),
            )
        else:
            body = Group(
                Text("Select a contact", justify="center", style=f"bold {_TEXT}"),
                Text(),
                Text("…or press  a  to add one.", justify="center", style=_SUBTLE),
            )
        return Align.center(body, vertical="middle")
