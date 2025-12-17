Here are 5 more suggestions for log additions, deletions, or edits to improve UX:

---

**Suggestion 1 (Edit/Consolidate): Consolidate "Added X via Y" messages after autofill**

*   **Problem:** The autofill prints each "Added X via Y" message twice. Once immediately after the addition, and then again in a block after autofill is complete. This is redundant and makes the log longer than necessary.
*   **Proposed Edit:** After the `autofill_team` function completes, instead of re-printing each "Added X via Y" message individually, print a single summary line that states "Autofill complete. Added X Pokémon: [List of Pokémon names]."
*   **Why it's critical:** Reduces redundancy, making the log more concise and easier to scan. The individual adds are already logged as they happen; a final summary is more user-friendly.

---

**Suggestion 2 (Addition): Explicitly state *why* a Pokémon was considered "weakest" for drop**

*   **Problem:** The log currently states `Weakest (candidate drop): yveltal`. It's not immediately clear to the user *why* Yveltal is the weakest. Is it lowest defensive impact, lowest overall score, highest overlap?
*   **Proposed Addition:** When identifying the "weakest" member for an upgrade pass, briefly state the metric used for this determination.
*   **Placement:** Immediately after `Weakest (candidate drop): X`.
*   **Example:**
    ```
    Weakest (candidate drop): yveltal
    [Upgrade Logic] Identified as weakest due to lowest defensive impact (-16).
    ```
*   **Why it's critical:** Increases transparency and helps the user understand the algorithm's decisions during a crucial stage of team optimization.

---

**Suggestion 3 (Edit/Consolidate): Streamline individual Pokémon move suggestions in "Draft results" section**

*   **Problem:** The `Draft results` section currently lists just the move names. The detailed move breakdown (Role, Alignment, Weaknesses, Coverage Priority, Suggested moves, Top by category) for *each* Pokémon appears much later in "Final team summary", making the `Draft results` feel sparse and requiring the user to scroll to connect the dots.
*   **Proposed Edit:** For the "Draft results" section, instead of just `Xerneas: terrain-pulse`, add a very concise summary, like `Xerneas (Role: Balanced, Key Move: Terrain Pulse)`. The full details would remain in the "Final team summary." This partially covers Log Addition 4 from the previous set, but focuses on the "Draft results" section.
*   **Placement:** Modify the print statement in the "Draft results" loop.
*   **Example:**
    ```
    === Draft results ===
    Xerneas: terrain-pulse (Role: Balanced, Key Move: Terrain Pulse)
    Mewtwo: psychic-noise (Role: Sweeper, Key Move: Psychic Noise)
    ```
*   **Why it's critical:** Provides immediate, high-level context for each Pokémon's assigned moves without overwhelming the user, improving readability and linking sections.

---

**Suggestion 4 (Addition): Acknowledge unused candidates in `get_best_defensive_candidates`**

*   **Problem:** `get_best_defensive_candidates` might identify a theoretically "best" typing, but then `fetch_single_type_candidates` or `fetch_dual_candidates` returns an empty list because no actual Pokémon fit that typing or are already on the team. The log currently prints `Best defensive typing found: X/Y (delta +Z). Considering candidates.` but doesn't explicitly state if suitable Pokémon were *actually found*.
*   **Proposed Addition:** If `defensive_names` (the list of actual Pokémon candidates) is empty, add a small note in the log.
*   **Placement:** Within `autofill_team`, after the `[Autofill Logic]` line, if `defensive_names` is empty.
*   **Example:**
    ```
    [Autofill Logic] Iteration 1: Best defensive typing found: Rock/Ground (delta +30). Considering candidates.
    [Autofill Note] No available Pokémon found for Rock/Ground typing not already on team.
    ```
*   **Why it's critical:** Avoids confusion and accurately reflects the state of candidate discovery. A user might wonder why a "best typing" didn't lead to a pick.

---

**Suggestion 5 (Deletion): Remove the `Typing-based Overall Preview` line in `coverage_report` when `show_suggestions` is False**

*   **Problem:** When `show_suggestions` is `False` (e.g., in `do_finalize`), the line `Typing-based Overall Preview (moves not yet factored): 56/100 (def 76, off 80, stack 3.0, delta 89.0)` is still printed. This preview is useful when suggestions are being made, but in a final summary, the "Overall Rating" from the detailed breakdown is the definitive metric. This line becomes redundant or could be confusing.
*   **Proposed Deletion:** Make the `report_lines.append` for "Typing-based Overall Preview" conditional on `show_suggestions`.
*   **Why it's critical:** Streamlines the final output, removing a preview metric that is superseded by the actual final score. This ensures the log focuses on final results when appropriate.