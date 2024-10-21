# SPDX-FileCopyrightText: 2024-present Timon Viola <44016238+timonviola@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import logging

from textual.logging import TextualHandler

logging.basicConfig(level="NOTSET", handlers=[TextualHandler()])
from .__main__ import app

