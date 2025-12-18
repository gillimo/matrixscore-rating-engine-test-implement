## Priorities (2025-12-17)

1) Fix scoring correctness
- Resolve defense=0 bug (BUG-2025-12-15-036) and offense delta inflation (BUG-2025-12-15-037).
- Enforce overlap penalties (5 points per overlapping weakness); clamp to 100 when no gaps/overlaps.

2) Enforce defense-first autofill
- BUG-2025-12-15-039: offense picks must come from top defensive delta pool (remove `[:3]` shortcuts) across autofill/finalize.

3) Explainability and logging
- BUG-2025-12-15-034/035: add concise explanations for picks and low-stat wins.
- Reduce log noise and fix hangs/empty logs (BUG-2025-12-13-014).

4) Move selection quality
- Wire coverage-aware move selection and positive-gain gating; expand move payloads beyond 1-move outputs (FT-2025-12-17-001).

5) UX feature: unavailable mon reroll
- GUI click-to-reroll slot using current team context (FT-2025-12-17-002).

Scope: code in git + tickets added by the current agent are in-scope.

Signed: Codex (2025-12-17)
