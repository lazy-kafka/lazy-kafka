# Agent Notes

## Justfile / task runner hygiene

Do not add `just` (or any task-runner) recipes that are a trivial alias for a
single straightforward command, e.g.:

- `sync: uv sync` — just tell people to run `uv sync`.
- `install-cog: cargo install --locked cocogitto` — a one-liner someone runs
  once; document it in prose instead.
- `lint: ruff check .` / `format: ruff format .` — these are already obvious
  and memorable as `uv run ruff check .` / `uv run ruff format .`.

Every alias is something future readers have to discover, remember, and
maintain (keeping it in sync with the underlying tool's flags/version). Only
add a `just` recipe when it actually saves meaningful complexity: multiple
steps, non-obvious flags, conditional logic, or something people get wrong
when typed by hand (see `release` in `Justfile` for an example that's
justified). When in doubt, leave it out and just document the plain command.

## Nix / devenv vs. task runners

`devenv.nix` is responsible for provisioning tools (installing `uv`, `git`,
`just`, etc. and syncing the venv on shell entry). Don't duplicate that
responsibility in `Justfile` recipes (e.g. no `just install-uv` or similar) —
if a tool needs to be available, that's a `devenv.nix` change, not a `just`
command. Exception: tools intentionally left for the user/CI to install
explicitly (e.g. `cocogitto`, which is installed via `cargo install` directly
in `.github/workflows/release.yaml` and expected to be installed manually for
local release work) — don't add devenv/nix support for those unless asked.

## TUI architecture (Textual)

Entry point: `src/lazy_kafka/__main__.py` (`LazyKafka` app). Screens are
switched through `App.MODES` (`dashboard`, `settings`, `logs`) via key
bindings — no screen stacking for these; the app "changes mode", it does not
push modals.

### Screen/widget conventions (consistency rules)

- One `Footer` per screen, composed by the **Screen**, never by its child
  widgets. `style.tcss` docks `Footer` to `top`, so duplicate footers stack
  into a doubled header bar.
- `set_focus` exists on App/Screen only. On a widget use `widget.focus()`.
- Every `DataTable`: construct with `cursor_type="row", zebra_stripes=True`,
  give it `background: $background` (not `$surface`), transparent header,
  odd/even row backgrounds — copy the rules from
  `src/lazy_kafka/widgets/common.py` / `_logs.py`.
- Full-height table screens get their frame from the shared `has-border`
  class in `style.tcss` (round `$primary` border) plus a `border_title` set
  in `on_mount`. Don't redefine border CSS per widget.
- Selection/detail UX lives in `src/lazy_kafka/widgets/common.py`:
  - `WidgetWithDataTable` — base class for hook-fed table widgets
    (topics, messages, schema registry, connect).
  - `DataTableCursorMixin` — j/k cursor movement (vim style).
  - Vim jump keys follow the same cursor-based model (never raw view
    scrolling, which table rebuilds would fight): `G` = last row,
    `gg` = first row, and while the cursor sits on the last row, rebuilds
    keep following new entries.
    Note: textual 8.x does not support multi-key bindings — `Binding("g g")`
    registers a literal key no keypress can match. Sequences must be tracked
    manually (see `LogsWidget.action_handle_g` + pending timer).
  - `DetailsPanelMixin` — reactive `details` + `watch_details` that mounts a
    bordered `SubjectDetails` panel docked at the bottom.
  Any new table screen must reuse these mixins/classes instead of
  reimplementing navigation or a details pane.

### Logging

`main()` routes the root logger ONLY into the in-app `LogHandler`
(`widgets/_logs.py`); filtering happens at display level (`LogsWidget`).
Do not attach `logging.StreamHandler` or `TextualHandler` to the root logger:
before `app.run()` starts console capture, they print straight to the
terminal and pollute the TUI's clean startup. `LogsWidget` rebuilds its table
on a 0.1s interval but skips the rebuild when the filtered entry set and
level are unchanged; row keys are `f"log-{id(entry)}"` and selection/cursor
are preserved across rebuilds.

### Testing the TUI

- Headless testing uses Textual's Pilot: `async with app.run_test(size=...)
  as pilot:` — no real terminal needed. Existing examples:
  `tests/integration/test_tui.py`.
- `pytest.ini` sets `--asyncio-mode=auto`: async test functions need no
  `@pytest.mark.asyncio` marker.
- `LazyKafka()` reads the user's real config (`~/.config/.lazy-kafka.toml`);
  missing file is handled and falls back to defaults. To control logging in
  tests, pass a dedicated `LogHandler` (or emit records via
  `handler.emit(logging.LogRecord(...))`) — pytest's global root-logger state
  can point elsewhere.
- Assert rendering by inspecting the DOM (`app.screen`,
  `query_one(...)`, `styles.*`) — `App.export_text` does not exist in
  textual 8.x.

