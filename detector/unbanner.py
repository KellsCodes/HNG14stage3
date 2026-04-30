import time
import subprocess
import blocker
from notifier import send_slack_alert


def run_unbanner_scheduler(config):
    """Loop that checks for IPs ready to be unbanned."""
    schedule = config.get('unban_schedule', [600, 1800, 7200])

    while True:
        time.sleep(10)  # Check every 10 seconds
        now = time.time()
        to_unban = []

        # 1. Identify IPs whose ban duration has expired
        for ip, data in blocker.banned_ips.items():
            if data['level'] >= len(schedule):
                continue  # Permanent ban

            if now - data['start_time'] >= data['duration']:
                to_unban.append(ip)

        # 2. Process Unbans
        for ip in to_unban:
            unban_ip(ip, blocker.banned_ips[ip], config)


def unban_ip(ip, data, config):
    """Removes the iptables rule and updates the ban level."""
    try:
        # Remove the rule from the host
        subprocess.run(["iptables", "-D", "DOCKER-USER", "-s",
                       ip, "-j", "DROP"], check=True)

        # Log the action
        print(f"[UNBAN] {ip} | Level {data['level']} completed")
        blocker.log_audit("UNBAN", ip, "Duration Expired", 0, 0, "0s")

        # Notify Slack
        send_slack_alert(condition="Unbanned", rate=0, baseline=0, ip=ip)

        # Prepare for next potential ban (backoff)
        data['level'] += 1
        # If not yet permanent, we keep them in memory but marked as
        # "not active"
        # In a production environment, we'd clear this, but for now,
        # we need to track the 'level' for the next time they attack.
        del blocker.banned_ips[ip]

    except subprocess.CalledProcessError:
        print(f"Failed to unban {ip}")
