## User Priority (2025-12-17)

The primary focus remains on improving the **autorating and scoring algorithms** and ensuring the autofill process aligns with strategic team building. The user is satisfied with the *suggestions* being generated, but not with the *handling* of those suggestions.

### Current High-Level Priorities:

1.  **Refactor Autofill Logic (BUG-2025-12-15-039):**
    *   Implement the refined autofill strategy: **first identify the best defensive typing to add, and then find the best offensive Pokémon from candidates within that specific typing's pool.**
    *   Ensure this new logic is uniformly applied across both `autofill` and `finalize` flows.
    *   Remove development shortcuts (e.g., `[:3]` candidate limits) to ensure a comprehensive search for optimal Pokémon.
2.  **Enhance User Explainability:**
    *   Implement **"Low-Stat Win" Notifications (BUG-2025-12-15-035):** Provide clear, concise explanations when a seemingly "weaker" (lower BST) Pokémon is chosen over a higher-stat alternative, detailing the strategic reasons (e.g., superior type coverage, defensive improvement).
3.  **Optimize Autopick Performance & Clarity:**
    *   **Suppress Suggestions in Finalize Flow:** During non-interactive autofill/finalize, suppress verbose "Top offense lifts" and "Top overall lifts" output to improve efficiency and log clarity.
4.  **Overall Score Tuning:**
    *   Adjust the `overall_score` calculation to:
        *   Punish **5 points per overlapping weakness**.
        *   Result in a perfect score of **100** if both `best_defensive_delta` and `best_offense_gap` are 0 (meaning no further improvement is possible) AND there are no overlapping weaknesses.
5.  **"Critical Moves" Concept (Future Work):** Develop a system to identify and prioritize 1-3 "critical" offensive move types for each Pokémon (e.g., STAB, super-effective coverage against key team weaknesses) to better guide move selection and enhance offensive strategy. This requires further definition and implementation.

---

## Scoring System Health (2025-12-17)

User has noted that the current scoring system produces scores that are **"LOW and aggressive"**. This indicates that the scoring formulas may be too punitive and not accurately reflecting the true quality of a team.

This area **"will need work"**.

Future work should focus on:
1.  Resolving the critical scoring flaws identified in `CURRENT_STATE_2025-12-17.md` (e.g., defense score of 0, incorrect offensive deltas).
2.  Re-evaluating the scoring formulas to provide more intuitive and useful scores that are not overly punitive.