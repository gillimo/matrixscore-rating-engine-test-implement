## How To Operate (v5) - Gemini Agent (Updated 2025-12-17)

This document provides instructions for operating the Teambuilder CLI tool, focusing on its core functionalities and new behavioral rules.

---

### General Guidelines

*   **Documentation Reference Order:** Before working, it's recommended to consult these documents in order: `PERMISSIONS.md` (authoritative), this file, `V2_TICKETS.md`, `BUG_LOG.md`, `SYSTEM_NOTES.md`, `DEMO_MODE.md`, `PROJECT_VISION.md`, `METRICS.md` (for scoring formulas), and `SIGNING_OFF.md` (for personal context).
*   **Scope Rule:** Scope is the code in git plus any tickets added by the current coding agent. New tickets created during your run must be captured in `BUG_LOG.md` and/or `V2_TICKETS.md` and are automatically in-scope.
*   **Logging & Bug Hygiene:**
    *   Always tail recent `logs/*.log` to review previous runs.
    *   Log any new bugs immediately in `BUG_LOG.md` before making code changes.
    *   Track active work in `V2_TICKETS.md`.
    *   Include the current date (YYYY-MM-DD) and your unique handle from `LOGBOOK.md` on any documentation changes. Sign log files with your handle.
*   **Permissions & Logging Footer:** Operations are confined to `OneDrive/Desktop/teambuilder_v5`. All generated log files must include the current permissions footer from `PERMISSIONS.md`:  
    `Permissions: full access to OneDrive/Desktop/teambuilder_v5 granted by user on 2025-12-17.`  
    Sign logs with your handle (e.g., `Signed: Gemini (Agent, 2025-12-17)`).
*   **Avoid Blocking Operations:** Continue primary tasks unless an issue is a massive stoppage.

---

### Core CLI Commands & Flow

The CLI operates interactively, allowing users to add Pokémon, manage the team, and finalize the process.

*   **Adding Pokémon:** Type a Pokémon's name (and optional level cap) at the prompt:
    `Add Pokemon (name [level]) or 'next' to move to moves: <pokemon_name> [level_cap]`
*   **Team Management Commands:**
    *   `next`: Moves to the move suggestion phase. If the team is not full (6 members), it will auto-fill remaining slots first.
    *   `done`: Exits the application.
    *   `drop <pokemon_name>`: Removes the specified Pokémon from the current team.
    *   `finalize`: Triggers the auto-filling of the team to 6 members (if not already full), processes move suggestions, and attempts to launch the Tkinter GUI.
*   **Team Full Status:** If the team reaches 6 members, a message will indicate: "Team is full (6/6). Type 'next' to lock typings or 'drop <name>' to swap someone."

---

### New Autofill Rules & Behavior (v5)

These rules apply when the team is auto-filled (e.g., via `finalize` or implicitly before the move suggestion phase).

*   **Primary Logic:** The autofill process now prioritizes identifying the highest defensive delta typing for the current team. Once this typing is found, the algorithm then selects the best offensive Pokémon from the available candidates *within that specific typing*. This ensures each addition strengthens both defense and offense strategically.
*   **"Low-Stat Win" Explanation:** If the autofill algorithm selects a Pokémon with a lower Base Stat Total (BST) over a higher-stat alternative, a notification will be printed to the console explaining the strategic reason for the choice (e.g., due to superior offensive gain, defensive improvement, or overall performance).
*   **Suppressed Suggestions:** During automatic autofill or `finalize` flows, the verbose "Top offense lifts" and "Top overall lifts" suggestions are now suppressed in the output to improve processing speed and log clarity. These detailed suggestions are still shown during interactive team building.

---

### Demo & Testing

To run the tool in a non-interactive, test-like mode, execute the `team_cli_v5.py` script directly with commands as arguments or piped input.

*   **Official Autofill Test (empty team):**
    `echo "finalize" | python team_cli_v5.py`
    *   This command tests the autofill logic by starting with an empty team and invoking `finalize` directly.
*   **Direct Command Execution (pre-seeded team):**
    `python team_cli_v5.py "gengar finalize"`
    *   This will add Gengar, then automatically `finalize` the team.
*   **Piped Input for Interactive Mode Simulation:**
    `echo "gengar\nnext\ndone" | python team_cli_v5.py`
    *   This simulates typing "gengar", then "next", then "done".
*   **Finalize Harness (see output directly):**
    `python test_harness.py` streams a single `finalize` command into `team_cli_v5.py` and shows stdout. Override input with `--commands "gengar\nfinalize"` or `--input-file demo_input.txt`. Uses the current interpreter by default.
*   **Log Review:** Always review the latest `logs/run_*.log` file to check the output of any run. Single-mon runs should auto-fill to 6 before moves.

---

### Tkinter GUI (Wheel) Overview

The application includes an optional Tkinter-based graphical user interface for visualizing the team.

*   **Launch:** The GUI automatically launches if `tk_team_builder.py` is present and the team is finalized.
*   **Features:** Displays team cards with Pokémon sprites and types, per-category move carousels, and an "I don't have this" button to cycle through move options. It provides a summary of team metrics (defense, offense, shared, balance index, type diversity, move-type breadth, exposures, base stats). Metrics and coverage summaries are visible on the left pane.

---

### Scoring Metrics Overview

For detailed formulas and explanations of how defensive, offensive, shared, and overall scores are calculated, refer to `METRICS.md`. This includes specifics on self-weak handling (e.g., ghost/dragon counting at 25% when STAB is present).

---

Signed: Gemini (Agent, 2025-12-17)
