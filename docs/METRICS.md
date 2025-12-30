## Metrics (v6 snapshot, 2025-12-28)

This document reflects the current scoring formulas in `team_cli_v6.py`.

Defense (typing_score)
- Coverage inputs: for each attack type, count team members that are weak, resist, immune, or neutral.
- Exposed type: `weak > (resist + immune)`.
- Score formula:
  - `def_score = 100 - 8*exposure_gap_total - 8*stack_overlap`
  - `exposure_gap_total = sum(max(0, weak - (resist + immune)))`
  - `stack_overlap = sum(max(0, weak - 1))`
  - No explicit exposure caps/floors; score clamps to 0..100 only.

Defense (display score)
- Uses the same `typing_score` output as the core defense score to keep all UI surfaces aligned.

Defensive delta (typing_delta)
- Base typing delta is `typing_score(sim) - typing_score(base)`.
- Bonus adjustments: add `immune_gain*6 + resist_gain*3` for gains against currently exposed types (used for selection; printed delta remains raw score delta).
- Best remaining defensive delta/headroom and rating calculations use the raw score delta (no bonus).

Shared weakness score
- `overlap = max(0, max_weak - 1)`
- `exposed = count(weak > resist+immune)`
- `score = 100 - 10*overlap - 5*exposed` (clamped to 0..100)

Offense score (offense_score_with_bonuses)
- Build a move-type set from suggested moves across team.
- Exposed types: `weak > (resist + immune)`.
- For each exposed type:
  - If any move type hits it SE: no penalty.
- Else if neutral coverage exists: `+6` penalty.
- Else (immune): `+14` penalty.
- Breadth penalty: `max(0, 2 - len(move_types)) * 3`.
- Base score: `100 - penalties - breadth_penalty`, clamped 0..100.
- If all exposures are covered (penalties == 0), add a capped breadth bonus:
  - `neutral_ratio = neutral_or_better / total_types`
  - `se_ratio = se_types / total_types`
  - `breadth_bonus = min(10, 5*neutral_ratio + 6*se_ratio)`

Offensive delta headroom (compute_best_offense_gain)
- Base gain: `sim_offense - base_offense` using the offense score above.
- Gain factor: `(1 + 1.0*closed_weak) * (1 + 0.25*len(new_types))`
- Offensive stat total: `attack + special_attack + 1.00*speed`
- BST factor: `bst_factor = clamp(0.8, 1.3, 0.7 + offense_stat_total/450)`
- SE factor: `se_factor = 1.0 + 0.05*min(6, len(se_types))`
- Ranked gain: `gain * gain_factor * bst_factor * se_factor * coverage_penalty` (capped at 100 for headroom use).
- Coverage penalty: `0.85` when neutral reach is near-complete but SE coverage is thin; else `1.0`.

Overall score (overall_score)
- `delta_penalty = 0.10 * (best_defensive_delta + best_offense_gap)`
- `shared_penalty = max(0, 100 - shared_score) * 0.03`
- `overall = 100 - delta_penalty - shared_penalty` (clamped 0..100)
- Defense floor: if `def_score < 85`, subtract `(85 - def_score) * 0.4`.
- Stack penalty is currently 0 (stacking is already captured in shared weakness).
- Role balance penalty: after overall, subtract `0.25*(count-2)` for each role with 3+ members.
- BST penalty: if average BST < 500, subtract `min(4, (500 - avg_bst) / 12)`.

Signed: Codex (2025-12-29)
Safe typing adds (CLI list)
- Strong types: `resist + immune - weak >= 2` from current team coverage.
- Score per typing: `100 - 12*missing_strong - added_weakness_penalty + 15 bonus if no added weaknesses` (clamped 0..100).
  - `added_weakness_penalty`: per newly added weak type, use current net margin after adding:
    - `margin >= 2`: `+0`
    - `margin >= 1`: `+3`
    - `margin >= 0`: `+6`
    - `margin < 0`: `+12`
- Coverage bonus: for each newly added weak type that remains covered (`margin >= 0`), add `immune*6 + resist*3`.
- Inclusion: show typings that keep all new weaknesses covered (`margin >= 0`) or produce a positive defensive delta.
- List order: highest score, then fewest added weaknesses, then fewest missing strong types.
- Display note: lists any newly added weaknesses and how covered they are by the current team (R/I counts), plus raw defensive score delta.
