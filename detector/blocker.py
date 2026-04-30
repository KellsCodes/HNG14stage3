import subprocess
import time
from notifier import send_slack_alert

# Stores banned IPs and their metadata for the Unbanner
# Format: { "1.2.3.4": {"start_time": ts, "level": 0} }
banned_ips = {}


def ban_ip(ip, rate, baseline, condition, config):
    """Executes iptables DROP and records the ban."""
    if ip in banned_ips:
        return  # Already banned

    # Determine ban duration level (0=10m, 1=30m, 2=2h, 3=perm)
    # We will implement the logic to increment this in unbanner.py
    duration_seconds = 600  # Default 10 mins for first offense

    print(
        f"[BAN] {ip} | {condition} | Rate: {rate:.2f} | Base: {baseline:.2f}")

    try:
        # Apply iptables rule on the host
        subprocess.run(
            ["iptables", "-I", "DOCKER-USER", "1", "-s", ip, "-j", "DROP"],
            check=True
        )

        # Store ban info
        banned_ips[ip] = {
            "start_time": time.time(),
            "level": 0,
            "duration": duration_seconds,
            "rate": rate,
            "baseline": baseline
        }

        # Notify Slack
        send_slack_alert(
            condition=condition,
            rate=rate,
            baseline=baseline,
            ip=ip,
            duration=f"{duration_seconds // 60} mins",
            config=config,
        )

        # Audit Log (as required by prompt)
        log_audit("BAN", ip, condition, rate, baseline, f"{duration_seconds}s")

    except subprocess.CalledProcessError as e:
        print(f"Failed to ban {ip}: {e}")


def log_audit(action, ip, condition, rate, baseline, duration):
    """Writes structured log entries to audit.log."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    entry = (
        f"[{timestamp}] ACTION {action} {ip} | "
        f"{condition} | {rate:.2f} | {baseline:.2f} | {duration}\n"
    )
    with open("audit.log", "a") as f:
        f.write(entry)
