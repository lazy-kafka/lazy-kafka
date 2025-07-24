# SPDX-FileCopyrightText: 2024-present Timon Viola <44016238+timonviola@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations
import contextlib
import importlib.metadata

# import logging

# from textual.logging import TextualHandler


#logging.basicConfig(
#    level=logging.NOTSET,
#    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',  # Custom format
#    handlers=None,
#)
# from lazy_kafka.__main__ import app

__version__ = "0.1.0"

with contextlib.suppress(importlib.metadata.PackageNotFoundError):
    __version__ = importlib.metadata.version("lazy-kafka")

