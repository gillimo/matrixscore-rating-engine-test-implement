## Tickets (v5, 2025-12-17)

Scope: code in git + tickets added by the current agent are in-scope. Log new tickets here (features) and bugs in `BUG_LOG.md`.

Open feature tickets
- **FT-2025-12-28-001 | Show all safe typing adds in CLI output (Completed)**  
  Replace top-3 safest list with full safe-typing add list in the orange summary block.

- **FT-2025-12-28-002 | Autopick always returns a Pokemon (Completed)**  
  Ensure autopick falls back to a defensive pick when offense gating yields no pick.

- **FT-2025-12-28-003 | Drop command prints updated summary/suggestions (Completed)**  
  After `drop <name>`, show defense suggestions and the red team summary.

- **FT-2025-12-28-004 | Fix NameError in predict_overall (Completed)**  
  Define `def_score_raw` before using it to gate defensive delta headroom.

- **FT-2025-12-28-005 | TK "Tell me more" coaching guide (Completed)**  
  Replace the breakdown panel with a coaching-focused guide and rename the button.

- **FT-2025-12-28-006 | Coaching anchors + weakness coverage (Completed)**  
  Add critical anchors to the guide and show who covers each mon's weaknesses in details.

- **FT-2025-12-17-001 | Coverage-aware move selection (In Progress)**  
  Wire exposed/needed types into move selection; rank moves per role for coverage; emit 4 suggested moves + top-12 draft board; enforce positive offensive gain/coverage before delta=0 fallbacks; high-BST fallback last. pick_moves accepts exposed_types/needed_offense; wiring and positive-gain enforcement pending.

- **FT-2025-12-17-002 | GUI slot reroll for unavailable mon (Open)**  
  Click sprite/name in Tk UI to rerun selection for that slot using current team (exclude the current mon) instead of 1:1 swap; covers “drop and rerun whole team” request.

Supporting/legacy work
- Draft board caching: keep move-data refresh to avoid stale/1-move outputs; ensure cached boards update after move fetch.
- Logging/UX cleanup: concise logs, single-fire GUI launch per run, summaries over duplication.

Closed/archived tickets: see `archive/docs_20251217_prerewrite` for prior verbose lists.

Signed: Codex (2025-12-28)
