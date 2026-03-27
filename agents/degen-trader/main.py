#!/usr/bin/env python3
"""Degen-Trader agent — crypto analytics and alerts."""
import logging
from pathlib import Path
from xander import AgentSession, HiveBroker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def handle_task(message):
    payload = message.payload
    action = payload.get("action")
    symbol = payload.get("symbol")
    if action == "alert" and symbol:
        logging.info(f"Checking price for {symbol}")
        price = 0.00012345  # mock
        if price < 0.0001:
            return {"action": "buy", "symbol": symbol, "price": price, "reason": "low price"}
        else:
            return {"action": "hold", "symbol": symbol, "price": price}
    return {"error": "unknown task"}

def main():
    broker = HiveBroker()
    session = AgentSession(
        agent_id="degen-trader",
        capabilities=["trade:crypto"],
        broker=broker,
        memory_root=Path("./memory")
    )
    session.register(handle_task)
    logging.info("Degen-Trader agent starting...")
    session.start()

if __name__ == "__main__":
    main()
