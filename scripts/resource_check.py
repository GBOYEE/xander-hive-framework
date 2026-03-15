#!/usr/bin/env python3
"""
Resource check for HEARTBEAT — outputs a short text summary.
"""
import json, os
from datetime import datetime, timedelta

LOG_PATH = "/root/.openclaw/workspace/memory/system-health.jsonl"
FLAG_PATH = "/root/.openclaw/workspace/memory/.resource_alert.flag"

def main():
    # Read last 5 entries
    try:
        with open(LOG_PATH, "r") as f:
            lines = f.read().strip().splitlines()[-5:]
    except Exception:
        print("Resource log missing.")
        return
    if not lines:
        print("No resource data yet.")
        return
    entries = [json.loads(line) for line in lines]
    avg_mem = sum(e["memory"]["used_gb"] for e in entries) / len(entries)
    avg_cpu = sum(e["cpu"]["percent"] for e in entries) / len(entries)
    flag = os.path.exists(FLAG_PATH)
    print(f"Recent avg: RAM {avg_mem:.2f} GB, CPU {avg_cpu:.1f}% | {'ALERT' if flag else 'OK'}")

if __name__ == "__main__":
    main()
