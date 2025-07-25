from __future__ import annotations

import sys
import logging
from lazy_kafka.__main__ import LazyKafka


def lazy_kafka():
    if len(sys.argv) <= 1:
        from textual.logging import TextualHandler

        logging.basicConfig(
            level="NOTSET",
            handlers=[TextualHandler()],
        )

        app = LazyKafka()
        app.run()
    else:
        from lazy_kafka.cli import app

        app()
