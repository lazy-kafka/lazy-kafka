from __future__ import annotations

from lazy_kafka.__main__ import LazyKafka


def lazy_kafka():
    app = LazyKafka()
    app.run()
