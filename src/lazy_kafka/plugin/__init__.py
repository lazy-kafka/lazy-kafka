"""Plugin protocol and in-repo registry.

A :class:`Plugin` bundles the three surfaces a lazy-kafka service exposes:

* a dashboard panel (a Textual ``Widget`` mounted as a tab),
* an optional Typer sub-app for CLI commands,
* (implicitly) any configuration it needs, read from the shared
  :class:`lazy_kafka.config.Configuration`.

Built-in plugins live under :mod:`lazy_kafka.plugins` and register
themselves on import.  The shell calls :func:`load_builtin_plugins`
once during start-up and then iterates :func:`iter_plugins`.

When this project splits into separate distributions, the registry
can be swapped for ``importlib.metadata.entry_points("lazy_kafka.plugins")``
without touching call sites.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    import typer
    from textual.widget import Widget

    from lazy_kafka.config import Configuration

_LOGGER = logging.getLogger(__name__)


@runtime_checkable
class Plugin(Protocol):
    """Dashboard + CLI extension point."""

    name: str
    """Stable, machine-readable identifier (e.g. ``"core-kafka"``)."""

    tab_label: str
    """Rich-markup label shown on the dashboard tab."""

    tab_id: str
    """DOM id used for the ``Tab`` and the mounted panel widget."""

    cli_name: str | None
    """Typer sub-command name (``None`` disables the CLI surface)."""

    def build_panel(self, config: Configuration) -> Widget | str:
        """Build the dashboard panel.

        Return a ``Widget`` on success or a plain ``str`` on connection failure.
        A string result is displayed as a ``Label`` in the tab so the dashboard
        still mounts without crashing.
        """
        ...

    def build_cli(self) -> typer.Typer | None:
        """Return the plugin's Typer sub-app, or ``None`` if unused."""
        ...


_PLUGINS: list[Plugin] = []


def register(plugin: Plugin) -> Plugin:
    """Register a plugin instance.

    Idempotent on ``plugin.name`` — re-registering with the same name
    replaces the previous entry (useful for hot-reload in development).
    """
    for i, existing in enumerate(_PLUGINS):
        if existing.name == plugin.name:
            _LOGGER.debug("replacing plugin %r", plugin.name)
            _PLUGINS[i] = plugin
            return plugin
    _PLUGINS.append(plugin)
    return plugin


def iter_plugins() -> Iterator[Plugin]:
    """Iterate registered plugins in registration order."""
    return iter(_PLUGINS)


def load_builtin_plugins() -> None:
    """Import built-in plugin modules so they self-register.

    Safe to call more than once.
    """
    import lazy_kafka.plugins  # noqa: F401  (side-effect import)


__all__ = ["Plugin", "iter_plugins", "load_builtin_plugins", "register"]
