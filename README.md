<div align="center">

# Contact Manager

**A fast, keyboard-driven contact manager for your terminal.**

Built in Python with [Textual](https://textual.textualize.io/) — a clean master/detail interface in a Rosé Pine Moon theme.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Built with Textual](https://img.shields.io/badge/built%20with-Textual-5a4fcf.svg)](https://textual.textualize.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-pytest-0a9edc.svg)](tests/)
[![Code style: Ruff](https://img.shields.io/badge/lint-ruff-261230.svg)](https://docs.astral.sh/ruff/)

</div>

---

## Overview

Contact Manager is a small but complete TUI (terminal user interface) application
for keeping track of the people you know — entirely from the keyboard. A sidebar
list pairs with a rich detail card so each contact reads like a person (initials
avatar, role, tags, notes, favorites) rather than a row in a database. It is also
a deliberately clean reference for **layered application design in Python**: the
user interface, business rules and storage are fully decoupled, so each can be
understood, tested or replaced on its own.

> [!NOTE]
> The UI never touches the database and the database never knows about the UI.
> Everything flows through a single service layer, which is the only place that
> validates input and enforces the rules.

## Features

| Feature | Description |
| --- | --- |
| 📇 **Master / detail** | A sidebar list on the left, a rich profile card on the right. |
| 👤 **Rich contacts** | Phone, e-mail, company, title, location, website, birthday, tags and notes. |
| 🅰️ **Initials avatars** | Each contact gets a stable, colour-coded avatar from their initials. |
| 🔎 **Live search** | Press `/` and type to filter the sidebar instantly across name, company, tags and more. |
| ⭐ **Favorites** | Pin the people you reach for most with `f`, or narrow the list to just them with `F`. |
| 🏷️ **Tags** | Group contacts with lightweight, free-form labels. |
| ➕ **Add & edit** | Focused modal forms (`a` / `e`) create or update a contact; validation errors show inline. |
| 🗑️ **Safe delete** | Deleting asks first, and a one-key **undo** (`u`) brings the contact back. |
| 📋 **Copy fields** | Yank a contact's phone (`y`) or e-mail (`Y`) straight to the clipboard. |
| 🎂 **Birthday glance** | Upcoming birthdays are flagged on the card and announced on launch. |
| 🎛️ **Command palette** | `Ctrl+P` to fuzzy-jump to any contact or run actions hands-free. |
| ⌨️ **Keyboard-first** | Browse, search, add, edit, favorite and delete without ever reaching for the mouse. |
| ✅ **Validated input** | Names and numbers are required; e-mail, website and birthday are format-checked. |
| 💾 **Safe persistence** | Changes are written atomically to JSON — no half-saved files. |
| 🎨 **Themed** | Quiet, intentional styling using the Rosé Pine Moon palette. |

## Screenshots

<div align="center">

![Contact Manager screenshot](assets/screenshot.png)

</div>

## Installation

> Requires **Python 3.10+**. Textual is installed automatically as a dependency.

```bash
git clone https://github.com/timur-manjosov/contact-manager.git
cd contact-manager

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -e .
```

## Usage

Launch the app with the installed console script:

```bash
contacts
```

…or run it as a module without installing the script:

```bash
python -m contact_manager
```

Browse with `↑` / `↓` — the detail card updates as you move. Press `/` to search
and filter the list as you type, or `F` to show only your favorites; press `Esc`
to clear the filter and return to the list. Press `a` to open the new-contact
form, fill in the fields (only **Name** and **Phone** are required) and press
`Enter` to save; press `e` to edit the highlighted contact (its name is locked —
rename by deleting and re-adding). Pin a contact with `f`. Pressing `d` asks for
confirmation before removing a contact, and `u` undoes the last deletion. Copy
the highlighted contact's phone with `y` or e-mail with `Y`, and press `Ctrl+P`
to fuzzy-jump to anyone by name. Birthdays in the next week are flagged on the
contact card and announced when you launch the app. Contacts are saved to
`contacts.json` in the current working directory.

> [!TIP]
> Point the app at a different data file with the `CONTACTS_FILE` environment
> variable: `CONTACTS_FILE=~/.local/share/contacts.json contacts`

### Keybindings

| Key | Action |
| --- | --- |
| `↑` / `↓` | Move between contacts |
| `a` | Add a contact (opens the form) |
| `e` | Edit the highlighted contact |
| `/` | Search / filter the list as you type |
| `f` | Toggle the highlighted contact as a favorite |
| `F` | Filter to favorites only (toggle) |
| `d` | Delete the highlighted contact (asks to confirm) |
| `u` | Undo the last deletion |
| `y` / `Y` | Copy the highlighted contact's phone / e-mail |
| `Esc` | Clear the search / filter (or cancel a dialog) |
| `Enter` | Save the contact (in the add / edit form) |
| `Ctrl` + `p` | Command palette (jump to a contact, run actions) |
| `q` | Quit |

## Architecture

The codebase follows a layered architecture. Dependencies point **inward** —
outer layers know about inner ones, never the reverse — so business logic has
no idea a terminal UI or a JSON file exists.

```mermaid
flowchart TD
    UI["ui · ContactApp<br/><i>Textual front-end</i>"]
    SVC["services · ContactService<br/><i>validation & rules</i>"]
    REPO["repositories · ContactRepository<br/><i>persistence interface</i>"]
    JSON["JsonContactRepository<br/><i>atomic JSON storage</i>"]
    MODEL["models · Contact<br/><i>immutable record</i>"]

    UI --> SVC
    SVC --> REPO
    REPO -.implemented by.-> JSON
    SVC --> MODEL
    REPO --> MODEL
```

| Layer | Responsibility | Knows about |
| --- | --- | --- |
| `models` | Immutable domain data (`Contact`). | nothing |
| `repositories` | Load/save behind an interface; swap JSON for SQLite later. | `models` |
| `services` | Validation, uniqueness, orchestration — the single source of rules. | `models`, `repositories` |
| `ui` | Render widgets, capture input, show notifications. | `services`, `models` |
| `config` | Resolve runtime settings (data-file location). | — |
| `app.py` | Composition root: wires the layers together. | everything |

See [`docs/architecture.md`](docs/architecture.md) for a deeper walkthrough.

## Project structure

```
contact-manager/
├── src/
│   └── contact_manager/
│       ├── app.py              # Composition root + console entry point
│       ├── __main__.py         # `python -m contact_manager`
│       ├── exceptions.py       # Domain exception hierarchy
│       ├── models/             # Contact dataclass
│       ├── repositories/       # ContactRepository + JSON implementation
│       ├── services/           # ContactService (business logic)
│       ├── ui/                 # Textual app, widgets, modal screens, command palette + styles.tcss
│       ├── config/             # Settings resolution
│       └── utils/              # Field validators
├── tests/                      # pytest suite (unit + UI integration)
├── docs/                       # Architecture notes
├── assets/                     # Screenshots and media
├── pyproject.toml              # Packaging, deps, tooling config
└── README.md
```

## Development setup

```bash
# Install the package with its development extras (pytest, ruff, …)
pip install -e ".[dev]"
```

| Task | Command |
| --- | --- |
| Run the app | `contacts` |
| Run the tests | `pytest` |
| Lint | `ruff check .` |
| Auto-fix lint | `ruff check --fix .` |

## Testing

The suite covers each layer independently plus an end-to-end UI test driven by
Textual's [pilot](https://textual.textualize.io/guide/testing/) harness:

```bash
pytest            # run everything
pytest -v         # verbose
pytest tests/test_contact_service.py   # one module
```

- **Unit tests** validate the model, validators, repository and service in isolation.
- **Integration tests** drive the real UI with simulated key presses and clicks,
  asserting on application state rather than pixels.

## Roadmap

- [x] Per-contact detail view with notes, tags and favorites.
- [x] Live search & filtering (by name, company, tag) in the sidebar.
- [x] Edit existing contacts, with confirm-before-delete and one-key undo.
- [ ] Pluggable SQLite backend behind the existing repository interface.
- [ ] Import / export (CSV, vCard).
- [ ] Configurable themes.

## Contributing

Contributions are welcome! Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) for the
workflow, coding standards and how to run the checks before opening a pull request.

In short: fork, branch, keep the layers separated, add tests, run `ruff` and
`pytest`, then open a PR.

## License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

## Built with

- [Python](https://www.python.org/) 3.10+
- [Textual](https://textual.textualize.io/) — the terminal UI framework
- [pytest](https://docs.pytest.org/) — testing
- [Ruff](https://docs.astral.sh/ruff/) — linting & import sorting
