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

- **FT-2025-12-28-007 | Detail view swap coverage (Completed)**  
  Move per-weakness coverage/swap guidance to the top of each Pokemon detail panel and make the layout more coherent.

- **FT-2025-12-28-008 | Upgrade drop guidance (Completed)**  
  Show a suggested drop target alongside each upgrade idea in the coaching guide.

- **FT-2025-12-28-009 | Reduce stack penalty in overall (Completed)**  
  Lower the stack overlap penalty so stacked-ghost teams rate closer to 92-94.

- **FT-2025-12-28-010 | Delta-0 exposure autopick (Completed)**  
  When no positive defensive deltas exist, prefer safe typings that reduce current exposures.

- **FT-2025-12-28-011 | Delta-0 autopick uses exposure-fix pool (Completed)**  
  Ensure the exposure-fix candidate pool becomes the active choice list for autopick.

- **FT-2025-12-28-012 | Safe typing excludes worsening exposures (Completed)**  
  Filter out safe typing adds that increase gap on already exposed types (e.g., fairy).

- **FT-2025-12-28-013 | Safe list weakness notes (Completed)**  
  Annotate safe typing adds when they increase raw weakness counts.

- **FT-2025-12-28-014 | Defense score 100 only when no exposures (Completed)**  
  Clamp defense score below 100 when any exposed weaknesses remain.

- **FT-2025-12-28-015 | Remove stack penalty from overall (Completed)**  
  Avoid double-penalizing stacks already captured by shared weakness scoring.

- **FT-2025-12-28-016 | Element-filtered add options (Completed)**  
  When user types up to two elements alongside a command or name, append 3 suggested options limited to those element(s), colored by element; suggestions should mirror autopick-style ranking within the filtered pool.

- **FT-2025-12-28-017 | Speed-first type suggestions (Completed)**  
  Rank element-filtered suggestions by base Speed (fastest wins), then defensive delta.

- **FT-2025-12-28-018 | Dual-type filter shows both singles (Completed)**  
  When two elements are provided, show suggestions for each single type and the dual combo.

- **FT-2025-12-28-019 | Type-only input handling (Completed)**  
  Allow entering just element filters to show suggestions without requiring a Pokemon name.

- **FT-2025-12-28-020 | Per-element 3 suggestions (Completed)**  
  Show three suggestions per requested element and color each element section accordingly.

- **FT-2025-12-28-021 | Exclude legendaries from type suggestions (Completed)**  
  Filter legendary/mythic Pokemon from the new element-filtered suggestion lists.

- **FT-2025-12-28-022 | Safe list sorted by added weaknesses (Completed)**  
  Prioritize safe typing adds by fewest new weaknesses, then by score.

- **FT-2025-12-28-023 | Safe list scoring uses strong-type coverage (Completed)**  
  Score safe typing adds by whether their weaknesses are covered by team strong types (resist+immune-weak >= 2), with 100 reserved for weakness sets fully covered by strong types and no new exposures.

- **FT-2025-12-28-024 | Rename main CLI to v6 and update harness (Completed)**  
  Rename `team_cli_v5.py` to `team_cli_v6.py` and point the test harness at the v6 script.

- **FT-2025-12-28-025 | Safe list prioritizes fewest added weaknesses (Completed)**  
  Order safe typing adds by added weakness count first, then by missing strong-type coverage and score.

- **FT-2025-12-28-026 | Update METRICS.md to v6 formulas (Completed)**  
  Document the current defense/offense/shared/overall formulas and penalties in `team_cli_v6.py`.

- **FT-2025-12-28-027 | Defense score A-tier tuning (Completed)**  
  Retune defense weights (weak/resist/immune/exposed/stack) to reduce drift between `typing_score` and `typing_score_display`, keep 100 only when net_exposed==0, and preserve current structure while improving stability across stacked teams.

- **FT-2025-12-28-028 | Offense score A-tier tuning (Completed)**  
  Adjust offense penalty/breadth bonus weights to ensure exposure coverage dominates, while rewarding true breadth without inflating scores; keep structure of `offense_score_with_bonuses`.

- **FT-2025-12-28-029 | Shared weakness score A-tier tuning (Completed)**  
  Rebalance overlap/stack/exposed penalties to avoid double‑punishing teams already penalized in defense, while keeping shared weaknesses a meaningful discriminator.

- **FT-2025-12-28-030 | Defensive delta headroom A-tier tuning (Completed)**  
  Refine `typing_delta` penalty/bonus coefficients to better penalize new exposures/stacking and reward closing exposed types, without changing the formula shape.

