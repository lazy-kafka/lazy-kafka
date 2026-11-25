#!/usr/bin/env python
"""Capture SVG screenshots of the lazy-kafka TUI for the docs page.

Runs the TUI headlessly (Textual Pilot) against the locally configured
Kafka / Schema Registry, drives it into a few representative states and
exports each as an inline-able SVG via `App.export_screenshot()` — the same
mechanism the Textual widget gallery uses.

Screens are written to `docs/screens/*.svg` and embedded in `docs/index.html`
through `<img>` tags (SVG stays crisp at any size and needs no JS player).

Usage:

    uv run python scripts/capture_screens.py            # all shots
    uv run python scripts/capture_screens.py topics ... # a subset
    uv run python scripts/capture_screens.py --list     # shot names
"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import TYPE_CHECKING

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS_DIR = os.path.join(REPO_ROOT, "docs", "screens")
SIZE = (112, 34)

if TYPE_CHECKING:
    from textual.pilot import Pilot
    from textual.widgets import DataTable

    from lazy_kafka.__main__ import LazyKafka


def _handle_name(data_table: DataTable) -> str | None:
    """Row key of the currently highlighted row."""
    key = data_table.coordinate_to_cell_key(data_table.cursor_coordinate).row_key.value
    return str(key) if key is not None else None


async def _wait_rows(pilot: Pilot, table: DataTable, deadline: float = 15.0) -> None:
    """Wait until the table has data (workers hit real Kafka)."""
    waited = 0.0
    while table.row_count == 0 and waited < deadline:
        await pilot.pause(0.2)
        waited += 0.2
    if table.row_count == 0:
        raise RuntimeError("table stayed empty — is local Kafka reachable?")


async def capture(pilot: Pilot, app: LazyKafka, name: str, title: str) -> None:
    """Export the current screen as `docs/screens/<name>.svg`."""
    os.makedirs(SHOTS_DIR, exist_ok=True)
    path = os.path.join(SHOTS_DIR, f"{name}.svg")
    await asyncio.to_thread(_write_svg, path, app.export_screenshot(title=title))
    print(f"  {path}")


def _write_svg(path: str, svg: str) -> None:
    with open(path, "w") as svg_file:
        svg_file.write(svg)


async def run(shots: list[str]) -> None:
    from textual.widgets import DataTable

    from lazy_kafka.__main__ import LazyKafka
    from lazy_kafka.widgets.topic import TopicPanel

    app = LazyKafka()
    async with app.run_test(size=SIZE) as pilot:
        topic_panel = app.screen.query_one(TopicPanel)
        topic_table = topic_panel.query_one(DataTable)
        await _wait_rows(pilot, topic_table)

        def on(name: str) -> bool:
            return name in shots or not shots

        # --- topics: browse ------------------------------------------------
        if on("topics"):
            topic_table.action_cursor_down()
            await pilot.pause(0.3)
            await capture(pilot, app, "topics", "lazy-kafka · topics")

        # --- topics: live search highlight ---------------------------------
        if on("topics-search"):
            topic_panel.search_token = "test"
            await pilot.pause(0.5)
            await capture(pilot, app, "topics-search", "lazy-kafka · search")

        # --- topics: applied filter ----------------------------------------
        if on("topics-filtered"):
            topic_panel.filter_token = "test"
            await pilot.pause(0.5)
            await capture(pilot, app, "topics-filtered", "lazy-kafka · filtered")
            topic_panel.filter_token = ""
            topic_panel.search_token = ""
            await pilot.pause(0.5)

        # --- messages: topic details with AVRO decode ----------------------
        if on("messages"):
            row = _handle_name(topic_table) or "test-topic-avro"
            keys = list(topic_panel.subjects.keys())
            topic_table.move_cursor(
                row=next((i for i, k in enumerate(keys) if "avro" in str(k)), 0)
            )
            await pilot.pause(0.3)
            topic_panel.focus()
            await pilot.pause(0.1)
            await pilot.press("enter")
            await pilot.pause(0.5)
            details_table = app.screen.query_one(DataTable)
            await _wait_rows(pilot, details_table)
            row = details_table.coordinate_to_cell_key(
                details_table.cursor_coordinate
            ).row_key
            details_table.action_cursor_down()
            await pilot.pause(2.0)  # schema fetch + AVRO decode of details
            await pilot.press("j")
            await pilot.pause(1.5)
            await capture(pilot, app, "messages", f"lazy-kafka · {row.value} messages")
            await pilot.press("escape")
            await pilot.pause(0.3)

        # --- kafka connect ----------------------------------------------
        if on("kconnect"):
            await pilot.press("l")
            await pilot.pause(0.3)
            connect_table = app.screen.query_one(DataTable)
            await _wait_rows(pilot, connect_table)
            await capture(pilot, app, "kconnect", "lazy-kafka · connect")

        # --- schema registry ----------------------------------------------
        if on("schema-registry"):
            await pilot.press("l")
            await pilot.pause(0.3)
            schema_table = app.screen.query_one(DataTable)
            await _wait_rows(pilot, schema_table)
            await pilot.press("j")
            await pilot.pause(0.5)
            await capture(pilot, app, "schema-registry", "lazy-kafka · schemas")

        # --- logs ---------------------------------------------------------
        if on("logs"):
            await pilot.press("L")
            await pilot.pause(1.0)
            await capture(pilot, app, "logs", "lazy-kafka · logs")
            await pilot.press("d")
            await pilot.pause(0.5)


SHOTS = {
    "topics": "topics table on boot",
    "topics-search": "live search highlight (`/test` typed, nothing filtered)",
    "topics-filtered": "Enter applies the filter to matching rows",
    "messages": "topic messages with parsed AVRO payload in the details panel",
    "kconnect": "kafka connect status table",
    "schema-registry": "schema registry subjects",
    "logs": "in-app log viewer",
}


def main() -> int:
    if "--list" in sys.argv:
        for name, description in SHOTS.items():
            print(f"{name:16s} {description}")
        return 0
    wanted = [a for a in sys.argv[1:] if a in SHOTS]
    unknown = [a for a in sys.argv[1:] if a not in SHOTS]
    if unknown:
        print(f"unknown shots: {unknown}; known: {list(SHOTS)}")
        return 1
    asyncio.run(run(wanted))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
