"""Main entry point for headless mode."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import textual
from textual.app import App
from textual.driver import Driver
from textual.pilot import Pilot

from lazy_kafka.config import Configuration
from lazy_kafka.headless.demo import DemoScript, ActionType
from lazy_kafka.headless.recorder import AsciinemaRecorder
from lazy_kafka.widgets._logs import LogHandler

_LOGGER = logging.getLogger(__name__)


@dataclass
class FrameData:
    """Data for a captured frame."""
    text: str
    timestamp: float


class HeadlessLazyKafka(App[None]):
    """LazyKafka app configured for headless execution."""
    
    def __init__(self, demo_script: DemoScript | None = None, **kwargs):
        self.demo_script = demo_script
        self._frames: list[FrameData] = []
        self._start_time = time.time()
        self._log_messages: list[dict] = []
        
        # Load configuration
        try:
            self.lazy_kafka_config = Configuration.from_local_config()
            _LOGGER.info("Config loaded successfully")
        except FileNotFoundError:
            _LOGGER.info("Using default config (FileNotFoundError)")
            self.lazy_kafka_config = Configuration()
        except Exception as e:
            _LOGGER.info(f"Using default config: {e}")
            self.lazy_kafka_config = Configuration()
        
        super().__init__(**kwargs)

    def _capture_screen(self) -> None:
        """Capture the current screen content."""
        try:
            screen_text = self.screen_to_text()
            if screen_text:
                self._frames.append(FrameData(
                    text=screen_text,
                    timestamp=time.time()
                ))
        except Exception as e:
            _LOGGER.debug(f"Failed to capture screen: {e}")

    def screen_to_text(self) -> str:
        """Convert current screen to text."""
        try:
            # This is a placeholder - we'll implement proper screen capture
            import io
            from contextlib import redirect_stdout
            
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                self.screen._repaint()
            
            return buffer.getvalue()
        except Exception:
            return f"Screen: {self.screen}"


async def create_pilot_coroutine(pilot: Pilot, demo_script: DemoScript, app: HeadlessLazyKafka) -> None:
    """Auto-pilot coroutine that executes the demo script."""
    _LOGGER.info(f"Starting demo script execution with {len(demo_script.actions)} actions")
    
    for i, action in enumerate(demo_script.actions):
        _LOGGER.debug(f"Executing action {i+1}/{len(demo_script.actions)}: {action}")
        
        if action.action_type == ActionType.KEY:
            key = action.data["key"]
            _LOGGER.debug(f"Pressing key: {key}")
            
            await pilot.press(key)
            
            if action.delay_ms > 0:
                await asyncio.sleep(action.delay_ms / 1000)
                
        elif action.action_type == ActionType.WAIT:
            await asyncio.sleep(action.data["duration_ms"] / 1000)
            
        elif action.action_type == ActionType.LOG:
            _LOGGER.log(
                getattr(logging, action.data["level"], logging.INFO),
                action.data["message"]
            )
            app._log_messages.append({
                "message": action.data["message"],
                "level": action.data["level"],
                "timestamp": time.time()
            })
            if action.delay_ms > 0:
                await asyncio.sleep(action.delay_ms / 1000)
                
        elif action.action_type == ActionType.SCREENSHOT:
            app._capture_screen()
            if action.delay_ms > 0:
                await asyncio.sleep(action.delay_ms / 1000)
        
        # Capture screen after each action
        app._capture_screen()
    
    _LOGGER.info("Demo script execution completed")
    app._capture_screen()
    
    # Exit the app
    _LOGGER.info("Exiting app")
    await pilot.exit(None)  # Exit with no result


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for headless mode."""
    parser = argparse.ArgumentParser(
        description="Run lazy-kafka in headless mode for testing and recording."
    )
    parser.add_argument(
        "--demo-script",
        type=str,
        help="Path to demo script JSON file",
        required=True
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for asciinema recording (should end with .cast)",
        required=True
    )
    parser.add_argument(
        "--width",
        type=int,
        default=80,
        help="Terminal width for headless mode"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=24,
        help="Terminal height for headless mode"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=10,
        help="Frames per second for recording"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="lazy-kafka demo",
        help="Title for the asciinema recording"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    return parser


def run_headless_sync(
    demo_script_path: str,
    output_path: str,
    width: int = 80,
    height: int = 24,
    fps: int = 10,
    title: str = "lazy-kafka demo",
    verbose: bool = False
) -> None:
    """Run lazy-kafka in headless mode and generate asciinema recording."""
    
    # Load demo script
    script_path = Path(demo_script_path)
    if not script_path.exists():
        _LOGGER.error(f"Demo script file not found: {demo_script_path}")
        sys.exit(1)
    
    demo_script = DemoScript.from_json(script_path)
    _LOGGER.info(f"Loaded demo script with {len(demo_script.actions)} actions")
    
    _LOGGER.info("Creating HeadlessLazyKafka app")
    # Create the app with headless driver
    app = HeadlessLazyKafka(
        demo_script=demo_script,
    )
    _LOGGER.info("HeadlessLazyKafka app created successfully")
    
    # Create auto-pilot coroutine
    async def pilot_main(pilot: Pilot) -> None:
        await create_pilot_coroutine(pilot, demo_script, app)
    
    # Run the app in headless mode with auto-pilot
    try:
        _LOGGER.info("Starting headless execution")
        _LOGGER.info("Running app with headless=True")
        app.run(
            headless=True,
            size=(width, height),
            auto_pilot=pilot_main
        )
        _LOGGER.info("App.run() completed successfully")
    except Exception as e:
        _LOGGER.error(f"Headless execution failed: {e}", exc_info=True)
        raise
    
    # Create asciinema recording from captured frames
    recorder = AsciinemaRecorder(
        command=f"lazy-kafka --headless --demo-script={demo_script_path} --output={output_path}",
        title=title,
        width=width,
        height=height
    )
    
    # Convert frames to asciinema format
    for frame in app._frames:
        recorder.add_frame(frame.text, frame.timestamp)
    
    # Add log messages as comments
    for log_msg in app._log_messages:
        log_frame = f"[LOG {log_msg['level']}] {log_msg['message']}\n"
        recorder.add_frame(log_frame, log_msg['timestamp'])
    
    # Save the recording
    output_file = Path(output_path)
    if not output_file.name.endswith('.cast'):
        output_file = output_file.with_suffix('.cast')
    
    recorder.save(output_file)
    _LOGGER.info(f"Asciinema recording saved to: {output_file}")


def main() -> None:
    """Main entry point for headless mode."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging for the headless execution
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    _LOGGER.info("Starting lazy-kafka in headless mode")
    
    try:
        run_headless_sync(
            demo_script_path=args.demo_script,
            output_path=args.output,
            width=args.width,
            height=args.height,
            fps=args.fps,
            title=args.title,
            verbose=args.verbose
        )
    except Exception as e:
        _LOGGER.error(f"Headless execution failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
