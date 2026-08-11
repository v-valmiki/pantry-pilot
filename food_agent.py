"""
Runnable shell for the food agent, demo version.

This is a simple heuristic stand-in for the reasoning Codex will eventually
do from AGENTS.md. It's here so you have something to actually run and see
the confirm-before-checkout flow work end to end, before wiring up a real
LLM session.

Run: python3 pantrypilot.py
"""

import json
import sys
from pathlib import Path

import dd_client

PREFS_PATH = Path(__file__).parent / "preferences.json"

TAKEOUT_SIGNALS = ["tired", "exhausted", "sick", "slammed", "no time", "busy"]
GROCERY_SIGNALS = ["restock", "groceries", "grocery", "fridge is empty", "out of food"]


def load_preferences():
    if PREFS_PATH.exists():
        return json.loads(PREFS_PATH.read_text())
    return {}


def classify(message: str) -> str:
    lowered = message.lower()
    if any(sig in lowered for sig in GROCERY_SIGNALS):
        return "groceries"
    if any(sig in lowered for sig in TAKEOUT_SIGNALS):
        return "takeout"
    return "takeout"  # default assumption for a food-ordering assistant


def propose_cart(category: str):
    results = dd_client.search(query=category, category=category)
    # Demo simplification: propose the first two items from the mock catalog.
    picked = results[:2]
    return dd_client.build_cart(picked)


def print_cart(cart: dict):
    print("\nHere's what I'd order:")
    for item in cart["items"]:
        print(f"  - {item['name']} ({item['restaurant']}) — ${item['price']:.2f}")
    print(f"  Estimated total: ${cart['estimated_total']:.2f}")
    if dd_client.DRY_RUN:
        print("  [simulated order, DRY_RUN is on, nothing real will be charged]")


def main():
    prefs = load_preferences()
    print("Pantrypilot shell (DRY_RUN =", dd_client.DRY_RUN, ")")
    print("Tell me how you're feeling or what you need. Type 'quit' to exit.\n")

    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not message or message.lower() in ("quit", "exit"):
            break

        category = classify(message)
        cart = propose_cart(category)
        print_cart(cart)

        confirm = input("\nConfirm this order? (yes/no): ").strip().lower()
        if confirm in ("y", "yes", "confirm", "go ahead"):
            result = dd_client.checkout(cart)
            print(f"\nOrdered. {result}\n")
        else:
            print("\nOkay, not ordering. Let me know if you want something else.\n")


if __name__ == "__main__":
    main()