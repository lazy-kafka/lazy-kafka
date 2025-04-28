from __future__ import annotations
import time

def get_current_time() -> str:
    return time.strftime("%H:%M:%S", time.localtime())

