## Operator Logbook
- 2025-12-12: Handle registered and signed: Atlas.
- 2025-12-12: Handle registered and signed: Helix.
- 2025-12-13: Handle registered and signed: Orion.
- 2025-12-13: Handle registered and signed: Comet.
- 2025-12-13: Handle registered and signed: Vega.
- 2025-12-14: Handle registered and signed: Codex.
- 2025-12-14: Codex: retuned overall ranking to reward bulk/stat totals and defense, stronger low-BST penalty; ran smoke demos (`logs/run_20251214_131154.log`, `logs/run_20251214_131738.log`).
- 2025-12-14: Codex: tightened offense scoring (harder 100s), harsher SE-penalty, offense list sorts by offense first; new demo `logs/run_20251214_205006.log`.
- 2025-12-14: Codex: switched offense score to headroom-style (100 - best remaining offensive gain); added offense gap detection for autofill; demo `logs/run_20251214_210230.log`.
- 2025-12-15: Handle registered and signed: Codex.
- 2025-12-15: Handle registered and signed: Nova.
- 2025-12-15: Handle registered and signed: Quill.
- 2025-12-15: Handle registered and signed: Cygnus.
- 2025-12-15: Gemini: Resolved RecursionError by refactoring candidate scoring in `fetch_single_type_candidates` and `fetch_dual_candidates`. Implemented `pokemon_defense_stat_total` and integrated it into `pick_defensive_addition` for improved defensive weighting. Refined `overall_score` formula to be `100 - (best_defensive_delta + best_offense_gap)` based on user feedback.
- 2025-12-15: Handle registered and signed: Stardust.
- 2025-12-17: Gemini: Performed a full audit of the `teambuilder dlc` project. Identified critical bugs in scoring algorithms and the automated test harness. Documented user's primary focus: improving the autorating and the handling of suggestions, rather than the suggestions themselves. Created a new `CURRENT_STATE_2025-12-17.md` document with the full audit findings. Updated `PRIORITIES.md` to reflect the user's focus.
- 2025-12-17: Orchestrator: Implemented `--gemini-test` flag in `team_cli_v3.py` with a 15-second timeout to automatically "finalize" input for automated testing. Updated `test_harness.py` to utilize this flag and remove the redundant `--demo` flag.
- 2025-12-17: Codex: Reviewed the teambuilder dlc project context and signed off in the logbook after confirming the current state.
- 2025-12-17: Codex (Git/bookkeeping): Read LOGBOOK and HALL_OF_FAME; proceeding to triage BUG_LOG and update ticket status.
- 2025-12-17: Codex (Git/bookkeeping): Rewrote documentation set to current DLC scope; archived pre-rewrite docs in `archive/docs_20251217_prerewrite/`.
- 2025-12-29: Handle registered and signed: Beacon.
- 2025-12-29: Handle registered and signed: Quasar.
- 2025-12-29: Codex: tightened overall rating by applying a defense-score floor penalty when defense < 85.
- 2025-12-29: Codex: fixed NameError in pick_offense_addition by restoring synthetic_cover default.
- 2025-12-29: Codex: enforced move draft blueprints (STAB/coverage/utility per role) before final move list.
- 2025-12-29: Codex: limited defense stack overlap penalty to exposed types only.
- 2026-01-04: Handle registered and signed: Aster.
- 2026-01-04: Aster: normalized ZA form entries for type cache; added 6/6 drop+upgrade prompt; enforced unique draft moves; added move rarity weighting; tests: py_compile, test_harness finalize (timeout).
- 2026-01-04: Aster: moved move rarity ranker into `move_rarity.py` and cached rarity stats in `move_rarity_cache.json`.



