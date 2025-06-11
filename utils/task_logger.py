import json
from datetime import datetime

LOG_PATH = "trace_log.jsonl"

def log_event(event: str, details: dict):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event,
        "details": details
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
