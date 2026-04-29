import requests
import json


def send_slack_alert(condition, rate, baseline, ip=None, duration=None):
    """Sends a structured alert to the configured Slack webhook."""
    # This would ideally be loaded from config, but we pass it or hardcode
    # for now
    webhook_url = "YOUR_SLACK_WEBHOOK_URL_HERE"

    if webhook_url == "YOUR_SLACK_WEBHOOK_URL_HERE":
        print(
            f"Slack notification skipped: Webhook URL not set. [{condition}]")
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

    payload = {
        "text": message,
        "username": "HNG-Anomaly-Detector",
        "icon_emoji": ":shield:"
    }

    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        if response.status_code != 200:
            print(
                f"Slack API Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to send Slack alert: {e}")