- **FT-2025-12-28-031 | Offensive delta headroom A-tier tuning (Completed)**  
  Normalize `compute_best_offense_gain` scaling to prevent inflation and make 0 truly mean no remaining offensive lift; keep current calculation flow.

- **FT-2025-12-28-032 | Overall score A-tier tuning (Completed)**  
  Adjust overall weighting for delta penalties and shared penalty so strong, balanced teams land in expected bands (e.g., 83–85 for the clefable/mawile team, 92–94 for stacked ghosts) without changing structure.

- **FT-2025-12-28-033 | Speed-weighted offense stats (Completed)**  
  Include a stronger speed contribution in offensive stat total (Atk + SpA + 0.75*Speed) used by offense gain scaling.

- **FT-2025-12-28-034 | Speed-forward role classification (Completed)**  
  Increase speed weighting and relax sweeper thresholds in `classify_role` to encourage a bell-curve role mix (1 tank, 1 sweeper, 2 balanced by default).

- **FT-2025-12-28-035 | Safe typing score respects added weaknesses (Completed)**  
  Incorporate added weakness count into the safe typing score so the printed score matches the ordered list.

- **FT-2025-12-28-036 | Dual types always draft STAB for each type (Completed)**  
  Ensure dual-typed mons include at least one STAB move for each type in suggested moves and draft board.

- **FT-2025-12-28-037 | All types always get STAB in draft/suggestions (Completed)**  
  Require at least one STAB for every type on the mon (mono or dual) before role drafting; enforce inclusion in final moves and draft board.

- **FT-2025-12-28-038 | Autopick delta/explanation alignment (Completed)**  
  Use `typing_delta` in defensive candidate selection and fix autopick offense loop so explanations match the formula and top defensive typings.

- **FT-2025-12-28-039 | Perfect team line only when perfect (Completed)**  
  Print the "Perfect team" definition in gold only when the team meets perfect criteria.

- **FT-2025-12-28-040 | Scoring consistency + overall lift (Completed)**  
  Use the same defense score formula for UI and deltas, and reduce overall penalties to target 92–94 for the stacked-ghost Gengar team.

- **FT-2025-12-28-041 | Soften BST penalty for stacked teams (Completed)**  
  Reduce low-BST penalty so strong stacked teams (e.g., Gengar core) can reach the 92–94 target band.

- **FT-2025-12-28-042 | Exposed types listed in breakdown (Completed)**  
  Append explicit exposed type names in the detailed breakdown summary line.

- **FT-2025-12-28-043 | Defensive delta emphasizes exposed closures (Completed)**  
  Tie defensive delta bonuses to exposed types and penalize choices that do not reduce net exposed types.

- **FT-2025-12-28-044 | Console fallback after piped input (Completed)**  
  When stdin hits EOF (piped runs), switch to `CONIN$` so the CLI stays interactive for drops and tweaks.

- **FT-2025-12-28-045 | Remove stack penalty from shared score (Completed)**  
  Drop stack penalty from shared weakness scoring; keep overlap + exposed only.

- **FT-2025-12-28-046 | Defense exposed penalty increased (Completed)**  
  Increase net-exposed penalty in defense score so teams with exposed types don't grade near 100.

- **FT-2025-12-28-047 | Halve role penalty (Completed)**  
  Reduce role balance penalty to half strength for 3+ of a role.

- **FT-2025-12-17-001 | Coverage-aware move selection (In Progress)**  
  Wire exposed/needed types into move selection; rank moves per role for coverage; emit 4 suggested moves + top-12 draft board; enforce positive offensive gain/coverage before delta=0 fallbacks; high-BST fallback last. pick_moves accepts exposed_types/needed_offense; wiring and positive-gain enforcement pending.

- **FT-2025-12-17-002 | GUI slot reroll for unavailable mon (Open)**  
  Click sprite/name in Tk UI to rerun selection for that slot using current team (exclude the current mon) instead of 1:1 swap; covers “drop and rerun whole team” request.

Supporting/legacy work
- Draft board caching: keep move-data refresh to avoid stale/1-move outputs; ensure cached boards update after move fetch.
- Logging/UX cleanup: concise logs, single-fire GUI launch per run, summaries over duplication.

Closed/archived tickets: see `archive/docs_20251217_prerewrite` for prior verbose lists.

Signed: Codex (2025-12-28)
