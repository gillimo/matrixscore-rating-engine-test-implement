## System Notes (Updated by Gemini Agent, 2025-12-17)

-   **Interpreter:** Python 3.9 at `C:\Users\gilli\AppData\Local\Programs\Python\Python39\python.exe` (primary for demos/tests). Use full path (python alias may be disabled).
-   **File Versioning:** The current main development script is `team_cli_dlc.py`. The previous `team_cli_v3.py` has been archived to `archive/team_cli_v3.py.archive`.
-   **Type chart:** cached locally at `type_chart_cache.json` to avoid PokeAPI timeouts.
-   **Shell:** PowerShell on Windows.
-   **PowerShell I/O:** for input redirection use piping (`Get-Content file | command`) instead of bash-style `< file`.
-   **Filesystem:** work inside OneDrive Desktop (`teambuilder dlc`); `PERMISSIONS.md` is the authoritative inherited-permissions-source; include footer (`Permissions: full access to OneDrive/Desktop/teambuilder dlc granted by user on 2025-12-17.`) on logs.
-   **Network:** enabled (current session); PokeAPI typically reachable (required at runtime).
-   **Naming/Signature:** operators must choose a unique handle in `LOGBOOK.md` and sign note/log files with that handle (recent handles: Atlas, Helix, Orion, Comet, Gemini).
-   **Logging expectation:** disk logging TODO (see tickets); until then, manual logs must carry the permissions footer and Atlas signature. Known issue: some runs hang or stay empty (BUG-2025-12-13-014); prefer inline Python execution and ensure flush/close.
-   **Access practice:** only issue visible PowerShell commands against `OneDrive/Desktop/teambuilder dlc`; no hidden processes or destructive commands; network used only when running the demo (PokeAPI).

---

### Agent Operational Notes (Gemini, 2025-12-17):

*   **File Modification Reliability:** The `replace` tool has proven unreliable for complex, multi-line modifications or when previous changes might subtly alter the target `old_string` (e.g., whitespace, line endings, prior `builtins.globals()` insertions). This has led to repeated failures to correctly apply changes.
*   **Best Practice for Large Changes:** For significant code overhauls or when modifying complex functions, the most robust approach is to compose the *entire* modified file content and use a single `write_file` operation. This minimizes the risk of `replace` failures due to context drift.
*   **Debugging Strategy:** When encountering persistent `IndentationError`s or `NameError`s in new code, re-confirm the entire file content and ensure all necessary `import` statements and function definitions are present and correctly scoped, especially when dealing with name shadowing (e.g., `globals()` vs. `builtins.globals()`).
*   **Function Tracing:** The `TRACE_FUNCTIONS` flag in `team_cli_dlc.py` has been enabled, and a custom `trace_call` decorator, along with an `_apply_tracing` mechanism, has been implemented to provide detailed logging of function entries, exits, arguments, return values, and durations. This is intended to aid in understanding complex execution flows and debugging scoring logic.

Context handoff: see `SIGNING_OFF.md` for personal summaries; keep tickets/bugs as the canonical work list.

Signed: Gemini (Agent, 2025-12-17)


