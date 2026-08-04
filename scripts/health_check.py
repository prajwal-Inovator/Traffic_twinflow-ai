# scripts/health_check.py
import requests
import sys
from typing import Dict, List

SERVICES = [
    ("Backend", "http://localhost:8000/health"),
    ("AI", "http://localhost:8001/health"),
    ("Simulation", "http://localhost:8002/health"),
    ("Notification", "http://localhost:8003/health"),
    ("Data Ingestion", "http://localhost:8004/health"),
]

def check_health() -> Dict[str, bool]:
    results = {}
    for name, url in SERVICES:
        try:
            resp = requests.get(url, timeout=5)
            results[name] = resp.status_code == 200
        except Exception:
            results[name] = False
    return results

if __name__ == "__main__":
    status = check_health()
    all_ok = all(status.values())
    for name, ok in status.items():
        print(f"{name}: {'✓' if ok else '✗'}")
    sys.exit(0 if all_ok else 1)s