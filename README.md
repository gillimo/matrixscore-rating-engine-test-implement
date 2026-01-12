# Teambuilder DLC

Pokemon team builder for Legends Z-A with defensive/offensive scoring.

## Quick Start
```bash
python team_cli_dlc.py                    # Interactive mode
echo "gengar\nfinalize" | python team_cli_dlc.py  # Pipe commands
```

## For AI Agents

**Read these first (in order):**
1. `docs/FUNCTION_INDEX.md` - Find any function quickly
2. `docs/METRICS.md` - Scoring formulas
3. `docs/V2_TICKETS.md` - Open work items

**Token-friendly workflow:**
- Use FUNCTION_INDEX.md to locate code - don't grep randomly
- Don't read archived docs unless explicitly needed
- Delete logs after each session
- Archive completed tickets immediately
- Keep /docs minimal

## Project Structure
```
team_cli_dlc.py     # Main CLI (all core logic)
move_suggestor.py   # Move selection/drafting
move_rarity.py      # Rarity scoring
tk_team_builder.py  # Tkinter GUI
globals.py          # Shared constants
docs/               # Essential docs only
archive/            # Old docs, don't read unless asked
```

## Key Files
| File | Purpose |
|------|---------|
| team_cli_dlc.py | Main app - team building, scoring, suggestions |
| move_suggestor.py | pick_moves(), role classification |
| *_cache.json | Runtime caches (don't read, large) |

---
Last updated: 2026-01-11
