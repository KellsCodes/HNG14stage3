import requests


def send_slack_alert(
    condition,
    rate,
    baseline,
    config,
    ip=None,
    duration=None
):
    """Sends a structured alert using the webhook URL from the config."""
    # Read the URL directly from the config dictionary
    webhook_url = config.get('slack', {}).get('webhook_url')

    if not webhook_url:
        print(
            f"Slack skipped: No Webhook URL found in config. [{condition}]")
        return

    # Build the message block
    message = f"*Anomaly Detected: {condition}*\n"
    if ip:
        message += f"*Target IP:* `{ip}`\n"

    message += (
        f"*Current Rate:* `{rate:.2f} req/s` | "
        f"*Baseline:* `{baseline:.2f} req/s`\n"
    )

    if duration:
        message += f"*Action:* IP Banned for `{duration}`\n"
    elif condition == "Unbanned":
        message = f"*IP Unbanned:* `{ip}` - Access restored."

    payload = {"text": message}

    try:
        response = requests.post(webhook_url, json=payload, timeout=5)
        if response.status_code not in [200, 201, 202]:
            print(f"Slack Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Failed to send Slack alert: {e}")
