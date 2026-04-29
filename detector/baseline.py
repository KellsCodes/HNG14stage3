import time
import math
from collections import deque

# Global data stores
# Holds total requests received in each exact second (timestamp: count)
per_second_counts = {}
# Deque to hold the last 1800 counts for the rolling 30-minute baseline
rolling_window = deque(maxlen=1800)

# Current baseline metrics
effective_mean = 1.0
effective_stddev = 0.5


def record_request():
    """Increments the request count for the current second."""
    current_second = int(time.time())
    per_second_counts[current_second] = per_second_counts.get(
        current_second, 0) + 1


def run_baseline_calculator(config):
    """Background thread that recalculates the baseline every 60 seconds."""
    global effective_mean, effective_stddev

    baseline_window = config.get('windows', {}).get('baseline_window', 1800)
    recalc_interval = config.get('windows', {}).get(
        'recalculation_interval', 60)

    while True:
        time.sleep(recalc_interval)

        current_time = int(time.time())
        cutoff_time = current_time - baseline_window

        # 1. Clean up old seconds from memory
        keys_to_remove = [k for k in per_second_counts if k < cutoff_time]
        for k in keys_to_remove:
            del per_second_counts[k]

        # 2. Rebuild the rolling window list
        rolling_window.clear()
        for sec in range(cutoff_time, current_time):
            # If a second had no traffic, count it as 0
            rolling_window.append(per_second_counts.get(sec, 0))

        # 3. Calculate Mean & StdDev manually without math/stats libraries
        n = len(rolling_window)
        if n > 0:
            total_sum = sum(rolling_window)
            mean = total_sum / n

            # Variance calculation
            variance = sum((x - mean) ** 2 for x in rolling_window) / n
            stddev = math.sqrt(variance)

            # Apply calculated baseline
            # (default to a floor to avoid division by zero)
            effective_mean = max(mean, 0.1)
            effective_stddev = max(stddev, 0.1)

            print(
                f"[Baseline Updated] Mean: {effective_mean:.2f} req/s | "
                f"StdDev: {effective_stddev:.2f}"
            )
