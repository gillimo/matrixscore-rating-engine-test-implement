## Bug Log

Last triage: 2025-12-17 by Codex (Git/bookkeeping).
Updated: Quasar (2025-12-29).

### Active Bugs
- ID: BUG-2025-12-29-008 | Title: Defense score over-penalizes stacked weaknesses even when covered | Status: Fixed (Verified) | Reported By: Quasar | Date: 2025-12-29 | Notes: typing_score now applies stack_overlap only to exposed types.
- ID: BUG-2025-12-29-007 | Title: Drafted moves can violate role blueprint (missing STAB/coverage/utility) | Status: Fixed (Verified) | Reported By: Quasar | Date: 2025-12-29 | Notes: Draft enforcement now backfills missing categories per role before final move list prints.
- ID: BUG-2025-12-29-006 | Title: pick_offense_addition crashes on synthetic_cover NameError | Status: Fixed (Verified) | Reported By: Quasar | Date: 2025-12-29 | Notes: Defined synthetic_cover default after removing synthetic move injection; run no longer crashes on `froslass` add.
- ID: BUG-2025-12-29-002 | Title: Defense score penalizes total weakness counts instead of exposed weaknesses | Status: Fixed (Verified) | Reported By: Codex | Date: 2025-12-29 | Notes: typing_score uses net_exposed/stack only; no total_weak term; verified with Gengar/Sableye coverage check.
- ID: BUG-2025-12-29-003 | Title: Defense score remains too high with multiple exposed weaknesses | Status: Fixed (Verified) | Reported By: Codex | Date: 2025-12-29 | Notes: Increased net_exposed/stack penalties and tightened caps (92/80/65) to push multi-exposure teams down.
- ID: BUG-2025-12-29-004 | Title: Defense display score mismatches core defense score | Status: Fixed (Verified) | Reported By: Codex | Date: 2025-12-29 | Notes: typing_score_display delegates to typing_score; no alternate formula remains.
- ID: BUG-2025-12-29-005 | Title: Suggestions do not reliably close exposed weaknesses | Status: Fixed (Verified) | Reported By: Codex | Date: 2025-12-29 | Notes: Defensive candidate selection and suggestion buckets now prioritize net-exposure reduction when exposures exist.
- ID: BUG-2025-12-29-001 | Title: Defense score stays high with multiple exposed weaknesses | Status: Fixed (Verified) | Reported By: Codex | Date: 2025-12-29 | Notes: Stronger net_exposed/stack penalties and lower caps reduce inflated scores.
- ID: BUG-2025-12-28-004 | Title: Pokemon cache save can crash on MemoryError | Status: Fixed (Verified) | Reported By: Atlas | Date: 2025-12-28 | Notes: persist_fail initialized; KeyError no longer possible after MemoryError.
- ID: BUG-2025-12-28-003 | Title: _top_defensive_typings sort lambda crashes | Status: Fixed (Verified) | Reported By: Atlas | Date: 2025-12-28 | Notes: sort key uses delta + label only; no tuple index crash.
- ID: BUG-2025-12-28-002 | Title: NameError def_score_raw in predict_overall | Status: Fixed (Verified) | Reported By: Codex | Date: 2025-12-28 | Notes: def_score_raw set from typing_score(cov).
- ID: BUG-2025-12-28-001 | Title: Autopick returns none despite safe candidates | Status: Fixed (Verified) | Reported By: Codex | Date: 2025-12-28 | Notes: Defensive fallback always returns a pick when safe adds exist.
- ID: BUG-2025-12-12-002 | Title: Exposed weakness popup sometimes appears twice | Status: Fixed (Verified) | Reported By: Atlas | Date: 2025-12-12 | Notes: No exposed-weakness popup path remains in v6 Tk flow; duplicate trigger no longer present.
- ID: BUG-2025-12-12-005 | Title: Demo log shows defense 34/100 despite "Balanced" banner | Status: Fixed (Verified) | Reported By: Atlas-Delta | Date: 2025-12-12 | Notes: Banner text now reads "No defensive gains left" to avoid implying a high defense score.
- ID: BUG-2025-12-13-014 | Title: Logs remain 0 bytes / runs hang | Status: Fixed (Verified) | Reported By: Orion | Date: 2025-12-13 | Notes: Non-interactive EOF now returns "done"; harness run produced non-empty log (run_20251229_114109.log). Long move fetches can still extend runtime.
- ID: BUG-2025-12-15-023 | Title: Typing delta prefers new exposures (emolga stacking rock) | Status: Fixed (Verified) | Reported By: Nova | Date: 2025-12-15 | Notes: Increased new_exposed/stack penalties and added exposure-first ordering in defensive candidates.
- ID: BUG-2025-12-15-024 | Title: Defensive delta overvalues flying/electric despite stack (emolga vs scizor/skarmory) | Status: Fixed (Verified) | Reported By: Nova | Date: 2025-12-15 | Notes: Stronger stack and exposure penalties make new-exposure picks lose to exposure-closing options.
- ID: BUG-2025-12-15-029 | Title: Confusing Log Output | Status: Fixed (Verified) | Reported By: Cygnus | Date: 2025-12-15 | Notes: Candidate spam moved to VERBOSE-only logging.
- ID: BUG-2025-12-15-034 | Title: Enhance Autofill Selection Explanation | Status: Fixed (Verified) | Reported By: Gemini | Date: 2025-12-15 | Notes: Autofill now prints cleaned gain reasons alongside picks.
- ID: BUG-2025-12-15-035 | Title: Enhance Autofill Selection Explanation (Low-Stat/Diamond in the Rough) | Status: Fixed (Verified) | Reported By: Gemini | Date: 2025-12-15 | Notes: Low-stat win line includes a cleaned rationale for the choice.
- ID: BUG-2025-12-15-036 | Title: Defense Score of 0 in Aurorus/Talonflame Run | Status: Fixed (Verified) | Reported By: Gemini | Date: 2025-12-15 | Notes: Defense floor now bottoms at 5 when exposed types exist; Aurorus/Talonflame scores 5 instead of 0.
- ID: BUG-2025-12-15-037 | Title: Xerneas Offensive Delta of 145 | Status: Fixed (Verified) | Reported By: Gemini | Date: 2025-12-15 | Notes: compute_best_offense_gain capped at 100 for headroom use.
- ID: BUG-2025-12-15-039 | Title: Refactor Autofill: Two-Stage Selection (Defensive First, then Offensive Optimization) | Status: Fixed (Verified) | Reported By: Gemini | Date: 2025-12-15 | Notes: pick_offense_addition selects from the full best-defensive pool (all tied top typings).

