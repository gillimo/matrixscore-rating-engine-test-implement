Teambuilder v5 — working guide (2025-12-17)
===========================================

You are in `teambuilder_v5`, the active codebase. The current agent’s tickets and changes define scope for this run; anything added by the current agent is in-scope for delivery.

Quick start
- Run autofill/finalize from empty: `echo "finalize" | python team_cli_v5.py`
- Seed then finalize: `python team_cli_v5.py "gengar finalize"`
- Simulate interactive pipe: `echo "gengar\nnext\ndone" | python team_cli_v5.py`
- Harness: `python test_harness.py` (override with `--commands "gengar\nfinalize"` or `--input-file demo_input.txt`)

Doc map (read in order)
- Index: docs/DOCS_INDEX.md (navigation)
- Permissions/handles: docs/PERMISSIONS.md, docs/LOGBOOK.md, docs/agents.md
- Operating guide: docs/HOW_TO_OPERATE.md, docs/SYSTEM_NOTES.md, docs/DEMO_MODE.md
- Current state/priorities: docs/CURRENT_STATE_2025-12-17.md, docs/PRIORITIES.md
- Worklists: docs/BUG_LOG.md, docs/V2_TICKETS.md
- Vision/metrics: docs/PROJECT_VISION.md, docs/METRICS.md
- Process/history: docs/GIT_PROCESS.md, docs/LOG_CHECKLIST.md, docs/SIGNING_OFF.md, docs/HALL_OF_FAME.md, docs/HANDOFF_2025-12-12.md

Scope & workflow facts
- Scope is the code in git plus any tickets added by the current coding agent.
- Use Python 3.9 at `C:\Users\gilli\AppData\Local\Programs\Python\Python39\python.exe` if `python` alias fails.
- Work inside `OneDrive/Desktop/teambuilder_v5`; see docs/PERMISSIONS.md for footer text on logs.
- For logging: tail recent `logs/run_*.log`/`demo_*.log`; ensure flush/close if running harnesses.

If time is short
- Start from docs/PRIORITIES.md and docs/BUG_LOG.md for what matters now.
- Review docs/V2_TICKETS.md for feature scope carried by the current agent.
