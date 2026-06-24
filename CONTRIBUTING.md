# Contributing

Thanks for your interest in improving Contact Manager! This project doubles as a
reference for clean, layered Python design, so contributions are reviewed with an
eye on architecture as much as functionality.

## Getting started

```bash
git clone https://github.com/timur-manjosov/contact-manager.git
cd contact-manager
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Workflow

1. **Fork** the repository and create a branch off `main`:
   `git checkout -b feat/short-description`.
2. Make your change, keeping the layer boundaries intact (see below).
3. Add or update tests for your change.
4. Run the checks (they must pass):
   ```bash
   ruff check .
   pytest
   ```
5. Commit with a clear, [conventional](https://www.conventionalcommits.org/)
   message (`feat:`, `fix:`, `docs:`, `refactor:`, …).
6. Open a pull request describing **what** changed and **why**.

## Architecture guidelines

The single most important rule: **respect the layer boundaries**. See
[`docs/architecture.md`](docs/architecture.md) for the full picture.

- **Business rules** (validation, uniqueness, anything about what a "valid"
  contact is) belong in `services/` — never in the UI.
- **The UI** (`ui/`) may only call the service; it must not import repositories,
  validators or touch files directly.
- **New storage backends** go in `repositories/` as subclasses of
  `ContactRepository`; don't special-case them anywhere else.
- **Models** stay free of I/O and UI concerns.

## Coding standards

- Follow **PEP 8**; `ruff` enforces style and import ordering.
- Add **type hints** to all new public functions and methods.
- Write **docstrings** for modules, public classes and functions.
- Prefer readability over cleverness; avoid premature optimisation.
- Keep functions focused — one responsibility each.

## Tests

- Put tests under `tests/`, mirroring the package layout.
- Unit-test new logic in isolation; reach for the Textual pilot harness only for
  genuine UI behaviour.
- Every bug fix should come with a regression test.
