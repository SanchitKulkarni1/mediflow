from datetime import datetime
from typing import List, Dict

AUDIT_LOG: List[Dict] = []

def log_event(event_type: str, details: dict):
    AUDIT_LOG.append({
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "details": details
    })
