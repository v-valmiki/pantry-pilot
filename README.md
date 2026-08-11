# Pantrypilot

A personal food-ordering assistant. Chat with it about your schedule or mood,
it proposes an order, you confirm, it places it. Ordering goes through
DoorDash's `dd-cli` (https://github.com/doordash-oss/doordash-cli).

The longer-term intention for this project is visual awareness of what's
actually in storage, low-cost cameras covering the **fridge, the pantry,
and general food storage**, not just the fridge. See "Vision extension"
below.

## Run it now (mock mode, no dd-cli needed)
```bash
python3 pantrypilot.py
```
`DRY_RUN` defaults to `true`, so every search and checkout is simulated
using a small fake catalog in `dd_client.py`. Nothing real is ever charged
in this mode. This works on any machine, no Mac required.

### Example session
```
You: I'm exhausted, don't want to cook
Here's what I'd order:
  - Pad Thai (Thai Basil) — $14.50
  - Chicken Burrito Bowl (Border Grill) — $12.75
  Estimated total: $27.25
  [simulated order, DRY_RUN is on, nothing real will be charged]

Confirm this order? (yes/no): yes

Ordered. {'order_id': 'DRYRUN-a1b2c3d4', 'status': 'simulated', 'total': 27.25}
```

## Going live: on-demand Scaleway Mac, not always-on
dd-cli requires macOS on Apple Silicon. Rather than keeping a Mac running
24/7, the plan is to rent a Scaleway Mac mini (Apple Silicon, billed hourly
with a 24-hour minimum lease) and spin it up only when you actually want to
use Pantrypilot, then shut it down after.

Rough workflow once you have dd-cli waitlist access:

1. **Boot the instance** from the Scaleway console (or CLI) when you want
   Pantrypilot available. Takes a few minutes to come up.
2. **SSH or VNC in**, run `dd-cli login` once per instance if it's a fresh
   boot (check whether Scaleway preserves state between stops, or if login
   needs repeating, confirm this once you're actually renting).
3. **Set the environment variable and run:**
   ```bash
   export DRY_RUN=false
   python3 pantrypilot.py
   ```
4. **Pair Codex mobile** (see below) so you can chat with it from your
   phone while the instance is up.
5. **Shut the instance down** from the Scaleway console when you're done
   for the day. Billing stops accruing (beyond the 24-hour minimum on
   whichever lease you're in).

**Before your first live order**, run `dd-cli --help` on the actual
instance and check the cart-add and checkout commands in `dd_client.py`.
The `search` command is confirmed correct against dd-cli's public README
(`dd-cli search --query "..."`), but cart and checkout syntax aren't
publicly documented, they're a reasonable guess, not a verified match.
Fix those two calls against the real `--help` output before relying on them.

## Codex mobile pairing (once live on the Scaleway instance)
1. Open the Codex Mac app on the running instance, select "Codex mobile,"
   and scan the QR code from the ChatGPT mobile app.
2. Message the session from your phone the same way you'd type into this
   shell. Codex reads `AGENTS.md` for the same rules this script hardcodes.
3. Pairing is tied to that specific running session, expect to re-pair
   after you shut the instance down and boot a new one, unless Scaleway
   preserves instance state across stops (worth confirming once you're
   actually testing this).

## Vision extension (planned, not built)
Intention: low-cost cameras on the fridge, the pantry, and general food
storage areas, triggered by a door/motion sensor, feeding a captured image
to a multimodal LLM for a plain-language read of what's there and what's
running low. That output would join `preferences.json` as context Pantrypilot
reads before proposing an order, so it can suggest using what's on hand or
restocking specific items, instead of ordering blind. Not part of this
build yet.

## Files
- `pantrypilot.py` — runnable demo shell (heuristic decision logic, stands
  in for Codex's own reasoning until wired up to a real session).
- `dd_client.py` — dd-cli wrapper, dry-run/live modes, order logging.
- `AGENTS.md` — persona and rules for a real Codex session to read,
  including the vision-extension intention.
- `preferences.json` — your standing food preferences, edit directly.
- `order_log.jsonl` — append-only log of every proposed/placed order.