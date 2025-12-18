## Metrics (v5) - As Implemented and Proposed (2025-12-17)

**NOTE:** This document reflects the *actual implementation* in the code as of 2025-12-17, incorporating recent discussions and proposed changes.

---

### Defense (`typing_score`)
- **Formula:** `100 - 2.1*total_weak + 1.4*total_resist + 2.2*total_immune + 3.5*exposed_immunes - 12*net_exposed - 14*stack_overlap`
- **Clamping:** `0..100`
- **`stack_overlap`:** `sum(max(0, weak-1) for each attack type)`
- **`net_exposed`:** `sum(1 for c in cov if c["weak"] > (c["resist"] + c["immune"]))`
- **`exposed_immunes`:** `sum(c["immune"] for c in top_exposed)`
- **Notes:** This formula is implemented in `team_cli_v5.py`.

---

### Shared-weakness score (`shared_weak_score`)
- **Formula:** `100 - (overlap * 18) - (stack * 7) - (exposed * 5)`
- **Clamping:** `0..100`
- **`overlap`:** `max(0, max_weak - 1)` where `max_weak` is the highest number of weaknesses to a single type.
- **`stack`:** `sum(max(0, c["weak"] - 1) for c in cov)`
- **`exposed`:** `sum(1 for c in cov if c["weak"] > (c["resist"] + c["immune"]))`
- **Note:** The code has a special case: `if stack == 1: stack = 0`. This formula is implemented in `team_cli_v5.py`.

---

### Offense score (`offense_score_with_bonuses`)
- **Logic:** The score starts at 100 and is reduced by a penalty.
- **Penalty Formula:** `penalty = neutral_gap * 3.5 + se_gap * 4.0 + uncovered_exposed * 6.0 + breadth_penalty + off_stat_penalty`
- **Components:**
    - `neutral_gap`: Number of types not hit at least neutrally.
    - `se_gap`: Number of super-effective hits short of a target (hardcoded to 16).
    - `uncovered_exposed`: Number of the team's defensive weaknesses that are not hit at least neutrally by the team's moves.
    - `breadth_penalty`: Penalty for having fewer than 4 move types.
    - `off_stat_penalty`: Penalty based on the average offensive stats of the team members.
- **Note:** This formula is implemented in `team_cli_v5.py`.

---

### Headroom (delta)
- **Defensive Delta Score:** `100 - best_defensive_delta`
    - `best_defensive_delta` is the highest positive score from the `typing_delta` function when simulating adding new types.
- **Offensive Delta Score:** `100 - best_offense_gap`
    - `best_offense_gap` is a complex `ranked_gain` value calculated in `compute_best_offense_gain`, which includes factors for closing weaknesses, adding new move types, stats, and more.
- **Note:** These headroom calculations are implemented in `team_cli_v5.py`.

---

### Overall score (`overall_score`)
- **Current Formula:** `100 - (best_defensive_delta + best_offense_gap)`
- **Clamping:** `0..100`
- **Proposed Tuning (Future Work):**
    *   **Overlap Penalty:** Introduce a penalty of **5 points per overlapping weakness**. This directly addresses the user's requirement for clear penalties on stacked weaknesses.
    *   **Perfect Score Condition:** The overall score should be 100 if both `best_defensive_delta` and `best_offense_gap` are 0 (meaning no further improvement is possible) AND there are no overlapping weaknesses.
- **Note:** The current formula is implemented in `team_cli_v5.py`. The proposed tuning requires future code modification.

---

### Autofill & Suggestions (`autofill_team`)
- **Current Logic (Implemented in `team_cli_v5.py`):**
    1.  **Defense-First Selection:** The autofill process now prioritizes identifying the highest defensive delta typing for the current team.
    2.  **Offensive Optimization:** Once the best defensive typing is found, the algorithm then selects the best offensive Pokémon from the available candidates *within that specific typing*.
    3.  **Low-Stat Win Explanation:** If a lower-stat Pokémon is chosen over a higher-stat alternative, a notification is printed explaining the strategic reason for the choice.
    4.  **Suppressed Suggestions:** During non-interactive autofill or `finalize` flows, verbose "Top offense lifts" and "Top overall lifts" suggestions are suppressed.
- **Future Refinement (BUG-2025-12-15-039 Clarification):** The "pool" for offensive processing should consist of candidates corresponding to the three highest *overall* defensive deltas available to the current team, not simply the top 3 candidates per individual type/pair. This requires removing current development shortcuts (`[:3]` limits) and implementing more sophisticated candidate selection.

---

### "Critical Moves" Concept (Future Work)

-   **Goal:** The tool should identify 1-3 "critical" offensive move types for each Pokémon. This aims to explain *why* a particular Pokémon is valuable beyond its raw stats or broad typing.
-   **Definition:** A critical move type could be:
    *   A STAB (Same Type Attack Bonus) move.
    *   A move that provides super-effective coverage against a key team weakness (e.g., Staryu's Electric move covering a Flying-type weakness).
    *   A move that fills a crucial offensive niche for the team.
-   **Integration:** This concept needs to be integrated into move selection and potentially into the "low-stat win" explanations.
