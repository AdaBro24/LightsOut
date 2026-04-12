import time
import tracemalloc
from typing import Any, Callable, Tuple


def run_with_stats(func: Callable, *args, **kwargs) -> Tuple[Any, float, int]:
    # lightweight helper to run a function and measure time + peak Python memory
    #uses tracemalloc which measures Python allocated memory

    tracemalloc.start()
    try:
        tracemalloc.reset_peak()
    except Exception:
        pass

    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - t0

    try:
        current, peak = tracemalloc.get_traced_memory()
    except Exception:
        current, peak = 0, 0
    finally:
        tracemalloc.stop()

    return result, elapsed, peak
