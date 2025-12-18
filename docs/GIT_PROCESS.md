## Git Workflow (v5)

Ground rules
- One commit per signoff unless told otherwise; keep messages scoped and clear (`docs:`, `fix:`, `feat:`, `chore:`).
- Run `git status` before/after work; do not leave uncommitted changes at signoff.
- Do not use force operations (`reset --hard`, `push --force`) without explicit user approval.

Daily flow
1. `git status` (and `git log --oneline -5` if needed) to confirm base.
2. Work in small steps; re-check `git status`.
3. Inspect diffs with `git diff` (unstaged) and `git diff --cached` (staged).
4. Commit: `git add <paths>` then `git commit -m "<type>: <summary>"`.
5. Optional tag: `git tag -a v5-YYYYMMDD -m "Snapshot after <feature>"`.
6. Rollback only with approval: single file `git restore <file>`; whole repo resets require user ok.

Backups
- Existing: `team_cli_v3.py.bak` (2025-12-15), `team_cli_v5.py.bak` (2025-12-17). Keep .bak for major versions; .gitignore excludes them.

Notes
- Initial repository commit: 2025-12-17.
- If logs/caches are large, prefer updating `.gitignore` over deletion.
- Scope rule: code in git + tickets added by the current agent are in-scope; keep docs aligned when committing.

Signed: Codex (2025-12-17)
