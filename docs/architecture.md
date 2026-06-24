# Architecture

This document explains how Contact Manager is structured and why. The goal of
the design is simple: **business logic should not depend on the user interface
or the storage mechanism.** Everything below follows from that.

## Layers

The application is split into concentric layers. Dependencies only ever point
inward, from the outer layers (which change often) toward the inner ones (which
change rarely).

```
        ┌─────────────────────────────────────────────┐
        │  ui/  ContactApp  (Textual)                  │  presentation
        │     │                                        │
        │     ▼                                        │
        │  services/  ContactService                   │  business rules
        │     │              │                         │
        │     ▼              ▼                         │
        │  models/Contact   repositories/Repository    │  domain + ports
        │                      ▲                        │
        │                      │ implements             │
        │            JsonContactRepository              │  adapters
        └─────────────────────────────────────────────┘
```

### `models/` — the domain

`Contact` is a frozen, slotted dataclass: an immutable value object with no
behaviour beyond (de)serialisation. It depends on nothing, which makes it the
stable core the rest of the system is built around.

### `repositories/` — the persistence port

`ContactRepository` is an abstract base class defining `load()` and `save()`.
The service depends on this *interface*, not on any concrete store — an
application of the **Dependency Inversion Principle**. `JsonContactRepository`
is the default adapter; a future `SqliteContactRepository` could be dropped in
without touching the service or the UI.

Writes are **atomic**: data is written to a temporary file and then renamed over
the target, so a crash mid-save can never corrupt `contacts.json`.

### `services/` — the business logic

`ContactService` is the heart of the application and the **single source of
truth for the rules**:

- It is the only place that turns raw user strings into validated `Contact`
  objects (via `utils/validators`).
- It enforces that names are unique and that required fields are present.
- It caches contacts in an insertion-ordered `dict` keyed by name, giving O(1)
  lookups, duplicate checks and deletions while preserving display order.
- Every mutation persists immediately, so memory and disk never drift apart.

Failures are reported through a small exception hierarchy
(`ValidationError`, `DuplicateContactError`, `ContactNotFoundError`) so callers
can react precisely instead of parsing error strings.

### `ui/` — the presentation

`ContactApp` is a thin Textual front-end. It renders widgets, captures input and
translates the service's domain exceptions into on-screen notifications. It
holds **no business rules** — remove the UI and the service still works exactly
the same, which is what the test suite demonstrates.

### `config/` and `app.py`

`config/settings.py` resolves runtime configuration (where the data file lives,
overridable via the `CONTACTS_FILE` environment variable) in one place.
`app.py` is the **composition root**: the single location where concrete classes
are instantiated and injected together. Wiring lives here so the rest of the
package can depend purely on abstractions.

## Data flow: adding a contact

1. The user types into the inputs and presses **Add**.
2. `ContactApp._add_contact` reads the field values and calls
   `ContactService.add(name, number, email)`.
3. The service normalises and validates each field, checks for a duplicate
   name, constructs a `Contact`, and saves the collection through the
   repository.
4. On success the UI appends a row and shows a confirmation; on a
   `ContactManagerError` it shows the message as an error notification.

The UI knows *nothing* about validation rules or JSON — it only knows how to ask
the service and how to display the answer.

## Why this matters

- **Testability** — each layer is tested in isolation, plus one end-to-end UI
  test. Most tests need no UI at all.
- **Extensibility** — new storage backends or even a different front-end (a web
  UI, a CLI) reuse the service unchanged.
- **Maintainability** — a contributor changing validation looks in exactly one
  place; a contributor restyling the table never risks breaking the rules.
