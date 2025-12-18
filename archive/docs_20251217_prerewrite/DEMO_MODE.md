# Demo Mode (2025-12-17) - Gemini Agent
- Run: `echo "finalize" | python team_cli_v5.py`
- Behavior: Starts with an empty team and invokes the autofill logic via the `finalize` command. The team will be auto-filled to 6 members.
- Self-weak handling: ghost/dragon self-weakness counts as 25% if the mon has STAB of that type; move suggester will ensure such mons carry their self-type STAB.
- Logging: auto-writes to `logs/demo_<timestamp>.log`; each log must include footer `Permissions: full access to OneDrive/Desktop/teambuilder_v5 granted by user on 2025-12-12.` and be signed `Gemini`.
- Known issues: demo still requires a clean, uninterrupted run to validate end-to-end logging; scripted inputs (`next`, `done`) enabled. Runs may hang or truncate logs at startup (BUG-2025-12-13-014); autofill-to-6 remains flaky when defensive delta=0 (Tickets 12/13/17).
Signed: Gemini (Agent, 2025-12-17)
