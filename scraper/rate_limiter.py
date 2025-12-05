"""Polite rate limiter to avoid hammering the source site."""
import random
import time


def polite_delay() -> None:
    """Sleep for at least 5 seconds with a small random jitter."""
    time.sleep(5 + random.uniform(0.2, 1.0))
