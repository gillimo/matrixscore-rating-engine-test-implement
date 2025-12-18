## Metrics (v5 snapshot)

Current intent (needs fixes):
- Overall: target `100 - (best_defensive_delta + best_offense_gap)`, with 5-point penalty per overlapping weakness. Should hit 100 when both deltas are 0 and no overlaps. Known bug: defense can hit 0 and offense gaps can inflate (e.g., +289) leading to nonsensical overall.
- Defense: typing delta with penalties for new exposures/stacking; needs stronger bias against introducing 4x/2x stacks (BUG-2025-12-15-023/024) and fix for zero-score cases (BUG-2025-12-15-036).
- Offense: headroom/gap based on coverage; inflation observed (BUG-2025-12-15-037). Move drafting still thin (often 1 move/mon).
- Shared/overlap: overlapping weaknesses should incur penalties; ensure penalty applied consistently in overall.

Move selection (in progress):
- Draft board up to top 12; aim to suggest 4 moves per mon.
- Moves should be coverage-aware (exposed/needed types) with positive-gain enforcement before delta=0 fallbacks; high-BST fallback last.
- De-dupe moves globally; refresh stale move data to avoid 1-move outputs.

Action items:
- Normalize defensive delta (handle new exposures/stacking correctly).
- Clamp/adjust offensive gap to prevent inflation and reflect real coverage gains.
- Enforce overlap penalties in overall; ensure 100 when no gaps/overlaps.
- Fully wire coverage-aware move selection and positive-gain gating.

Signed: Codex (2025-12-17)
