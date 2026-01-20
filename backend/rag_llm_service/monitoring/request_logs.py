import time
from datetime import datetime

def log_request(endpoint, payload):
    return {
        "endpoint": endpoint,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload
    }

def log_response(endpoint, duration_ms, status):
    return {
        "endpoint": endpoint,
        "duration_ms": duration_ms,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }
