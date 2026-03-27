#!/usr/bin/env python3
"""CLI client to send a task to an agent via the broker."""
import argparse
import json
import sys
from pathlib import Path
from xander import HiveBroker

def main():
    parser = argparse.ArgumentParser(description="Send a task to an agent")
    parser.add_argument("--agent", required=True, help="Agent ID to target")
    parser.add_argument("--task", required=True, help="JSON task object")
    parser.add_argument("--redis-url", default="redis://localhost:6379", help="Redis URL")
    args = parser.parse_args()

    try:
        task_data = json.loads(args.task)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)

    broker = HiveBroker(redis_url=args.redis_url)
    broker.connect()
    broker.send_task(args.agent, task_data)
    print(f"Sent task to {args.agent}: {task_data}")
    broker.redis.close()

if __name__ == "__main__":
    main()
