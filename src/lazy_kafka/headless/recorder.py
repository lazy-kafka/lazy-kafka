"""Asciinema recorder for generating asciinema JSON format."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lazy_kafka.headless.driver import DriverOutput, CapturedFrame


@dataclass
class AsciinemaFrame:
    """A frame in asciinema format."""
    time: float
    type: str = "output"
    text: str = ""


@dataclass
class AsciinemaRecorder:
    """Records terminal output in asciinema JSON format."""
    
    frames: list[AsciinemaFrame] = field(default_factory=list)
    width: int = 80
    height: int = 24
    command: str = "lazy-kafka --headless"
    title: str = "lazy-kafka demo"
    start_time: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Initialize the recorder with header info."""
        # Add header as first frame
        header = {
            "width": self.width,
            "height": self.height,
            "timestamp": int(self.start_time),
            "title": self.title,
            "command": self.command,
            "env": {
                "SHELL": "/bin/bash",
                "TERM": "xterm-256color"
            }
        }
        # Store header separately for final output
        self._header = header
    
    def add_frame(self, text: str, timestamp: float | None = None) -> None:
        """Add a new frame with terminal output.
        
        Args:
            text: The terminal output text
            timestamp: Optional timestamp (uses current time if not provided)
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate time relative to start
        relative_time = timestamp - self.start_time
        
        self.frames.append(AsciinemaFrame(
            time=relative_time,
            type="output",
            text=text
        ))
    
    def add_frames_from_output(self, output: DriverOutput) -> None:
        """Add frames from driver output.
        
        Args:
            output: The driver output containing captured frames
        """
        for frame in output.frames:
            self.add_frame(frame.text, frame.timestamp)
        
        # Also add ANSI output as frames
        for ansi_text in output.ansi_output:
            self.add_frame(ansi_text)
    
    def to_json(self, pretty: bool = True) -> str:
        """Convert the recording to asciinema JSON format.
        
        Args:
            pretty: Whether to format the JSON with indentation
        
        Returns:
            JSON string in asciinema format
        """
        asciinema_data = {
            "version": 2,
            "width": self.width,
            "height": self.height,
            "timestamp": int(self.start_time),
            "time": int(time.time()),
            "title": self.title,
            "env": self._header.get("env", {}),
            "theme": {
                "fg": "#ffffff",
                "bg": "#000000",
                "cursor": {
                    "fg": "#000000",
                    "bg": "#ffffff"
                },
                "palette": [
                    "#000000", "#cc0000", "#4e9a06", "#c4a000",
                    "#3465a4", "#75507b", "#06989a", "#d3d7cf",
                    "#555753", "#ef2929", "#8ae234", "#fce94f",
                    "#729fcf", "#ad7fa8", "#34e2e2", "#eeeeec"
                ]
            },
            "stdout": []
        }
        
        # Add frames to stdout
        for frame in self.frames:
            asciinema_data["stdout"].append({
                "time": frame.time,
                "type": frame.type,
                "text": frame.text
            })
        
        if pretty:
            return json.dumps(asciinema_data, indent=2)
        return json.dumps(asciinema_data)
    
    def save(self, path: Path) -> None:
        """Save the recording to a file.
        
        Args:
            path: Path to save the recording
        """
        # Ensure the file has .cast extension
        if not path.name.endswith('.cast'):
            path = path.with_suffix('.cast')
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        
    @classmethod
    def from_driver_output(
        cls, 
        output: DriverOutput, 
        command: str = "lazy-kafka --headless",
        title: str = "lazy-kafka demo",
        width: int = 80,
        height: int = 24
    ) -> AsciinemaRecorder:
        """Create a recorder from driver output.
        
        Args:
            output: The driver output to convert
            command: The command being recorded
            title: Title for the recording
            width: Terminal width
            height: Terminal height
        
        Returns:
            A new AsciinemaRecorder instance
        """
        recorder = cls(
            command=command,
            title=title,
            width=width,
            height=height
        )
        recorder.add_frames_from_output(output)
        return recorder
