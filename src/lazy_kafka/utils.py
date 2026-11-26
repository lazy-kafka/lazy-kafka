from __future__ import annotations

import time
from collections.abc import Sequence
from datetime import datetime


def get_current_time() -> str:
    """Get current time formatted as HH:MM:SS or HH:MM:SS.microseconds."""
    # Get microseconds from time.time()
    current_time = time.time()
    microseconds = int((current_time % 1) * 1_000_000)

    # Format the main time part
    time_str = time.strftime("%H:%M:%S", time.localtime(current_time))

    # Append microseconds if present
    if microseconds > 0:
        return f"{time_str}.{microseconds:06d}"
    return time_str


def timestamp_histogram(timestamps: Sequence[str], num_buckets: int = 100) -> list[int]:
    """Bucket ISO-8601 timestamps into a histogram of counts.

    The first bucket holds the oldest timestamps, the last the newest.

    Args:
        timestamps: ISO-8601 timestamp strings (as produced by
            `lazy_kafka.topic._timestamp_to_str`).
        num_buckets: Number of time buckets to distribute over the
            [oldest, newest] range.

    Returns:
        A list of `num_buckets` counts, oldest first.
    """
    if not timestamps:
        return []
    num_buckets = max(1, num_buckets)
    times = sorted(datetime.fromisoformat(ts) for ts in timestamps)
    histogram = [0] * num_buckets
    span = (times[-1] - times[0]).total_seconds()
    if span == 0:
        # All timestamps are (effectively) identical: one spike
        histogram[0] = len(times)
        return histogram
    for ts in times:
        offset = (ts - times[0]).total_seconds()
        bucket = min(int(offset / span * num_buckets), num_buckets - 1)
        histogram[bucket] += 1
    return histogram
