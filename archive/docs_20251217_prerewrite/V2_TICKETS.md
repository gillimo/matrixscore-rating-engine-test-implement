## V5 Ticket List (Verbose) - Gemini Agent (Updated 2025-12-17)

Scope note: The code in git plus any tickets added by the current coding agent are in-scope for delivery. New tickets created during a session must be recorded here and in `BUG_LOG.md` (if a bug) immediately.

Ticket closing process (Atlas, 2025-12-12):
- When a ticket is completed, move it to the "Closed Tickets" section with date, summary of proof (run/log/commit), and signature `Atlas`.
- Active list should only contain open items.

1) Early draft-board caching
   - During typing phase, build and cache draft boards per Pokemon (or candidate) so offensive move types and SE hits are known without re-fetching later.
   - Store: move_types, SE_hits (def types it can hit 2x), role, alignment score, and draft_board.

2) Overall-first scoring for candidates & autofill
   - Status: Partially Addressed (Overall formula superseded by new user-defined logic).
   - Details: Overall formula: 100 - (best_defensive_delta + offensive_delta); clamp 0..100.
   - Defense: typing_score.
   - Offense: bonus coverage score (see formulas below) using move_types (cached if no suggested_moves yet).
   - Shared: shared-weak score (heavy penalty for overlapping weaknesses); self-weak ghost/dragon counted at 25% if STAB present.
   - Headroom: best remaining typing delta (single/dual) -> delta score = 100 - best_defensive_delta
   - Autofill: `finalize` fills to 6 by predicted overall uplift; avoid adding overlapping weaknesses.

3) Suggestion output improvements
   - Show offensive projection: count of types hit >= neutral; list types hit super-effectively.
   - Show defensive impact: weak/resist/immune deltas vs current team.
   - Keep 3 results max, best in green, dedupe dual permutations.
   - 2025-12-14 (Codex): V3 offense bucket ranks by offensive score gain (not neutral counts), multiplies gains for closing exposed weaknesses (highest) then adding new elements (second), caps synthetic coverage to top 3 types, and filters candidate lists to final forms (keep typing-change mids) with alignment/coverage weighting; ties still shown. Autofill triages when any score <65 and uses best overall when delta is flat; base stat totals now break ties to avoid baby picks.
   - 2025-12-14 (Codex): Major UI rework requested for move display (boxed cards, clear spacing, per-category flip buttons). Tk layout updated to single-column wide cards with larger wrap and up to 8 moves per category; continue to refine visual spacing and ensure all moves/categories render cleanly; consider alternative stack (e.g., React) if Tk limits persist.

4) End-loop behavior
   - Status: Partially Addressed (Autofill Reliability Improved).
   - Details: Autofill now reliably fills to 6 members. Remaining aspects are user finalization and single swap by name.

5) Logging/UX
   - Concise prints: e.g., "Evaluating fire/flying" overall +12 (hits 14 types, weak -1/resist +2). Avoid spam.

6) Docs update
   - Refresh HOW_TO_OPERATE / PROJECT_VISION / METRICS with the final formulas and behaviors.

---

### New Feature Tickets (Gemini Agent, 2025-12-17)

*   **ID: FT-2025-12-17-001 | Title: Fix Move Selection with Move Profiles and Required Offensive Typings**
    *   **Status:** Open
    *   **Reported By:** Gemini (Agent)
    *   **Notes:** This feature aims to refine the move selection process. It requires defining "move profiles" for Pokémon and identifying "required offensive typings" that support the overall team strategy. The goal is to ensure each monster has access to the moves needed to support the team's offensive plan, going beyond simply "knowing they have access to what's needed." This will involve analyzing team weaknesses and optimizing move choices for critical coverage and STAB.

### Open Tickets Requiring Review

- ID: BUG-2025-12-15-039 | Title: Refactor Autofill: Two-Stage Selection (Defensive First, then Offensive Optimization)
  - Notes: Refactor autofill logic such that `pick_offense_addition` considers only Pokémon derived from the output of defensive selection functions, rather than generating its own pool. This aims to find the best defensive picks first, then optimize their offensive contribution. Clarification: The "pool" for offensive processing should consist of candidates corresponding to the three highest *overall* defensive deltas available to the current team, not simply the top 3 candidates per individual type/pair. The current implementation's `[:3]` limit for `s_opts` and `d_opts` is a development speedup and needs to be replaced with logic to select the top 3 overall defensive delta contributors.
- ID: BUG-2025-12-15-035 | Title: Enhance Autofill Selection Explanation (Low-Stat/Diamond in the Rough)
  - Notes: When autofill selects a Pokémon with significantly lower base stats (or a lower evolutionary stage) compared to other available options, identify and print the critical information that led to its selection (e.g., specific defensive typing, key resistances/immunities, high defensive delta contribution, unique offensive coverage). This aims to clarify "diamond in the rough" picks to the user.
- ID: BUG-2025-12-15-036 | Title: Defense Score of 0 in Aurorus/Talonflame Run
  - Notes: User reported a specific run (Aurorus + Talonflame finalize) resulted in a defense score of 0. This indicates a critical breakdown in the defensive scoring logic for that team composition and needs immediate investigation. Confirmed in run_20251215_195551.log with Overall: 0/100.
- ID: BUG-2025-12-15-037 | Title: Xerneas Offensive Delta of 145
  - Notes: User observed Xerneas having an unusually high offensive delta of 145. This value seems excessive, suggesting a potential miscalculation or an issue in how offensive delta (best_offense_gap) is being computed or presented, indicating a large amount of "left on the table". Confirmed in run_20251215_195551.log with best remaining offensive delta +289.
- ID: BUG-2025-12-15-038 | Title: GUI Feature: Rerate/Replace Pokémon in Slot due to Unavailability
  - Notes: Implement a UI feature that allows users to click on a Pokémon's name in a team slot to trigger a re-evaluation for that specific slot, excluding the currently selected Pokémon from the candidate pool. This addresses situations where a user cannot access a chosen Pokémon.
- ID: FT-2025-12-17-002 | Title: GUI Feature: Click Sprite to Reroll Pokémon
  - Status: Open
  - Reported By: Gemini (Agent)
  - Notes: Implement a feature on the Tkinter UI that allows the user to click on a Pokémon's sprite within a team slot. This action should trigger a re-evaluation and rerolling of that specific Pokémon using the existing autofill logic, considering the current team composition, to suggest an alternative. This allows users to explore different options for a slot without resetting the entire team.
