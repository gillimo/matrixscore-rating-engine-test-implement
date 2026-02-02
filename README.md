# Teambuilder DLC

Mission Learning Statement
- Mission: Build a Pokemon team builder with defensive/offensive scoring and draft guidance.
- Learning focus: scoring heuristics, move suggestions, and rapid CLI iteration.
- Project start date: 2025-12-17 (inferred from earliest git commit)

Pokemon team builder for Legends Z-A with defensive/offensive scoring, move suggestions, and role balance.

## Features

- Interactive CLI drafting and piped command support
- Defensive/offensive scoring with exposure maps
- Move suggestions and rarity scoring
- Optional Tkinter GUI

## Installation

### Requirements

- Python 3.8+

## Quick Start

```bash
python team_cli_dlc.py
# or

echo "gengar\nfinalize" | python team_cli_dlc.py
```

## Usage

- Run `team_cli_dlc.py` for interactive drafting.
- Pipe commands for automation (e.g., `gengar`, `finalize`).
- See `docs/METRICS.md` for scoring formulas.

## Architecture

```
CLI Input
  |
  v
Team Builder Core (team_cli_dlc.py)
  |
  +--> Move Suggestion (move_suggestor.py)
  |
  +--> Rarity Scoring (move_rarity.py)
  |
  +--> UI (tk_team_builder.py)
  v
Scores + Recommendations
```

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

## Building

No build step required. Run directly with Python.

## Contributing

See `docs/V2_TICKETS.md` for open work items.

## License

No license file is included in this repository.