### Closed / Moot
- ID: BUG-2025-12-12-003 | Title: PowerShell piping/here-string errors abort demo runs and leave logs empty | Status: Moot | Reported By: Atlas-Delta | Date: 2025-12-12 | Notes: Environment/usage issue; use clean echo/apply_patch workflows instead of brittle here-strings.
- ID: BUG-2025-12-12-008 | Title: PS/inline edits brittle (quoting/escapes) | Status: Moot | Reported By: Atlas-Delta | Date: 2025-12-12 | Notes: Process problem (PowerShell inline editing); standardize on apply_patch/simple scripts on this system.
- ID: BUG-2025-12-12-009 | Title: One-mon run not logging beyond prompt | Status: Closed | Reported By: Atlas-Delta | Date: 2025-12-12 | Notes: Addressed by adding flushes to `log_verbose` and `progress` (Gemini, 2025-12-15); reopen if reproduction surfaces.
- ID: BUG-2025-12-15-030 | Title: Missing GUI Documentation | Status: Closed | Reported By: Cygnus | Date: 2025-12-15 | Notes: Tkinter GUI is now documented in HOW_TO_OPERATE.md (updated 2025-12-17).

### Feature Tickets (tracked in V2_TICKETS)
- ID: FT-2025-12-17-002 (formerly BUG-2025-12-15-038) | Title: GUI reroll a slot when unavailable | Status: Open | Reported By: Gemini | Date: 2025-12-15 | Notes: Click sprite/name in a slot to rerun selection for that slot using the current team (exclude the existing mon) instead of a 1:1 swap; covers the "drop and rerun whole team" request.
- ID: FT-2025-12-17-001 | Title: Coverage-aware move selection | Status: Completed | Reported By: Gemini | Date: 2025-12-17 | Notes: Exposed/needed types wired into move selection; role-ranked suggestions + top-12 draft board emitted; offense adds require positive gain or exposure coverage before delta=0 fallbacks.
- [NEW] UX Cleanup: Rework CLI prints for ship-ready clarity (section headers, concise autofill decisions, single-line gain reasons, trimmed progress noise, aligned final summaries, and consistent coloring). Status: Open.
