## 🛡️ HNG Cloud Anomaly Detection Engine
A real-time DevSecOps daemon that monitors Nginx logs, calculates traffic baselines, and automatically mitigates DDoS/Anomaly attacks using iptables and Slack notifications.

## Live Deployment Details
* **Server IP**: 20.86.137.57
* **Metrics Dashboard URL**: http://nextcloudmonitor.duckdns.org/
* **GitHub Repository**: https://github.com/KellsCodes/HNG14stage3.git
* **Blog post**: https://dev.to/ifeanyi_nworji/building-my-first-smart-firewall-how-i-stopped-ddos-attacks-with-python-1bp8

## Technical Documentation
### Language Choice & Why
The detection engine is written in **python 3.11**

* **Efficiency**: Python's native `collections` library provides the hyper-efficient deque data structure for high-speed log parsing

* **System Integration**: It allows native execution of Linux kernel commands via the `subprocess` module to manipulate iptables dynamically.

* **Rapid UI Development**: Python allowed for a quick, lightweight dashboard build using `Flask` without loading bulky frontend frameworks.

## Sliding Window Implementation

* **Structure**: The engine uses a `collections.deque` object to store timestamps of incoming traffic.

* **Eviction Logic**: For every incoming log line, the system checks the oldest timestamps at the left of the deque (`global_window[0]`). If that timestamp is oldeer than 60 seconds (`now - 60`), it is popped off (`popleft()`).

* **Benefit**: This guarantees an accurate Requests Per Second (`RPS`) tracking over exactly the last 60 seconds while keeping memory footprint incredibly small and constant.

## Baseline Computation

* **Window Size**: 1,800 seconds (30 minutes).

* **Recalculation Interval**: A background thread wakes up every 60 seconds to recalculate metrics.

* **Math Logic**: It calculates the `Mean` and `Standard Deviation` of the requests received in each exact second over the 30-minute block.

* **Floor Values**: Tp prevent "division by zero" errors and over-sensitivity during zero-traffic idle periods, a hard mathematical floor of `0.1` is enforced for both the effective mean and standard deviation.

## Setup Instructions (Fresh VPS to Running Stack)
Follow these steps to replicate this setup on a fresh `Ubuntu 24.04 LTS` VPS or other ubuntu distribution.

### Prerequisites
Ensure ports 80 and 443 are open on your VPS firewall (Network Security Group).

**Step 1: Install Docker & Docker Compose**
Run the official Docker installation script:
```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://docker.com -o get-docker.sh
sudo sh get-docker.sh
```

**Step 2: Clone the Project**
```bash
git clone https://github.com/KellsCodes/HNG14stage3.git
cd HNG14stage3
```

**Step 3: Configure Slack Alerts**: 
Copy .env.example and modify it by pasting your generated Slack Webhook/Trigger URL:
```bash
cp .env.example .env
nano .env
```

Update the URL:
```yaml
slack:
    webhook_url: "https://slack.com..."
```

**Step 4: Launch the Stack**
Run the orchestration command with administrative privileges to allow the detector to access the host's firewall:
```bash
sudo docker compose up --build -d
```

**Step 5: Verification**
* Visit your server IP to see Nextcloud
* Visit your domain/subdomain to view the Live Metrics Dashboard.

### Pro-Tip for Verification
To ensure all your files are fully accounted for, your repository structure should mimic this:
```bash
├── README.md
├── detector
│   ├── Dockerfile
│   ├── baseline.py
│   ├── blocker.py
│   ├── config.yml
│   ├── dashboard.py
│   ├── detector.py
│   ├── main.py
│   ├── monitor.py
│   ├── notifier.py
│   ├── requirements.txt
│   └── unbanner.py
├── docker-compose.yml
├── docs
├── nginx
│   └── nginx.conf
└── screenshots
    ├── Audit-log.png
    ├── Ban-slack.png
    ├── Baseline-graph.png
    ├── Global-alert-slack.png
    ├── Iptables-banned.png
    ├── Tool-runnin.png
    └── Unban-slack.png
```