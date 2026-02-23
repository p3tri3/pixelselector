# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

```bash
python pixelselector.py [image_path]
```

The image path argument is optional; if omitted, a file dialog opens on launch.

## Dependencies

- Python standard library: `tkinter`, `json`, `sys`, `os`
- Third-party: `Pillow` (PIL)

Install all dev tools: `pip install -e ".[dev]"`

## Dev Setup

```bash
pip install -e ".[dev]"   # project + ruff, mypy, bandit, vulture, pytest, pytest-cov
pip install pre-commit && pre-commit install   # git hooks (mirror CI checks)
```

## Running Tests

```bash
pytest                    # runs tests/, enforces ≥80% coverage
xvfb-run pytest           # headless (CI / no display)
```

## Tool Commands

```bash
ruff check .              # lint
ruff format --check .     # format check
mypy --strict pixelselector.py
bandit -r pixelselector.py
vulture pixelselector.py  # dead code — `_app` in __main__ is intentional, not dead
```

## Project Structure

```
pixelselector.py          # sole production module
tests/                    # pytest suite (~21 tests, ≥95% coverage)
  conftest.py             # session-scoped headless tk_root + app + sample_image fixtures
pyproject.toml            # single config for ruff / mypy / pytest / coverage / bandit
.pre-commit-config.yaml   # ruff, ruff-format, mypy --strict, bandit hooks
.github/workflows/
  ci.yml                  # ruff + mypy + bandit + vulture + xvfb pytest + codecov
  codeql.yml              # weekly CodeQL security scan
codecov.yml               # 80% coverage target, 2pp threshold
```

## Notes & Gotchas

- Writing to `.github/workflows/` is blocked by a security pre-tool hook; use `Bash` with a heredoc instead of the `Write` tool.
- Type annotations must use Python 3.11+ syntax: `X | None`, `list[...]`, `tuple[...]` — never `Optional[X]` or `List[X]`.
- `canvas.canvasx(x)` returns `float(x)` on an unscrolled, withdrawn canvas — no mock needed in tests.
- Output files go to `os.getcwd()`; tests use `monkeypatch.chdir(tmp_path)` to control destination.

## Architecture

This is a single-file Tkinter GUI application (`pixelselector.py`) consisting of one class, `PixelSelectorApp`.

**Layout:**
- Left panel: scrollable `Canvas` displaying the loaded image. Mouse clicks record pixel coordinates.
- Right panel: `Listbox` showing numbered pixel entries. Supports drag-to-reorder and remove-selected.

**State:** `self.pixels` (list of `(x, y)` tuples), `self.markers` (canvas text item IDs), `self.image` (PIL Image), `self.image_filename` (stem of the loaded file path, used for output naming).

**Output files** are written to the working directory, named after the loaded image:
- `{image_filename}_pixels.json` — JSON with a `"pixels"` key containing the coordinate list
- `{image_filename}_reference.png` — copy of the image annotated with red numbered labels

**Key methods:**
- `record_pixel` — captures canvas coordinates on left-click and appends to `self.pixels`
- `update_markers` — redraws all canvas markers after reorder or removal to keep numbering consistent
- `quick_save` — calls `save_json` + `export_image` without a save dialog
