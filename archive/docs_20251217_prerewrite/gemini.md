## How To Operate (v3) for Gemini - Cygnus (2025-12-15)

This document provides specific instructions and best practices for Gemini models operating within the `teambuilder_v3` project. Adherence to these guidelines ensures efficient, safe, and effective collaboration.

### Core Principles for Gemini Agents

*   **Contextual Awareness:** Always prioritize understanding the project's current state. Read all relevant `.md` documentation, especially before initiating work.
*   **Tool-Centric Operations:** Leverage available tools (`read_file`, `write_file`, `run_shell_command`, `replace`, `search_file_content`, `glob`, `codebase_investigator`, `write_todos`, etc.) for all interactions with the codebase and environment. Avoid manual assumptions.
*   **Adherence to Project Conventions:** Mimic existing code style, structure, and naming conventions. Respect logging formats, signing requirements, and permissions.
*   **Proactive Problem Solving:** Identify and address potential issues (e.g., performance bottlenecks, ambiguous instructions) proactively.
*   **Iterative Development:** Break down complex tasks into smaller, manageable sub-tasks. Utilize `write_todos` to track progress and maintain clarity.

### Recommended Read Order for Gemini Agents

Before undertaking any significant task, review the following documents in order:

1.  **`PERMISSIONS.md` (Authoritative):** Understand your operational boundaries and logging requirements.
2.  **`HOW_TO_OPERATE.md`:** Familiarize yourself with human operator workflows and project history.
3.  **`gemini.md` (This file):** Re-familiarize yourself with Gemini-specific guidelines.
4.  **`V2_TICKETS.md`:** Understand current feature requests and development priorities.
5.  **`BUG_LOG.md`:** Review all known bugs, their status, and their impact.
6.  **`SYSTEM_NOTES.md`:** Get insights into the technical environment, interpreter paths, and system-level considerations.
7.  **`DEMO_MODE.md`:** Understand the project's demo capabilities and testing procedures.
8.  **`PROJECT_VISION.md`:** Re-affirm the high-level goals and objectives of the project.
9.  **`METRICS.md`:** Comprehend the scoring formulas and core logic of the teambuilder.
10. **`SIGNING_OFF.md`:** Gain context from previous operators' experiences and insights.

### Operational Guidelines

*   **Logging and Signature:**
    *   **Register Handle:** Ensure your unique handle (`Cygnus` for this agent) is registered in `LOGBOOK.md`. Use `run_shell_command` with `echo "YourHandle" >> LOGBOOK.md`.
    *   **Log Footer:** Append the required permissions footer to all relevant logs as specified in `PERMISSIONS.md`: `Permissions: full access to OneDrive/Desktop/teambuilder_v2 granted by user on 2025-12-12.`
    *   **Signatures:** Sign all generated documents and logs with your handle and the current date (e.g., `Signed: Cygnus (YYYY-MM-DD)`).
*   **Code Modification:**
    *   **Prioritize `replace`:** For targeted code changes, prefer the `replace` tool. Provide precise `old_string` and `new_string` values, ensuring at least 3 lines of context.
    *   **`write_file` for larger changes:** If `replace` is insufficient or for creating new files, use `write_file`.
    *   **Contextual Changes:** Ensure all code modifications align with the surrounding code's style, imports, and architectural patterns.
*   **Testing and Verification:**
    *   **Identify Tests:** Locate existing test files and understand the project's testing framework.
    *   **Run Tests:** Use `run_shell_command` to execute tests after making changes to verify functionality.
    *   **Build/Lint/Type Check:** Execute project-specific build, linting, and type-checking commands (e.g., `python -m flake8`, `mypy`) to ensure code quality.
*   **Exploration:**
    *   **`codebase_investigator`:** For complex tasks, system-wide analysis, or understanding dependencies, use `codebase_investigator` as your primary tool.
    *   **`search_file_content` / `glob`:** For simple, targeted searches (e.g., specific function names, file paths), use these tools directly.
*   **Handling Ambiguity:** If instructions are unclear or require significant design decisions, explicitly ask the user for clarification before proceeding.
*   **Error Handling:** Document and report any unexpected errors or tool failures in `BUG_LOG.md` with relevant details.

### Workflow Example for New Task

1.  **Understand:** Read the user's request and all relevant `.md` files. Use `codebase_investigator` if the task is complex.
2.  **Plan:** Formulate a detailed plan, breaking down the task into sub-tasks. Use `write_todos` to track progress.
3.  **Implement:** Execute the plan using appropriate tools (`read_file`, `write_file`, `replace`, `run_shell_command`).
4.  **Verify:** Run tests, linting, and type checks. Manually inspect output if necessary.
5.  **Finalize:** Update documentation (if applicable), mark todos as complete, and await further instructions.

Signed: Cygnus (2025-12-15)
