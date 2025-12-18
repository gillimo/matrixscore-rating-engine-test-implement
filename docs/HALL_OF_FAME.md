## Hall of Fame

- 2025-12-13 (Vega): Tuned caching/logging, hardened GUI trace, enforced overlap gates with fallbacks to reach 6 during v2 stabilization.
- 2025-12-15 (Cygnus): Refactored scoring to clearer delta-based approach; optimized offensive suggestions; fixed critical v3 bugs.
- 2025-12-15 (Gemini): Fixed RecursionError in v3; added `pokemon_defense_stat_total`; refined overall score to “100 - remaining gaps”; built test harness and caching/perf improvements.
- 2025-12-17 (Atlas runs): Defense-first improvements—tie-aware defensive pool, positive-gain gating with BST floor, global move de-dupe, lazy move loading, colored decision logs. Added move-data refresh to avoid 1-move outputs; Tk wheel single-fire per run; draft results now up to four de-duped moves per mon. Known gap: offense still bottlenecked by thin move payloads; next push is richer move drafting and positive-gain enforcement.

Signed: Codex (2025-12-17)
