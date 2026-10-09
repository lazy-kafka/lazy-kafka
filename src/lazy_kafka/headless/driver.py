"""Headless driver for running lazy-kafka in headless mode."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from textual.driver import Driver
from textual._xterm_parser import XTermParser

if TYPE_CHECKING:
    from textual.app import App

_LOGGER = logging.getLogger(__name__)


@dataclass
class CapturedFrame:
    """A single frame of captured terminal output."""
    text: str
    timestamp: float
    width: int
    height: int


@dataclass
class DriverOutput:
    """Complete output from the headless driver."""
    frames: list[CapturedFrame] = field(default_factory=list)
    ansi_output: list[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: float = field(default_factory=time.time)
    
    def add_frame(self, text: str, width: int, height: int) -> None:
        """Add a new frame to the output."""
        self.frames.append(CapturedFrame(
            text=text,
            timestamp=time.time(),
            width=width,
            height=height
        ))
    
    def add_ansi(self, text: str) -> None:
        """Add ANSI output."""
        self.ansi_output.append(text)
    
    def get_duration(self) -> float:
        """Get the total duration of the recording."""
        return self.end_time - self.start_time


class HeadlessDriver(Driver):
    """Custom headless driver that captures ANSI output for asciinema recording."""
    
    def __init__(self, app: App, size: tuple[int, int] = (80, 24)):
        """Initialize the headless driver.
        
        Args:
            app: The Textual app instance
            size: Terminal size as (width, height)
        """
        super().__init__(app, size=size)
        self._output = DriverOutput()
        self._output.start_time = time.time()
        self._parser = XTermParser()
        self._current_screen_content: list[list[str]] = []
        self._size = size
        
    def _capture_current_screen(self) -> None:
        """Capture the current screen content as a frame."""
        # Get the current screen content from the app
        # This is a simplified version - we'll need to integrate with Textual's
        # actual screen rendering
        pass
    
    def _on_ansi_output(self, text: str) -> None:
        """Handle ANSI output from the app."""
        self._output.add_ansi(text)
        # Parse ANSI to understand cursor position and screen state
        self._parser.feed(text)
        
    def write(self, text: str) -> None:
        """Write text to the terminal."""
        self._on_ansi_output(text)
        # Also call parent to ensure proper handling
        super().write(text)
    
    def flush(self) -> None:
        """Flush the output buffer."""
        super().flush()
        # Capture a frame after flush
        self._capture_current_screen()
    
    def get_output(self) -> DriverOutput:
        """Get the captured output."""
        self._output.end_time = time.time()
        return self._output
    
    async def send_key(self, key: str, delay_ms: int = 0) -> None:
        """Send a key press to the app with optional delay.
        
        Args:
            key: The key to send
            delay_ms: Delay before sending in milliseconds
        """
        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000)
        
        # Send key to the app
        _LOGGER.debug(f"Sending key: {key}")
        # We need to inject the key event into the app's message queue
        # This will be handled through the app's post_message method
        
    async def run_demo_script(self, script: DemoScript) -> None:
        """Run a complete demo script.
        
        Args:
            script: The demo script to run
        """
        from lazy_kafka.headless.demo import ActionType
        
        for action in script.actions:
            if action.action_type == ActionType.KEY:
                await self.send_key(action.data["key"], action.delay_ms)
            elif action.action_type == ActionType.WAIT:
                await asyncio.sleep(action.data["duration_ms"] / 1000)
            elif action.action_type == ActionType.LOG:
                _LOGGER.log(
                    getattr(logging, action.data["level"], logging.INFO),
                    action.data["message"]
                )
                if action.delay_ms > 0:
                    await asyncio.sleep(action.delay_ms / 1000)
            elif action.action_type == ActionType.SCREENSHOT:
                # Capture a screenshot (frame)
                self._capture_current_screen()
                if action.delay_ms > 0:
                    await asyncio.sleep(action.delay_ms / 1000)
