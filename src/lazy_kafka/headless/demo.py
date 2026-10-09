"""Demo script parsing and execution for headless mode."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions supported in demo scripts."""
    KEY = "key"
    LOG = "log"
    WAIT = "wait"
    SCREENSHOT = "screenshot"


@dataclass
class DemoAction:
    """A single action in a demo script."""
    action_type: ActionType
    data: dict[str, Any] = field(default_factory=dict)
    delay_ms: int = 0
    
    @classmethod
    def from_dict(cls, action_dict: dict[str, Any]) -> DemoAction:
        """Parse a demo action from a dictionary."""
        if "key" in action_dict:
            return cls(
                action_type=ActionType.KEY,
                data={"key": action_dict["key"]},
                delay_ms=action_dict.get("delay", 0)
            )
        elif "log" in action_dict:
            return cls(
                action_type=ActionType.LOG,
                data={
                    "message": action_dict["log"],
                    "level": action_dict.get("level", "INFO")
                },
                delay_ms=action_dict.get("delay", 0)
            )
        elif "wait" in action_dict:
            return cls(
                action_type=ActionType.WAIT,
                data={"duration_ms": action_dict["wait"]},
                delay_ms=action_dict.get("delay", 0)
            )
        elif "screenshot" in action_dict:
            return cls(
                action_type=ActionType.SCREENSHOT,
                data={"name": action_dict.get("screenshot", "screenshot")},
                delay_ms=action_dict.get("delay", 0)
            )
        else:
            raise ValueError(f"Unknown action type in: {action_dict}")
    
    def to_dict(self) -> dict[str, Any]:
        """Convert action to dictionary."""
        result = {}
        if self.action_type == ActionType.KEY:
            result["key"] = self.data["key"]
        elif self.action_type == ActionType.LOG:
            result["log"] = self.data["message"]
            result["level"] = self.data["level"]
        elif self.action_type == ActionType.WAIT:
            result["wait"] = self.data["duration_ms"]
        elif self.action_type == ActionType.SCREENSHOT:
            result["screenshot"] = self.data["name"]
        
        if self.delay_ms > 0:
            result["delay"] = self.delay_ms
        
        return result


@dataclass
class DemoScript:
    """A complete demo script with actions and metadata."""
    actions: list[DemoAction] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_json(cls, json_str: str | Path) -> DemoScript:
        """Load a demo script from a JSON string or file path."""
        if isinstance(json_str, Path):
            with open(json_str, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = json.loads(json_str)
        
        actions = []
        for action_dict in data.get("actions", []):
            actions.append(DemoAction.from_dict(action_dict))
        
        return cls(
            actions=actions,
            metadata=data.get("metadata", {})
        )
    
    def to_json(self, pretty: bool = True) -> str:
        """Convert demo script to JSON string."""
        data = {
            "metadata": self.metadata,
            "actions": [action.to_dict() for action in self.actions]
        }
        if pretty:
            return json.dumps(data, indent=2)
        return json.dumps(data)
    
    def save(self, path: Path) -> None:
        """Save demo script to a file."""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    def get_key_actions(self) -> list[DemoAction]:
        """Get all key press actions."""
        return [a for a in self.actions if a.action_type == ActionType.KEY]
    
    def get_log_actions(self) -> list[DemoAction]:
        """Get all log actions."""
        return [a for a in self.actions if a.action_type == ActionType.LOG]
    
    def get_total_duration_ms(self) -> int:
        """Calculate total duration of the script in milliseconds."""
        return sum(a.delay_ms for a in self.actions)
