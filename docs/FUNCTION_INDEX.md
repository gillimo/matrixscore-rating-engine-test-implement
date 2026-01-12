# Function Index (DLC)

Quick reference for finding functions. Line numbers are approximate.

## team_cli_dlc.py (Main CLI)

### Core Data & API
| Line | Function | Purpose |
|------|----------|---------|
| 487 | `normalize_type_pokemon_entry` | Normalize Pokemon names from type API |
| 524 | `fetch_type_chart` | Get type effectiveness chart |
| 565 | `fetch_pokemon_typing` | Get Pokemon's types |
| 580 | `pokemon_base_stat_total` | Get BST for a Pokemon |
| 597 | `pokemon_speed_stat` | Get Speed stat |
| 619 | `pokemon_offense_stat_total` | Get offensive stats total |
| 644 | `pokemon_defense_stat_total` | Get defensive stats total |
| 676 | `pokemon_in_version` | Check if Pokemon is in ZA dex |
| 686 | `get_final_forms` | Get all final evolution forms |
| 773 | `fetch_single_type_candidates` | Get Pokemon of a single type |
| 834 | `fetch_species_info` | Get species data from API |
| 842 | `is_terminal_form` | Check if Pokemon is final evo |
| 892 | `is_legendary_or_mythical` | Check legendary/mythical status |
| 905 | `fetch_dual_candidates` | Get Pokemon with two specific types |
| 919 | `normalize_pokemon_name` | Normalize Pokemon name input |
| 929 | `api_pokemon_key` | Get PokeAPI key (handles form names) |

### Team Scoring
| Line | Function | Purpose |
|------|----------|---------|
| 1002 | `defensive_multiplier` | Calculate type multiplier |
| 1010 | `compute_coverage` | Compute team defensive coverage |
| 1044 | `typing_score` | Calculate defense score (0-100) |
| 1087 | `typing_delta` | Calculate typing improvement delta |
| 3126 | `shared_weak_score` | Score for shared weaknesses |
| 3137 | `offense_score_with_bonuses` | Calculate offense score |
| 3176 | `predict_overall` | Predict overall team rating |
| 3234 | `overall_score` | Compute final overall score |
| 3665 | `final_team_rating` | Final rating with all factors |

### Team Building
| Line | Function | Purpose |
|------|----------|---------|
| 1116 | `best_defensive_improvement` | Find best defensive add |
| 1171 | `get_best_defensive_candidates` | Get ranked defensive options |
| 1266 | `pick_defensive_addition` | Choose a defensive Pokemon |
| 1315 | `pick_offense_addition` | Choose an offensive Pokemon |
| 1512 | `suggestion_buckets` | Group suggestions by category |
| 1813 | `_preview_autopick` | Preview next autopick |
| 1882 | `_top_defensive_typings` | Get top defensive type combos |
| 1946 | `_safe_typing_adds` | Get safe additions list |
| 2068 | `_filtered_type_suggestions` | Filter suggestions by type |
| 2768 | `suggest_drop_upgrade` | Suggest who to drop/replace |
| 3292 | `pick_overall_addition` | Pick balanced addition |
| 3476 | `autofill_team` | Auto-fill remaining slots |

### Output & Display
| Line | Function | Purpose |
|------|----------|---------|
| 2531 | `defense_focus_report` | Print defense suggestions |
| 2609 | `print_speed_candidates` | Print speed rankings |
| 2661 | `coverage_report` | Print coverage analysis |
| 2871 | `_print_red_summary` | Print team summary |
| 2302 | `print_bst_compare` | Compare BST between Pokemon |
| 2384 | `print_move_search` | Search moves by criteria |

### Caching
| Line | Function | Purpose |
|------|----------|---------|
| 414 | `_load_draft_cache` | Load cached draft boards |
| 432 | `_save_draft_cache` | Save draft cache |
| 443 | `_load_type_pokemon_cache` | Load type->Pokemon cache |
| 467 | `_load_mega_cache` | Load mega evolution cache |
| 3793 | `cache_draft_board` | Cache a Pokemon's draft board |

### Entry Point
| Line | Function | Purpose |
|------|----------|---------|
| 3935 | `main` | Main CLI entry point |

---

## move_suggestor.py (Move Selection)

| Line | Function | Purpose |
|------|----------|---------|
| 1055 | `normalize_move_name` | Normalize move name |
| 1174 | `fetch_type_chart` | Get type chart |
| 1232 | `fetch_pokemon` | Fetch Pokemon data |
| 1249 | `compute_defensive_weaknesses` | Get type weaknesses |
| 1261 | `classify_role` | Classify as sweeper/tank/balanced |
| 1285 | `collect_move_pool` | Get available moves |
| 1318 | `fetch_move_detail` | Get move details |
| 1330 | `pick_moves` | **Main function**: Pick 4 moves + draft board |
| 1751 | `format_output` | Format Pokemon info for display |
| 1805 | `format_team` | Format team info |

---

## move_rarity.py (Move Rarity Scoring)

| Line | Function | Purpose |
|------|----------|---------|
| 27 | `_build_move_rarity_cache` | Build rarity scores |
| 90 | `get_rarity_for_move` | Get rarity score for a move |

---

## tk_team_builder.py (GUI)

| Line | Function | Purpose |
|------|----------|---------|
| 93 | `load_payload_team` | Load team from payload file |
| 136 | `build_matrix` | Build type effectiveness matrix |
| 244 | `compute_coverage` | Compute coverage (GUI version) |
| 293 | `typing_score` | Calculate typing score (GUI) |
| 379 | `TeamBuilderApp.__init__` | Main app class |
| 435 | `_build_ui` | Build the UI |
| 528 | `add_pokemon` | Add Pokemon to team |

---

## Key Constants (team_cli_dlc.py)

| Line | Constant | Purpose |
|------|----------|---------|
| 105 | `ZA_POKEDEX` | List of all Pokemon in Legends Z-A |
| 69 | `TYPE_FORM_REMAPS` | Map API forms to display names |
| 105 | `API_FORM_DEFAULTS` | Map display names to API forms |
| 271 | `TYPE_POOL` | List of all 18 types |

---
Generated: 2026-01-11
