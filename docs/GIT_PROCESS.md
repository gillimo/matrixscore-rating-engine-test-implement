## Git Workflow (teambuilder_v5)

This document defines how to use git for this project so changes can be rolled back safely.

### Ground rules
- Use one commit per signoff unless explicitly instructed otherwise.
- Keep commits scoped and descriptive (e.g., `fix: trim autofill trace spam`, `docs: add git workflow`).
- Always run `git status` before and after work; do not leave uncommitted changes at signoff.
- Avoid force operations (`reset --hard`, `push --force`) unless the user explicitly approves.

### Daily flow
1. **Sync / verify base:** `git status` then `git log --oneline -5` to confirm the expected base. If collaborating with remotes, `git pull` before editing.
2. **Work in small steps:** Make changes, then `git status` to review staged vs unstaged.
3. **Inspect diff:** `git diff` (unstaged) and `git diff --cached` (staged) to verify content.
4. **Commit:** `git add <paths>` → `git commit -m "<type>: <summary>"`. Prefer `docs:`/`fix:`/`feat:`/`chore:` prefixes.
5. **Tag optional milestones:** For stable snapshots, `git tag -a v5-YYYYMMDD -m "Snapshot after <feature>"`.
6. **Rollback options:** 
   - Single file: `git checkout HEAD -- <file>` (or `git restore <file>`).
   - Whole repo to last commit: `git reset --hard HEAD`.
   - To a prior commit: `git reset --hard <commit>` (only with explicit approval).

### Backups
- Existing: `team_cli_v3.py.bak` (2025-12-15).
- Created now: `team_cli_v5.py.bak` (copy of current main CLI as of 2025-12-17).
- Keep `.bak` files for major versions; `.gitignore` excludes them so they stay local.

### Notes
- Initial repository commit created on 2025-12-17 (`Initial commit`).
- If logs or caches grow large, consider updating `.gitignore` rather than deleting history.
- When in doubt, prefer a new commit over rewriting history to preserve traceability.

Signed: Codex (2025-12-17)
