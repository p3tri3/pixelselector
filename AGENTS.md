# AGENTS.md

Guidance for autonomous AI agents (OpenAI Codex, Google Gemini/Jules, etc.).

For project architecture, state model, dev setup, tool commands, and project
structure see [CLAUDE.md](CLAUDE.md). This file covers the validation workflow,
hard constraints, test authoring rules, and definition of done.

---

## Environment Bootstrap

```bash
pip install -e ".[dev]"          # installs project + all dev tools
sudo apt-get install -y xvfb     # required for headless Tkinter (CI / no display)
```

---

## Validation Sequence

Run every check below in order before marking any task complete. All must pass.

```bash
ruff check .                      # exit 0 required
ruff format --check .             # exit 0 required
mypy --strict pixelselector.py    # exit 0 required — zero errors
bandit -r pixelselector.py        # no HIGH or MEDIUM findings
vulture pixelselector.py          # informational only — see note below
xvfb-run pytest                   # exit 0 required; coverage ≥80% enforced by config
```

**vulture note:** `_app` in the `__main__` block is intentionally unused at
runtime (it keeps the `PixelSelectorApp` instance alive for `mainloop`). This
finding is expected and safe to ignore.

If `xvfb-run` is unavailable and `$DISPLAY` is set, plain `pytest` works.

---

## Hard Constraints

Violating any of these will cause CI to fail or introduce a regression.

| # | Constraint |
|---|---|
| 1 | **Single production file.** All application code lives in `pixelselector.py`. Do not create additional modules or packages for production code. |
| 2 | **No new runtime dependencies.** Only `tkinter`/`json`/`sys`/`os` (stdlib) and `Pillow` are permitted. Any other `import` in `pixelselector.py` is a hard blocker. |
| 3 | **State sync invariant.** `self.pixels`, `self.markers`, and `self.listbox` must always be consistent. Every mutating operation must keep all three in sync — call `update_markers()` when the list changes. |
| 4 | **Python 3.11+ type syntax.** Use `X \| None`, `list[...]`, `tuple[...]`. Never `Optional[X]`, `List[X]`, or `Union[X, Y]`. |
| 5 | **`pyproject.toml` is the single config source.** Do not create `setup.cfg`, `tox.ini`, `.mypy.ini`, `pytest.ini`, or any other per-tool config file. |
| 6 | **Output path convention.** Save output files as `{image_filename}_pixels.json` and `{image_filename}_reference.png` in `os.getcwd()`. Do not change this. |

---

## Writing Tests

New behaviour requires new tests. Place them in `tests/` following the existing
file layout (see [CLAUDE.md → Project Structure](CLAUDE.md)).

### Use the shared fixtures from `tests/conftest.py`

```python
def test_something(app, sample_image, tmp_path, monkeypatch):
    ...
```

| Fixture | What it provides |
|---|---|
| `app` | Fresh `PixelSelectorApp` instance (function-scoped) against a session-scoped headless `tk.Tk()` root |
| `sample_image` | Path to a 10×10 red PNG saved in `tmp_path` |
| `tmp_path` | pytest built-in; use with `monkeypatch.chdir(tmp_path)` to control output file destination |

### Required patterns

- **Suppress dialogs** — patch `tkinter.messagebox.showinfo` (and `.showerror`) in any test that triggers them.
- **Suppress file dialogs** — patch `tkinter.filedialog.askopenfilename` to return a path or `""`.
- **Canvas coordinates** — `canvas.canvasx(x)` returns `float(x)` on an unscrolled canvas; no mock needed unless the canvas has been scrolled.
- **Listbox nearest** — `listbox.nearest(y)` is a real Tk method; monkeypatch it on the instance (`app.listbox.nearest = lambda y: idx`) when testing `drag_reorder`.
- **Output files** — always `monkeypatch.chdir(tmp_path)` before calling `save_json` or `export_image` so files land in a temp directory, not the repo root.

---

## Definition of Done

A change is complete and ready for review when:

1. All six validation commands above exit with the expected codes.
2. Every new code path introduced by the change is covered by at least one test.
3. The state sync invariant (constraint 3) holds for any new mutating operation.
4. No new `# type: ignore` comments have been added without an explanatory inline note.
5. `git diff` shows no unintentional whitespace or formatting changes.

---

## Discovering Planned Work

`TASKLIST.md` in the repo root lists all planned improvements grouped by
dependency order, with ✅ marks on completed items. Check it first to understand
what is already done and what is outstanding before starting new work.
