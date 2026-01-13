# AGENTS.md

## Coding preferences (must follow)

When you make changes, you must follow these conventions:

### Python version and type hints

- Target **Python 3.13**.
- Use **native type hints** for built-ins (`list`, `dict`, `str`, etc.).
- Use **type hints** throughout the codebase (functions, return types, public objects).

### Docstrings and comments

- Prefer **docstrings** (Google/Numpy style is fine; keep consistent with existing Numpy-style docstrings in `main.py`).
- Use comments sparingly; only when intent is non-obvious and cannot be expressed clearly via names/structure.

### Tooling

- Use **uv** for dependency management and virtual environments.
- Use **ruff** for both linting and formatting.

## Commands you must run after each change to the code

### Lint/format (ruff)

- Format:
  - `ruff format`
- Lint:
  - `ruff check`
- Autofix:
  - `ruff check --fix`

If the above commands reveal any issues, fix them before proceeding.

### Tests

- Once all formatting and linting is complete, run all tests:
  - `uv run pytest`
