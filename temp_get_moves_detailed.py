import sys
import json
import requests
from pathlib import Path
import os

# Mimic log_verbose for minimal output
def log_verbose(msg: str):
    pass
def progress(msg: str):
    pass

# --- Mimic Global Vars from team_cli_v3 ---
POKEAPI_BASE = "https://pokeapi.co/api/v2"
VERSION_GROUP = "legends-za"
POKEMON_CACHE = {}
BOARD_CACHE = {}
AVAILABILITY_CACHE = {}
# Simplified ZA_POKEDEX_SET to only include relevant Pokemon for faster testing
ZA_POKEDEX_SET = set(["chikorita", "gengar", "staryu", "feraligatr", "mewtwo", "frogadier", "starmie", "greninja"])
TYPE_CACHE_PATH = Path(__file__).parent / "type_chart_cache.json"
DRAFT_CACHE_PATH = Path(__file__).parent / "draft_cache.json"

# --- Stat functions (copied from team_cli_v3 for self-containment) ---
def pokemon_base_stat_total(name: str):
    key = (name or "").lower()
    if not key: return 0
    try:
        if key not in POKEMON_CACHE:
            res = requests.get(f"{POKEAPI_BASE}/pokemon/{key}", timeout=15)
            res.raise_for_status()
            POKEMON_CACHE[key] = res.json()
        data = POKEMON_CACHE.get(key) or {}
        stats = data.get("stats") or []
        return sum(s.get("base_stat", 0) for s in stats)
    except Exception: return 0

def pokemon_offense_stat_total(name: str):
    key = (name or "").lower()
    if not key: return 0
    try:
        if key not in POKEMON_CACHE:
            res = requests.get(f"{POKEAPI_BASE}/pokemon/{key}", timeout=15)
            res.raise_for_status()
            POKEMON_CACHE[key] = res.json()
        data = POKEMON_CACHE.get(key) or {}
        stats = data.get("stats") or []
        total = 0
        for s in stats:
            stat_name = (s.get("stat") or {}).get("name", "")
            if stat_name in {"attack", "special-attack"}: total += s.get("base_stat", 0)
        return total
    except Exception: return 0

def pokemon_defense_stat_total(name: str):
    key = (name or "").lower()
    if not key: return 0
    try:
        if key not in POKEMON_CACHE:
            res = requests.get(f"{POKEAPI_BASE}/pokemon/{key}", timeout=15)
            res.raise_for_status()
            POKEMON_CACHE[key] = res.json()
        data = POKEMON_CACHE.get(key) or {}
        stats = data.get("stats") or []
        total = 0
        for s in stats:
            stat_name = (s.get("stat") or {}).get("name", "")
            if stat_name in {"defense", "special-defense"}: total += s.get("base_stat", 0)
        return total
    except Exception: return 0

# --- Helper to get stat functions ---
def _get_pokemon_stat_total_fn(key: str):
    if key == "defense": return pokemon_defense_stat_total
    elif key == "offense": return pokemon_offense_stat_total
    return pokemon_base_stat_total

# --- Mimic fetch_pokemon_typing (needed for pick_moves) ---
def fetch_pokemon_typing(name: str):
    key = name.lower()
    if key in POKEMON_CACHE:
        return [t["type"]["name"] for t in sorted(POKEMON_CACHE[key]["types"], key=lambda x: x["slot"])]
    try:
        res = requests.get(f"{POKEAPI_BASE}/pokemon/{key}", timeout=15)
        res.raise_for_status()
        POKEMON_CACHE[key] = res.json()
        types = [t["type"]["name"] for t in sorted(POKEMON_CACHE[key]["types"], key=lambda x: x["slot"])]
        return types
    except Exception: return []

# --- Import pick_moves from move_suggestor ---
try:
    # Adjust sys.path to ensure move_suggestor is found
    # This assumes move_suggestor.py is in the same directory as this script, or in python path
    # If move_suggestor itself has complex imports, this might fail.
    sys.path.insert(0, str(Path(__file__).parent))
    from move_suggestor import pick_moves
except ImportError as e:
    print(f"Error importing pick_moves: {e}. Ensure move_suggestor.py is accessible.", file=sys.stderr)
    sys.exit(1)

# --- cache_draft_board (copied from team_cli_v3) ---
def board_cache_key(name: str, level_cap=None, version_group=VERSION_GROUP):
    return (name.lower(), level_cap, version_group)

def _save_draft_cache(): # Mocked
    pass

def cache_draft_board(name: str, level_cap=None):
    key = board_cache_key(name, level_cap=level_cap)
    cached = BOARD_CACHE.get(key)
    if not cached:
        info = pick_moves(
            name,
            level_cap=level_cap,
            exclude_moves=set(),
            used_moves=set(),
            version_group=VERSION_GROUP,
        )
        move_types = sorted(list({m["type"] for m in info.get("draft_board", []) if m.get("type")}))
        se_hits = sorted(list([t for t, cnt in info.get("coverage_priority", []) if cnt > 0]))
        cached = {
            "info": info, # Raw pick_moves info
            "move_types": move_types,
            "se_hits": se_hits,
            "role": info.get("role"),
            "alignment_score": info.get("alignment_score"),
        }
        BOARD_CACHE[key] = cached
        _save_draft_cache()
    return cached

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python temp_get_moves_detailed.py <pokemon_name>", file=sys.stderr)
        sys.exit(1)
    
    pokemon_name = sys.argv[1]
    
    # Get stats
    base_stats = pokemon_base_stat_total(pokemon_name)
    def_stats = pokemon_defense_stat_total(pokemon_name)
    off_stats = pokemon_offense_stat_total(pokemon_name)
    typing = fetch_pokemon_typing(pokemon_name)

    # Get moves info via cache_draft_board
    cached_board = cache_draft_board(pokemon_name)
    
    result = {
        "name": pokemon_name,
        "typing": typing,
        "base_stat_total": base_stats,
        "defensive_stat_total": def_stats,
        "offensive_stat_total": off_stats,
        "move_types": cached_board.get("move_types", []),
        "se_hits": cached_board.get("se_hits", []),
        "role": cached_board.get("role", "n/a"),
        "alignment_score": cached_board.get("alignment_score", 0),
        # You can add raw moves from cached_board["info"]["draft_board"] if needed for full list
    }
    print(json.dumps(result, indent=2))
