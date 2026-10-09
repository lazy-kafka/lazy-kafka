"""Headless testing and recording module for lazy-kafka.

This module provides functionality for running lazy-kafka in headless mode
and generating asciinema recordings of terminal sessions.

Features:
- Headless execution of lazy-kafka TUI
- Demo script execution with key presses and delays
- ANSI output capture
- Asciinema JSON format generation
- Support for multiple screens: topics, connectors, registry
"""

from lazy_kafka.headless.demo import DemoScript, DemoAction
from lazy_kafka.headless.driver import HeadlessDriver, DriverOutput, CapturedFrame
from lazy_kafka.headless.recorder import AsciinemaRecorder, AsciinemaFrame

__all__ = [
    "DemoScript",
    "DemoAction", 
    "HeadlessDriver",
    "DriverOutput",
    "CapturedFrame",
    "AsciinemaRecorder",
    "AsciinemaFrame"
]
