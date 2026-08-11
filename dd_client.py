"""
Thin wrapper around dd-cli (https://github.com/doordash-oss/doordash-cli).

When DRY_RUN=true (default), every call is simulated: search returns a small
set of realistic fake results, and checkout never touches a real account.
When DRY_RUN=false, calls shell out to the real `dd-cli` binary. This script
assumes `dd-cli login` has already been run separately; it does not handle
auth.
"""

import json
import os
import subprocess
import time
import uuid
from pathlib import Path

DRY_RUN = os.environ.get("DRY_RUN", "true").lower() != "false"
LOG_PATH = Path(__file__).parent / "order_log.jsonl"

# Small fake catalog used only in dry-run mode, keyed by a rough category.
_MOCK_CATALOG = {
    "takeout": [
        {"name": "Pad Thai", "restaurant": "Thai Basil", "price": 14.50},
        {"name": "Chicken Burrito Bowl", "restaurant": "Border Grill", "price": 12.75},
        {"name": "Margherita Pizza", "restaurant": "Sliceworks", "price": 16.00},
    ],
    "groceries": [
        {"name": "Eggs (dozen)", "restaurant": "Corner Market", "price": 4.50},
        {"name": "Chicken breast (1lb)", "restaurant": "Corner Market", "price": 6.25},
        {"name": "Mixed greens", "restaurant": "Corner Market", "price": 3.75},
    ],
}


def _log(action: str, summary: str, result: str):
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "mode": "dry_run" if DRY_RUN else "live",
        "action": action,
        "summary": summary,
        "result": result,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def search(query: str, category: str = "takeout"):
    """Search for items. In dry-run mode, returns a slice of the mock catalog."""
    if DRY_RUN:
        results = _MOCK_CATALOG.get(category, _MOCK_CATALOG["takeout"])
        _log("search", f"query={query!r} category={category}", f"{len(results)} mock results")
        return results

    # Confirmed against the real dd-cli README: search takes a --query flag,
    # not a positional argument.
    proc = subprocess.run(
        ["dd-cli", "search", "--query", query], capture_output=True, text=True
    )
    _log("search", f"query={query!r}", proc.stdout.strip())
    return proc.stdout


def build_cart(items: list):
    """Return a proposed cart summary (does not add to a real cart yet)."""
    total = sum(item["price"] for item in items)
    cart = {"items": items, "estimated_total": round(total, 2)}
    _log("cart", f"{len(items)} item(s)", f"est. total ${cart['estimated_total']}")
    return cart


def checkout(cart: dict):
    """
    Place the order. Caller is responsible for having already gotten explicit
    user confirmation before calling this — this function does not ask.
    """
    if DRY_RUN:
        order_id = f"DRYRUN-{uuid.uuid4().hex[:8]}"
        _log("checkout", f"{len(cart['items'])} item(s), ${cart['estimated_total']}", order_id)
        return {"order_id": order_id, "status": "simulated", "total": cart["estimated_total"]}

    # UNVERIFIED: dd-cli's public README only documents `search --query`,
    # `order history`, and `--help`. It does not publish exact syntax for
    # adding items to a cart or checking out. The calls below are a
    # reasonable guess at the shape, but run `dd-cli --help` yourself once
    # you have real access and correct these before flipping DRY_RUN off.
    for item in cart["items"]:
        subprocess.run(["dd-cli", "cart", "add", item["name"]], check=True)
    proc = subprocess.run(["dd-cli", "checkout"], capture_output=True, text=True)
    _log("checkout", f"{len(cart['items'])} item(s), ${cart['estimated_total']}", proc.stdout.strip())
    return {"status": "live", "raw_output": proc.stdout}