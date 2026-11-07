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
