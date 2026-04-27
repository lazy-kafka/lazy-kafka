"""Built-in plugin modules.

Importing this package triggers registration of every bundled plugin.
Each submodule calls :func:`lazy_kafka.plugin.register` at import time.

Adding a new built-in plugin is a two-step change:

1. Create ``lazy_kafka/plugins/<your_plugin>/__init__.py`` that defines
   a class satisfying :class:`lazy_kafka.plugin.Plugin` and calls
   ``register(YourPlugin())``.
2. Add the module to the list below.
"""

from __future__ import annotations

from lazy_kafka.plugins import core_kafka, kafka_connect, schema_registry

__all__ = ["core_kafka", "kafka_connect", "schema_registry"]
