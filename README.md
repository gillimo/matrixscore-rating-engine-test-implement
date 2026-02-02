# MatrixScore — Full Use-Case Implementation / Rating Engine Test

Mission Learning Statement
- Mission: Implement a MatrixScore rating engine end-to-end, including scoring, suggestions, and evaluation.
- Learning focus: scoring models, heuristic optimization, caching strategies, CLI/GUI workflows.
- Project start date: 2025-12-17 (inferred from earliest git commit)

## Quick Start
```bash
python team_cli_dlc.py
echo "example_entity\nfinalize" | python team_cli_dlc.py
```

## What This Demonstrates
- Weighted scoring and rank aggregation across multiple attributes
- Draft/selection heuristics with guardrails and role balancing
- Cache-backed data pipelines for fast iteration
- CLI + GUI workflows for rapid experimentation

## Project Structure
```
team_cli_dlc.py     # Main CLI (all core logic)
move_suggestor.py   # Suggestion heuristics and role classification
move_rarity.py      # Rarity scoring
tk_team_builder.py  # Tkinter GUI
globals.py          # Shared constants
docs/               # Essential docs only
archive/            # Old docs, don't read unless asked
```

## Key Files
| File | Purpose |
|------|---------|
| team_cli_dlc.py | Main app - scoring, drafting, suggestions |
| move_suggestor.py | pick_moves(), role classification |
| *_cache.json | Runtime caches (large, not for manual edits) |

---
Last updated: 2026-01-11
