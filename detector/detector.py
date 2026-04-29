import time
from collections import deque, defaultdict
import baseline
from blocker import ban_ip
from notifier import send_slack_alert

# Sliding windows
ip_windows = defaultdict(lambda: deque())
# New: Track 4xx/5xx errors per IP
ip_error_windows = defaultdict(lambda: deque())
global_window = deque()


def check_traffic(log_data, config):
    """Main detection logic including Error Surge tracking."""
    ip = log_data.get('source_ip')
    status = int(log_data.get('status', 200))
    now = time.time()

    # Update Windows
    global_window.append(now)
    baseline.record_request()
    ip_windows[ip].append(now)

    # Track Errors (4xx and 5xx)
    if 400 <= status <= 599:
        ip_error_windows[ip].append(now)

    # Slide all windows (60s limit)
    window_limit = now - config['windows']['sliding_window']

    while global_window and global_window[0] < window_limit:
        global_window.popleft()
    while ip_windows[ip] and ip_windows[ip][0] < window_limit:
        ip_windows[ip].popleft()
    while ip_error_windows[ip] and ip_error_windows[ip][0] < window_limit:
        ip_error_windows[ip].popleft()

    # Calculate Rates
    current_ip_rate = len(ip_windows[ip]) / 60.0
    current_error_rate = len(ip_error_windows[ip]) / 60.0
    mean = baseline.effective_mean
    stddev = baseline.effective_stddev

    # Error Surge Logic: Tighten thresholds if errors are high
    z_limit = config['thresholds']['z_score_limit']
    # If error rate is high, we lower the Z-score limit to be more sensitive
    if current_error_rate > (mean * 0.1 *
                             config['thresholds']['error_multiplier']):
        z_limit /= 2.0

    # Anomaly Detection
    z_score = (current_ip_rate - mean) / stddev if stddev > 0 else 0

    if z_score > z_limit or \
       current_ip_rate > (mean * config['thresholds']['baseline_multiplier']):
        ban_ip(ip, current_ip_rate, mean, "IP Anomaly/Error Surge")

    elif len(global_window) / 60.0 > (
            mean * config['thresholds']['baseline_multiplier']):
        send_slack_alert("Global Traffic Spike", len(global_window)/60.0, mean)
