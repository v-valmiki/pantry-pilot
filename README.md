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

## Going live: owned Mac mini, not a cloud rental
dd-cli requires macOS on Apple Silicon. Cloud Apple Silicon rentals (Scaleway
and similar) turned out not to fit an on-demand use pattern: due to Apple's
own licensing terms, there's no pause/stop state, you're billed continuously
for as long as the machine is assigned to your account, there's a mandatory
24-hour minimum before you're even allowed to delete it, and deleting means
a full reinstall next time, not a resume. That's the opposite of "turn it on
when I need it."

An owned Mac mini (new or used) fits much better: put it to sleep when idle,
wake it instantly, no per-hour cost while it's off, and everything, dd-cli
login, Codex config, stays exactly as you left it.

Rough workflow once you have dd-cli waitlist access and a Mac:

1. **Run `dd-cli login` once.** This only needs to happen again if you wipe
   the machine.
2. **Set the environment variable and run:**
   ```bash
   export DRY_RUN=false
   python3 pantrypilot.py
   ```
3. **Pair Codex mobile** (see below) so you can chat with it from your
   phone while the Mac is awake.
4. **Let the Mac sleep** when you're not using it. Wake it (locally, or via
   Wake on Demand on the same network) when you want Pantrypilot available
   again, no reinstall, no re-pairing needed.

**Before your first live order**, run `dd-cli --help` on the actual
machine and check the cart-add and checkout commands in `dd_client.py`.
The `search` command is confirmed correct against dd-cli's public README
(`dd-cli search --query "..."`), but cart and checkout syntax aren't
publicly documented, they're a reasonable guess, not a verified match.
Fix those two calls against the real `--help` output before relying on them.

## Codex mobile pairing (once live on your Mac)
1. Open the Codex Mac app, select "Codex mobile," and scan the QR code
   from the ChatGPT mobile app.
2. Message the session from your phone the same way you'd type into this
   shell. Codex reads `AGENTS.md` for the same rules this script hardcodes.
3. Because the Mac itself persists (it's not deleted and recreated), this
   pairing should survive sleep/wake cycles. Re-pair only if you reinstall
   macOS or reset the Codex app.

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
