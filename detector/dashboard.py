import psutil
from flask import Flask, render_template_string
import baseline
import blocker
import detector

app = Flask(__name__)

# Simple HTML template with 3-second auto-refresh
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>HNG Cloud Monitor</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body {
            font-family: sans-serif;
            background: #1a1a1a;
            color: #eee;
            padding: 20px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        .card {
            background: #333;
            padding: 15px;
            border-radius: 8px;
            border-left: 5px solid #007bff;
        }
        .banned {
            border-left-color: #dc3545;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            text-align: left;
            padding: 8px;
            border-bottom: 1px solid #444;
        }
    </style>
</head>
<body>
    <h1>🛡️ HNG Cloud Anomaly Detection Dashboard</h1>
    <div class="grid">
        <div class="card">
            <h3>Global Traffic</h3>
            <p>Current: <b>{{ global_rate }}</b> req/s</p>
            <p>Baseline: {{ baseline_mean }} req/s</p>
        </div>
        <div class="card">
            <h3>System Health</h3>
            <p>CPU: {{ cpu }}%</p>
            <p>Memory: {{ mem }}%</p>
        </div>
        <div class="card">
            <h3>Detector Uptime</h3>
            <p>{{ uptime }} seconds</p>
        </div>
    </div>

    <div class="card banned" style="margin-top: 20px;">
        <h3>🚫 Currently Banned IPs</h3>
        <table>
            <tr>
                <th>IP Address</th>
                <th>Rate</th>
                <th>Ban Level</th>
                <th>Time Remaining</th>
            </tr>
            {% for ip, data in banned_ips.items() %}
            <tr>
                <td>{{ ip }}</td>
                <td>{{ data.rate | round(2) }}</td>
                <td>{{ data.level }}</td>
                <td>Active</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

START_TIME = 0


@app.route('/')
def index():
    global_rate = len(detector.global_window) / 60.0
    return render_template_string(
        DASHBOARD_HTML,
        global_rate=round(global_rate, 2),
        baseline_mean=round(baseline.effective_mean, 2),
        cpu=psutil.cpu_percent(),
        mem=psutil.virtual_memory().percent,
        banned_ips=blocker.banned_ips,
        uptime=int(psutil.time.time() - START_TIME)
    )


def start_dashboard(config):
    global START_TIME
    START_TIME = psutil.time.time()
    port = config.get('dashboard', {}).get('port', 5000)
    # Host 0.0.0.0 is required to be accessible outside the container
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
