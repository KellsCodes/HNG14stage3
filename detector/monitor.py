import json
import time
import os
from detector import check_traffic


def tail_log(config):
    """Continuously tails and parses the Nginx access log file."""
    log_file_path = config.get('log_path', '/var/log/nginx/hng-access.log')

    # Wait for the file to be created by Nginx if it doesn't exist yet
    while not os.path.exists(log_file_path):
        print(f"Waiting for log file at {log_file_path} to be created...")
        time.sleep(2)

    print(f"Tailing log file: {log_file_path}")

    with open(log_file_path, 'r') as f:
        # Move the cursor to the end of the file so we only read new lines
        f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)  # Wait briefly for new data
                continue

            try:
                # Parse the JSON log line
                log_data = json.loads(line.strip())

                # Pass the parsed data to the detection engine
                check_traffic(log_data, config)

            except json.JSONDecodeError:
                # Skip lines that aren't valid JSON (e.g., partial writes)
                continue
