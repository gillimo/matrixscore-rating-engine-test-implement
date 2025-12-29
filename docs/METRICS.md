## Metrics (v6 snapshot, 2025-12-28)

This document reflects the current scoring formulas in `team_cli_v6.py`.

Defense (typing_score)
- Coverage inputs: for each attack type, count team members that are weak, resist, immune, or neutral.
- Exposed type: `weak > (resist + immune)`.
- Score formula:
  - `def_score = 100 - 2.1*total_weak + 1.6*total_resist + 4.0*total_immune + 7.0*exposed_immunes - 14*net_exposed - 12*stack_overlap`
  - `stack_overlap = sum(max(0, weak - 1))`
  - `exposed_immunes = sum(immune for exposed attack types)`
  - If `net_exposed == 0`, defense returns 100; otherwise clamps to 0..99.

Defense (display score)
- Uses the same `typing_score` formula as the core defense score to keep the numbers consistent across UI surfaces.

Defensive delta (typing_delta)
- Base typing delta is `typing_score(sim) - typing_score(base)`.
- Penalty/bonus adjustments:
  - Penalty: `new_exposed*16 + max(0, stack_delta)*12 + max(0, new_weak - new_resist)*7`
  - Bonus: `immune_gain*12 + resist_gain*5 + max(0, new_resist - new_weak)*2`
  - `stack_delta = stack_overlap(sim) - stack_overlap(base)`

Shared weakness score
- `overlap = max(0, max_weak - 1)`
- `stack = sum(max(0, weak - 1))` (if `stack == 1`, set to 0)
- `exposed = count(weak > resist+immune)`
- `score = 100 - 12*overlap - 4*stack - 6*exposed` (clamped to 0..100)

Offense score (offense_score_with_bonuses)
- Build a move-type set from suggested moves across team.
- Exposed types: `weak > (resist + immune)`.
- For each exposed type:
  - If any move type hits it SE: no penalty.
  - Else if neutral coverage exists: `+7` penalty.
  - Else (immune): `+16` penalty.
- Breadth penalty: `max(0, 2 - len(move_types)) * 4`.
- Base score: `100 - penalties - breadth_penalty`, clamped 0..100.
- If all exposures are covered (penalties == 0), add a capped breadth bonus:
  - `neutral_ratio = neutral_or_better / total_types`
  - `se_ratio = se_types / total_types`
  - `breadth_bonus = min(10, 5*neutral_ratio + 6*se_ratio)`

Offensive delta headroom (compute_best_offense_gain)
- Base gain: `sim_offense - base_offense` using the offense score above.
- Gain factor: `(1 + 1.0*closed_weak) * (1 + 0.25*len(new_types))`
- Offensive stat total: `attack + special_attack + 0.75*speed`
- BST factor: `bst_factor = clamp(0.8, 1.3, 0.7 + offense_stat_total/450)`
- SE factor: `se_factor = 1.0 + 0.05*min(6, len(se_types))`
- Ranked gain: `gain * gain_factor * bst_factor * se_factor * coverage_penalty`
- Coverage penalty: `0.85` when neutral reach is near-complete but SE coverage is thin; else `1.0`.

Overall score (overall_score)
- `delta_penalty = 0.1 * (best_defensive_delta + best_offense_gap)`
- `shared_penalty = max(0, 100 - shared_score) * 0.04`
- `overall = 100 - delta_penalty - shared_penalty` (clamped 0..100)
- Stack penalty is currently 0 (stacking is already captured in shared weakness).
- Role balance penalty: after overall, subtract `0.5*(count-2)` for each role with 3+ members.

Signed: Codex (2025-12-28)
Safe typing adds (CLI list)
- Strong types: `resist + immune - weak >= 2` from current team coverage.
- Score per typing: `100 - 12*missing_strong - 6*added_weaknesses` (clamped 0..100).
- List order: fewest added weaknesses, then fewest missing strong types, then score.
