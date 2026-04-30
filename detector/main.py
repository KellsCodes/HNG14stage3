import threading
import yaml
from monitor import tail_log
from baseline import run_baseline_calculator
from unbanner import run_unbanner_scheduler
from dashboard import start_dashboard


def load_config():
    """Loads the YAML configuration file"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)


def main():
    print("Starting HNG Cloud Anomaly Detection Engine...")

    # Load configuration
    config = load_config()

    # Start the Baseline Calculator in a background thread
    print("Starting rolling baseline calculator...")
    baseline_thread = threading.Thread(
        target=run_baseline_calculator, args=(config,))
    baseline_thread.daemon = True
    baseline_thread.start()

    # Start the Auto-Unbanner in a background thread
    print("Starting auto-unban scheduler...")
    unban_thread = threading.Thread(
        target=run_unbanner_scheduler, args=(config,))
    unban_thread.daemon = True
    unban_thread.start()

    # Start the Web Dashboard UI in a background thread
    print("Starting live metrics dashboard...")
    dashboard_thread = threading.Thread(
        target=start_dashboard, args=(config,))
    dashboard_thread.daemon = True
    dashboard_thread.start()

    # Start the main log monitoring loop (Runs in the main thread)
    print("Monitoring Nginx access logs...")
    tail_log(config)


if __name__ == "__main__":
    main()
