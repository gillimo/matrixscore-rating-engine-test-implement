## Demo Mode (2025-12-17)

- Command: `echo "finalize" | python team_cli_dlc.py`
- Behavior: starts empty, autofills to 6, then moves/GUI if available.
- Logging: writes to `logs/demo_<timestamp>.log`; include footer `Permissions: full access to OneDrive/Desktop/teambuilder dlc granted by user on 2025-12-17.` and sign with your handle.
- Known issues: runs can hang or truncate logs (BUG-2025-12-13-014); scoring anomalies remain (defense=0, offense delta inflation).
- Tips: avoid interrupts; prefer simple pipes over here-strings; tail latest log after run.

Signed: Codex (2025-12-17)


