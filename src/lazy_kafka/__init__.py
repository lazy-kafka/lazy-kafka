# SPDX-FileCopyrightText: 2024-present Timon Viola <44016238+timonviola@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s'  # Custom format
)
from lazy_kafka.__main__ import app

__version__ = "0.1.0"
