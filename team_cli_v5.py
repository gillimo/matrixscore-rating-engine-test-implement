#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combined CLI: build team typings first, then suggest moves, then launch Tk wheel with final team.
"""
import json
import inspect
import os
import subprocess
import sys
import builtins
import threading
from datetime import datetime
from pathlib import Path
import json

from move_suggestor import ROLE_MOVE_MIX, pick_moves, format_output, get_move_cache_stats

import requests

POKEAPI_BASE = "https://pokeapi.co/api/v2"
EXCLUDED_TYPES = {"shadow", "unknown"}
VERSION_GROUP = "legends-za"
FINAL_FORMS_CACHE = None
POKEMON_CACHE = {}
AVAILABILITY_CACHE = {}
VERBOSE = False
BOARD_CACHE = {}
BOARD_CACHE_STATS = {"hit": 0, "miss": 0, "persist_fail": 0, "loaded": 0}
TOTAL_POKEMON_FOR_MOVE_FETCH = 0
POKEMON_MOVES_FETCHED = 0
LOG_DIR = Path(__file__).with_name("logs")
TYPE_CACHE_PATH = Path(__file__).with_name("type_chart_cache.json")
DRAFT_CACHE_PATH = Path(__file__).with_name("draft_cache.json")
TYPE_POKEMON_CACHE_PATH = Path(__file__).with_name("type_pokemon_cache.json")
FINAL_FORMS_CACHE_PATH = Path(__file__).with_name("final_forms_cache.json")
LOG_FOOTER = "Permissions: full access to OneDrive/Desktop/teambuilder_v2 granted by user on 2025-12-12. Signed: Atlas"
VERBOSE = False  # enable for detailed loop progress during test runs
TRACE_FUNCTIONS = True  # tracing enabled for detailed logs
HARNESS_SMOKE = os.environ.get("TEAM_HARNESS_SMOKE", "0") == "1" or "--harness-smoke" in sys.argv
TYPE_CACHE_STATS = {"hit": 0, "miss": 0}
ZA_POKEDEX = [
    "chikorita","bayleef","meganium",
    "tepig","pignite","emboar",
    "totodile","croconaw","feraligatr",
    "fletchling","fletchinder","talonflame",
    "bunnelby","diggersby",
    "scatterbug","spewpa","vivillon",
    "weedle","kakuna","beedrill",
    "pidgey","pidgeotto","pidgeot",
    "mareep","flaaffy","ampharos",
    "patrat","watchog",
    "budew","roselia","roserade",
    "magikarp","gyarados",
    "binacle","barbaracle",
    "staryu","starmie",
    "flabebe","floette","florges",
    "skiddo","gogoat",
    "espurr","meowstic",
    "litleo","pyroar",
    "pancham","pangoro",
    "trubbish","garbodor",
    "dedenne",
    "pichu","pikachu","raichu",
    "cleffa","clefairy","clefable",
    "spinarak","ariados",
    "ekans","arbok",
    "abra","kadabra","alakazam",
    "gastly","haunter","gengar",
    "venipede","whirlipede","scolipede",
    "honedge","doublade","aegislash",
    "bellsprout","weepinbell","victreebel",
    "pansage","simisage",
    "pansear","simisear",
    "panpour","simipour",
    "meditite","medicham",
    "electrike","manectric",
    "ralts","kirlia","gardevoir","gallade",
    "houndour","houndoom",
    "swablu","altaria",
    "audino",
    "spritzee","aromatisse",
    "swirlix","slurpuff",
    "eevee","vaporeon","jolteon","flareon","espeon","umbreon","leafeon","glaceon","sylveon",
    "buneary","lopunny",
    "shuppet","banette",
    "vanillite","vanillish","vanilluxe",
    "numel","camerupt",
    "hippopotas","hippowdon",
    "drilbur","excadrill",
    "sandile","krokorok","krookodile",
    "machop","machoke","machamp",
    "gible","gabite","garchomp",
    "carbink",
    "sableye",
    "mawile",
    "absol",
    "riolu","lucario",
    "slowpoke","slowbro","slowking",
    "carvanha","sharpedo",
    "tynamo","eelektrik","eelektross",
    "dratini","dragonair","dragonite",
    "bulbasaur","ivysaur","venusaur",
    "charmander","charmeleon","charizard",
    "squirtle","wartortle","blastoise",
    "stunfisk",
    "furfrou",
    "inkay","malamar",
    "skrelp","dragalge",
    "clauncher","clawitzer",
    "goomy","sliggoo","goodra",
    "delibird",
    "snorunt","glalie","froslass",
    "snover","abomasnow",
    "bergmite","avalugg",
    "scyther","scizor",
    "pinsir",
    "heracross",
    "emolga",
    "hawlucha",
    "phantump","trevenant",
    "scraggy","scrafty",
    "noibat","noivern",
    "klefki",
    "litwick","lampent","chandelure",
    "aerodactyl",
    "tyrunt","tyrantrum",
    "amaura","aurorus",
    "onix","steelix",
    "aron","lairon","aggron",
    "helioptile","heliolisk",
    "pumpkaboo","gourgeist",
    "larvitar","pupitar","tyranitar",
    "froakie","frogadier","greninja",
    "falinks",
    "chespin","quilladin","chesnaught",
    "skarmory",
    "fennekin","braixen","delphox",
    "bagon","shelgon","salamence",
    "kangaskhan",
    "drampa",
    "beldum","metang","metagross",
    "xerneas","yveltal","zygarde","diancie",
    "mewtwo",
]
ZA_POKEDEX_SET = set(ZA_POKEDEX)
TYPE_POOL = [
    "normal",
    "fire",
    "water",
    "electric",
    "grass",
    "ice",
    "fighting",
    "poison",
    "ground",
    "flying",
    "psychic",
    "bug",
    "rock",
    "ghost",
    "dragon",
    "dark",
    "steel",
    "fairy",
]
# Stable list of types for rating operations (avoids relying on API order)
TYPE_POOL = [
    "normal",
    "fire",
    "water",
    "electric",
    "grass",
    "ice",
    "fighting",
    "poison",
    "ground",
    "flying",
    "psychic",
    "bug",
    "rock",
    "ghost",
    "dragon",
    "dark",
    "steel",
    "fairy",
]

def trace_call(fn):
    """Decorator to trace function calls if TRACE_FUNCTIONS is enabled."""
    if not TRACE_FUNCTIONS:
        return fn

    def wrapper(*args, **kwargs):
        name = fn.__name__
        arg_str = ", ".join([repr(a) for a in args] + [f"{k}={repr(v)}" for k, v in kwargs.items()])
        # Print trace lines regardless of VERBOSE to ensure visibility in logs.
        print(f"[TRACE] Calling {name}({arg_str})")
        result = fn(*args, **kwargs)
        print(f"[TRACE] {name} -> {repr(result)}")
        return result
    return wrapper


def log_verbose(msg: str):
    if VERBOSE:
        print(f"[VERBOSE] {msg}")


def progress(msg: str):
    """Always-on progress indicator for long steps."""
    print(f"[progress] {msg}")


def loop_progress(context: str, count: int, freq: int = 25, total: int = None):
    """Print an occasional progress update for long-running loops."""
    if count % freq == 0 or count == 1:
        total_hint = f" / {total}" if total else ""
        progress(f"[{context}] processed {count}{total_hint} candidates")


def board_cache_key(name: str, level_cap=None, version_group=VERSION_GROUP):
    return (name.lower(), level_cap, version_group)


def _load_draft_cache():
    """Load draft cache from disk into BOARD_CACHE (keys: name, level_cap, version_group)."""
    if not DRAFT_CACHE_PATH.exists():
        return
    try:
        data = json.loads(DRAFT_CACHE_PATH.read_text(encoding="utf-8"))
        for k, v in data.items():
            try:
                nm, lvl, vg = k.split("|", 2)
                lvl_val = None if lvl == "" else int(lvl)
                BOARD_CACHE[(nm, lvl_val, vg)] = v
                BOARD_CACHE_STATS["loaded"] += 1
            except Exception:
                continue
    except Exception:
        pass


def _save_draft_cache():
    try:
        ser = {}
        for (nm, lvl, vg), val in BOARD_CACHE.items():
            lvl_part = "" if lvl is None else str(lvl)
            ser[f"{nm}|{lvl_part}|{vg}"] = val
        DRAFT_CACHE_PATH.write_text(json.dumps(ser), encoding="utf-8")
    except Exception:
        BOARD_CACHE_STATS["persist_fail"] += 1


def _load_type_pokemon_cache():
    if TYPE_POKEMON_CACHE_PATH.exists():
        try:
            return json.loads(TYPE_POKEMON_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_type_pokemon_cache(cache):
    try:
        TYPE_POKEMON_CACHE_PATH.write_text(json.dumps(cache), encoding="utf-8")
    except Exception:
        pass


def refresh_type_chart_async(session):
    """Refresh type chart in the background and update cache."""
    def _refresh():
        try:
            res = session.get(f"{POKEAPI_BASE}/type", timeout=15)
            res.raise_for_status()
            type_list = [t["name"] for t in res.json()["results"] if t["name"] not in EXCLUDED_TYPES]
            chart = {t: {} for t in type_list}
            for t in type_list:
                d = session.get(f"{POKEAPI_BASE}/type/{t}", timeout=15).json()
                rel = d["damage_relations"]
                for target in type_list:
                    chart[t][target] = 1.0
                for rr in rel["double_damage_to"]:
                    chart[t][rr["name"]] = 2.0
                for rr in rel["half_damage_to"]:
                    chart[t][rr["name"]] = 0.5
                for rr in rel["no_damage_to"]:
                    chart[t][rr["name"]] = 0.0
            TYPE_CACHE_PATH.write_text(json.dumps({"chart": chart, "types": type_list}), encoding="utf-8")
            log_verbose("[type_chart] background refresh complete")
        except Exception as exc:
            log_verbose(f"[type_chart] background refresh failed: {exc}")

    threading.Thread(target=_refresh, daemon=True).start()

def fetch_type_chart():
    # Try cached chart first to avoid repeat network timeouts; refresh in background
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=2)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    if TYPE_CACHE_PATH.exists():
        try:
            data = json.loads(TYPE_CACHE_PATH.read_text(encoding="utf-8"))
            chart = data.get("chart", {})
            type_list = data.get("types", [])
            if chart and type_list:
                log_verbose("[type_chart] loaded from cache; refreshing in background")
                refresh_type_chart_async(session)
                return chart, type_list
        except Exception:
            pass

    res = session.get(f"{POKEAPI_BASE}/type", timeout=15)
    res.raise_for_status()
    type_list = [t["name"] for t in res.json()["results"] if t["name"] not in EXCLUDED_TYPES]
    chart = {t: {} for t in type_list}
    for t in type_list:
        d = session.get(f"{POKEAPI_BASE}/type/{t}", timeout=15).json()
        rel = d["damage_relations"]
        for target in type_list:
            chart[t][target] = 1.0
        for rr in rel["double_damage_to"]:
            chart[t][rr["name"]] = 2.0
        for rr in rel["half_damage_to"]:
            chart[t][rr["name"]] = 0.5
        for rr in rel["no_damage_to"]:
            chart[t][rr["name"]] = 0.0
    try:
        TYPE_CACHE_PATH.write_text(json.dumps({"chart": chart, "types": type_list}), encoding="utf-8")
    except Exception:
        pass
    return chart, type_list


def fetch_pokemon_typing(name: str):
    key = name.lower()
    if key in POKEMON_CACHE:
        POKEMON_CACHE["__hits__"] = POKEMON_CACHE.get("__hits__", 0) + 1
    else:
        POKEMON_CACHE["__miss__"] = POKEMON_CACHE.get("__miss__", 0) + 1
        res = requests.get(f"{POKEAPI_BASE}/pokemon/{key}", timeout=15)
        res.raise_for_status()
        POKEMON_CACHE[key] = res.json()
    data = POKEMON_CACHE[key]
    types = [t["type"]["name"] for t in sorted(data["types"], key=lambda x: x["slot"])]
    return types


def pokemon_base_stat_total(name: str):
    key = (name or "").lower()
    if not key:
        return 0
    try:
        if key not in POKEMON_CACHE:
            res = requests.get(f"{POKEAPI_BASE}/pokemon/{key}", timeout=15)
            res.raise_for_status()
            POKEMON_CACHE[key] = res.json()
        data = POKEMON_CACHE.get(key) or {}
        stats = data.get("stats") or []
        return sum(s.get("base_stat", 0) for s in stats)
    except Exception:
        return 0


def pokemon_offense_stat_total(name: str):
    """Return offensive stat total (Atk + SpA) for use in offense scoring/sorting."""
    key = (name or "").lower()
    if not key:
        return 0
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
            if stat_name in {"attack", "special-attack"}:
                total += s.get("base_stat", 0)
        return total
    except Exception:
        return 0


def pokemon_defense_stat_total(name: str):
    """Return defensive stat total (Def + SpD) for use in defense scoring/sorting."""
    key = (name or "").lower()
    if not key:
        return 0
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
            if stat_name in {"defense", "special-defense"}:
                total += s.get("base_stat", 0)
        return total
    except Exception:
        return 0


def _get_pokemon_stat_total_fn(key: str):
    """Helper to return the correct stat total function based on key."""
    if key == "defense":
        return pokemon_defense_stat_total
    elif key == "offense":
        return pokemon_offense_stat_total
    return pokemon_base_stat_total


def pokemon_in_version(name: str, version_group: str = VERSION_GROUP):
    """Return True if the Pokemon is in the hardcoded Legends ZA dex list."""
    key = name.lower()
    if key in AVAILABILITY_CACHE:
        return AVAILABILITY_CACHE[key]
    ok = key in ZA_POKEDEX_SET
    AVAILABILITY_CACHE[key] = ok
    return ok


def get_final_forms():
    """Return a cached set of "final" forms, plus mid-evos whose typing differs from their evolution.

    Example: charmander (no), charmeleon (yes), charizard (yes) because charmeleon/charizard have different typing.
    Uses evolution chains to include typing changes and the last stage; cached to disk to avoid repeat calls.
    """
    global FINAL_FORMS_CACHE
    if FINAL_FORMS_CACHE is not None:
        return FINAL_FORMS_CACHE
    if FINAL_FORMS_CACHE_PATH.exists():
        try:
            data = json.loads(FINAL_FORMS_CACHE_PATH.read_text(encoding="utf-8"))
            FINAL_FORMS_CACHE = set(data)
            return FINAL_FORMS_CACHE
        except Exception:
            FINAL_FORMS_CACHE = None

    type_cache = {}

    def types_for(name: str):
        if name in type_cache:
            return type_cache[name]
        try:
            tps = fetch_pokemon_typing(name)
        except Exception:
            tps = []
        type_cache[name] = tps
        return tps

    chain_cache = {}

    def collect_chain(url: str):
        if url in chain_cache:
            return chain_cache[url]
        try:
            chain = requests.get(url, timeout=15).json().get("chain")
        except Exception:
            chain_cache[url] = set()
            return set()

        result = set()

        def walk(node):
            name = node["species"]["name"]
            children = node.get("evolves_to") or []
            child_names = []
            for c in children:
                child_names.append(c["species"]["name"])
                walk(c)
            if not children:
                result.add(name)
                return
            # include this node if its typing differs from any child typing
            parent_types = types_for(name)
            for cname in child_names:
                c_types = types_for(cname)
                if set(parent_types) != set(c_types):
                    result.add(name)
            # children already walked

        walk(chain)
        chain_cache[url] = result
        return result

    finals = set()
    for name in ZA_POKEDEX:
        try:
            species = fetch_species_info(name)
            chain_url = species.get("evolution_chain", {}).get("url")
            if chain_url:
                finals.update(collect_chain(chain_url))
            else:
                finals.add(name)
        except Exception:
            finals.add(name)

    FINAL_FORMS_CACHE = finals
    try:
        FINAL_FORMS_CACHE_PATH.write_text(json.dumps(sorted(FINAL_FORMS_CACHE)), encoding="utf-8")
    except Exception:
        pass
    return FINAL_FORMS_CACHE

def fetch_single_type_candidates(t, current_team=None, version_group: str = VERSION_GROUP, chart=None, attack_types=None, stat_sort_key=None):
    """Return up to 6 final-form/single-stage Pokemon that are pure type t (and not already on team), scored by projected overall."""
    type_cache = _load_type_pokemon_cache()
    names = type_cache.get(t)
    if not names:
        res = requests.get(f"{POKEAPI_BASE}/type/{t}", timeout=15)
        res.raise_for_status()
        data = res.json()
        names = []
        for p in data.get("pokemon", []):
            pname = p["pokemon"]["name"]
            if "-" in pname:
                continue
            names.append(pname)
        type_cache[t] = names
        _save_type_pokemon_cache(type_cache)
    if current_team:
        current_names = {m["name"] for m in current_team}
        names = [n for n in names if n not in current_names]
    finals_set = get_final_forms()
    candidates = []
    for n in names:
        if finals_set and n not in finals_set:
            continue
        candidates.append(n)

    # Legacy fast path if we don't have scoring context
    if chart is None or attack_types is None:
        finals = []
        for n in candidates[:30]:
            try:
                if not pokemon_in_version(n, version_group=version_group):
                    continue
                typing = fetch_pokemon_typing(n)
                if len(typing) == 1 and typing[0] == t:
                    finals.append(n)
            except Exception:
                continue
            if len(finals) >= 6:
                break
        return sorted(finals)[:6]

    # New logic for when chart and attack_types are available, but without nested predict_overall
    stat_total_fn = _get_pokemon_stat_total_fn(stat_sort_key)
    valid_candidates = []
    for n in candidates:
        try:
            if not pokemon_in_version(n, version_group=version_group):
                continue
            typing = fetch_pokemon_typing(n)
            if len(typing) == 1 and typing[0] == t:
                # Calculate stat_total for basic scoring/sorting, but no sim_overall
                stat_total = stat_total_fn(n)
                valid_candidates.append((stat_total, n))
        except Exception:
            continue
    # Sort by stat_total (descending) to get the "best" candidates in a simple way
    valid_candidates.sort(key=lambda x: x[0], reverse=True)
    return [n for _, n in valid_candidates[:6]] # Return only the names

def fetch_species_info(name: str):
    res = requests.get(f"{POKEAPI_BASE}/pokemon-species/{name.lower()}", timeout=15)
    res.raise_for_status()
    return res.json()

def fetch_dual_candidates(type_a, type_b, current_team=None, version_group: str = VERSION_GROUP, chart=None, attack_types=None, stat_sort_key=None):
    # Gather intersection of pokemon lists for both types
    type_cache = _load_type_pokemon_cache()

    def get_type_pokemon(t):
        names = type_cache.get(t)
        if not names:
            res = requests.get(f"{POKEAPI_BASE}/type/{t}", timeout=15)
            res.raise_for_status()
            data = res.json()
            names = []
            for p in data.get("pokemon", []):
                pname = p["pokemon"]["name"]
                if "-" in pname:
                    continue
                names.append(pname)
            type_cache[t] = names
            _save_type_pokemon_cache(type_cache)
        return set(names)

    try:
        a_list = get_type_pokemon(type_a)
        b_list = get_type_pokemon(type_b)
    except Exception:
        return []
    inter = a_list & b_list
    finals_set = get_final_forms()
    if current_team:
        current_names = {m["name"] for m in current_team}
        inter = {p for p in inter if p not in current_names}

    # Filter to finals if we have the cache; otherwise return a small subset
    if finals_set:
        inter = [p for p in inter if p in finals_set]
    # Legacy fast path without scoring context
    if chart is None or attack_types is None:
        finals = [p for p in sorted(inter) if pokemon_in_version(p, version_group=version_group)][:20]
        return finals[:6]

    # New logic for when chart and attack_types are available, but without nested predict_overall
    stat_total_fn = _get_pokemon_stat_total_fn(stat_sort_key)
    valid_candidates = []
    for n in inter: # 'inter' already filtered by finals_set and current_team
        try:
            if not pokemon_in_version(n, version_group=version_group):
                continue
            typing = fetch_pokemon_typing(n)
            if set(typing) != {type_a, type_b}:
                continue
            # Calculate stat_total for basic scoring/sorting
            stat_total = stat_total_fn(n)
            valid_candidates.append((stat_total, n))
        except Exception:
            continue
    valid_candidates.sort(key=lambda x: x[0], reverse=True)
    return [n for _, n in valid_candidates[:6]] # Return only the names
def list_final_forms():
    # Cache in memory
    url = f"{POKEAPI_BASE}/pokemon?limit=20000"
    res = requests.get(url, timeout=15)
    res.raise_for_status()
    results = res.json()["results"]
    finals = []
    for r in results:
        pname = r["name"]
        try:
            species = fetch_species_info(pname)
        except Exception:
            continue
        evo_chain_url = species.get("evolution_chain", {}).get("url")
        if not evo_chain_url:
            finals.append(pname)
            continue
        try:
            chain = requests.get(evo_chain_url, timeout=15).json()["chain"]
        except Exception:
            finals.append(pname)
            continue
        # traverse to last stage names
        def collect_last(node):
            if not node.get("evolves_to"):
                return [node["species"]["name"]]
            names = []
            for nxt in node["evolves_to"]:
                names.extend(collect_last(nxt))
            return names
        last_names = collect_last(chain)
        if pname in last_names:
            finals.append(pname)
    return set(finals)

FINAL_FORMS_CACHE = None


def defensive_multiplier(attack_type: str, defense_types, chart):
    base = chart.get(attack_type, {})
    mult = 1.0
    for dt in defense_types:
        mult *= base.get(dt, 1.0)
    return mult


def compute_coverage(team, chart, attack_types):
    coverage = []
    for atk in attack_types:
        weak = resist = immune = neutral = 0
        for member in team:
            if not member["types"]:
                continue
            m = defensive_multiplier(atk, member["types"], chart)
            if m == 0:
                immune += 1
            elif m > 1:
                # Self-weak types (ghost/dragon) with STAB: treat as 25% of a weakness
                weak_inc = 1.0
                if atk in member["types"]:
                    weak_inc *= 0.25
                weak += weak_inc
            elif m < 1:
                resist += 1
            else:
                neutral += 1
        size = sum(1 for m in team if m["types"])
        coverage.append(
            {
                "attack": atk,
                "weak": weak,
                "resist": resist,
                "immune": immune,
                "neutral": neutral,
                "size": size,
            }
        )
    return coverage


def typing_score(cov):
    total_weak = sum(c["weak"] for c in cov)
    total_resist = sum(c["resist"] for c in cov)
    total_immune = sum(c["immune"] for c in cov)
    net_exposed = sum(1 for c in cov if c["weak"] > (c["resist"] + c["immune"]))
    stack_overlap = sum(max(0, c["weak"] - 1) for c in cov)
    # Reward immunity to exposed types (heavier than generic immunity)
    top_exposed = [c for c in cov if c["weak"] > (c["resist"] + c["immune"])]
    exposed_immunes = sum(c["immune"] for c in top_exposed)
    # Balanced scoring: weaknesses and exposed types penalize; resist/immune reward
    def_score = (
        100
        - 2.1 * total_weak
        + 1.4 * total_resist
        + 2.2 * total_immune
        + 3.5 * exposed_immunes  # extra credit for blanking largest holes
        - 12 * net_exposed
        - 14 * stack_overlap  # heavier penalty for stacking existing weaknesses
    )
    return max(0, min(100, int(def_score)))


def stack_overlap_penalty(cov):
    """Compute stack overlap term (sum of weaknesses beyond 1 per attack type)."""
    return sum(max(0, c["weak"] - 1) for c in cov)


def delta_def_score(base_cov, sim_cov):
    """Delta based purely on the change in overall team typing score."""
    return typing_score(sim_cov) - typing_score(base_cov)


def addition_allows_overlap(team, pname, ptypes, chart, attack_types):
    """Return True if adding this mon is allowed given overlap rules (overlap only if overall >95)."""
    sim_team = team + [{"name": pname, "types": ptypes, "source": "sim"}]
    sim_cov = compute_coverage(sim_team, chart, attack_types)
    overlap = stack_overlap_penalty(sim_cov)
    if overlap == 0:
        return True
    try:
        sim_infos = team_infos_from_cache(sim_team)
        sim_overall, _ = predict_overall(sim_team, sim_infos, chart, attack_types)
    except Exception:
        # If we cannot score, err on the side of blocking overlap
        return False
    return sim_overall > 95


def typing_delta(team, add_types, chart, attack_types, base_cov=None, base_score=None):
    """Return defensive delta when adding typing(s) to the team, using actual team rating."""
    if base_cov is None:
        base_cov = compute_coverage(team, chart, attack_types)
    if base_score is None:
        base_score = typing_score(base_cov)
    sim_cov = compute_coverage(
        team + [{"name": "sim", "types": add_types, "source": "sim"}], chart, attack_types
    )
    sim_score = typing_score(sim_cov)
    # Penalize newly introduced exposures/stacking; reward immunizing/resisting exposed types.
    base_cov_map = {c["attack"]: c for c in base_cov}
    new_exposed = 0
    immune_gain = 0
    resist_gain = 0
    new_weak = 0
    new_resist = 0
    for sc in sim_cov:
        bc = base_cov_map.get(sc["attack"], {"weak": 0, "resist": 0, "immune": 0})
        was_exposed = bc["weak"] > (bc["resist"] + bc["immune"])
        now_exposed = sc["weak"] > (sc["resist"] + sc["immune"])
        if now_exposed and not was_exposed:
            new_exposed += 1
        if was_exposed and sc["immune"] > bc["immune"]:
            immune_gain += 1
        if was_exposed and sc["resist"] > bc["resist"]:
            resist_gain += 1
        # Track net resist vs weak creation
        new_weak += max(0, sc["weak"] - bc["weak"])
        new_resist += max(0, sc["resist"] - bc["resist"])
    stack_delta = stack_overlap_penalty(sim_cov) - stack_overlap_penalty(base_cov)
    penalty = new_exposed * 14 + max(0, stack_delta) * 10 + max(0, new_weak - new_resist) * 6
    bonus = immune_gain * 10 + resist_gain * 4 + max(0, new_resist - new_weak) * 2
    sim_score = sim_score - penalty + bonus
    return sim_score - base_score, sim_score, base_score


def best_defensive_improvement(team, chart, attack_types):
    """Return a string suggestion for the best single or dual typing to reduce weaknesses (defensive delta)."""
    base_cov = compute_coverage(team, chart, attack_types)
    base_score = typing_score(base_cov)
    # rec_scores like coverage_report
    weak_gaps = [c for c in base_cov if c["weak"] > (c["resist"] + c["immune"])]
    rec_scores = []
    for def_type in attack_types:
        score = 0
        for g in weak_gaps:
            mult = chart[g["attack"]].get(def_type, 1.0)
            severity = max(0.5, g["weak"] - (g["resist"] + g["immune"]))
            if mult == 0:
                score += 1.5 * severity
            elif mult < 1:
                score += 1 * severity
        if score > 0:
            rec_scores.append((score, def_type))
    rec_scores.sort(reverse=True, key=lambda x: (x[0], x[1]))

    best = None  # (delta, label, options)

    # monotype sims
    for _, t in rec_scores:
        delta, _, _ = typing_delta(team, [t], chart, attack_types, base_cov=base_cov, base_score=base_score)
        if best is None or delta > best[0]:
            opts = fetch_single_type_candidates(t, current_team=team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types)
            best = (delta, f"Single-type ({t}) delta {delta:+.0f}", opts)

    # dual sims among top 4 rec_scores
    top_types = [t for _, t in rec_scores[:4]]
    for i in range(len(top_types)):
        for j in range(i + 1, len(top_types)):
            pair = sorted((top_types[i], top_types[j]))
            delta, _, _ = typing_delta(team, list(pair), chart, attack_types, base_cov=base_cov, base_score=base_score)
            if delta > (best[0] if best else -999):
                opts = fetch_dual_candidates(
                    pair[0],
                    pair[1],
                    current_team=team,
                    version_group=VERSION_GROUP,
                    chart=chart,
                attack_types=attack_types,
                stat_sort_key="defense"
            )
                best = (delta, f"Dual-type ({pair[0]} + {pair[1]}) delta {delta:+.0f}", opts)

    if best is None:
        return "Defensive improvement suggestion: none (no better types found)."
    delta, label, opts = best
    opts_str = ", ".join(opts) if opts else "none found"
    return f"Defensive improvement suggestion: {label} -> {opts_str}"


def pick_defensive_addition(team, chart, attack_types):
    """Return best defensive addition as (scores, label, pname, types) or None."""
    base_cov = compute_coverage(team, chart, attack_types)
    base_score = typing_score(base_cov)
    base_infos = team_infos_from_cache(team)
    try:
        base_overall, _ = predict_overall(team, base_infos, chart, attack_types)
    except Exception:
        base_overall = 0
    best = None  # (delta, uplift, label, pname, types)
    for t in TYPE_POOL:
        opts = fetch_single_type_candidates(
            t, current_team=team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types, stat_sort_key=" total )
 # Consider top 3 candidates per type for breadth and stat tie-breaks
 count_single = 0
 for pname in (opts or [])[:3]:
 count_single += 1
 loop_progress(\overall single candidates\, count_single, freq=25)
 try:
 ptypes = fetch_pokemon_typing(pname)
 except Exception:
 ptypes = [t]
 consider(pname, ptypes)

 seen_pairs = set()
 count_dual = 0
 for i in range(len(TYPE_POOL)):
 for j in range(i + 1, len(TYPE_POOL)):
 pair = tuple(sorted((TYPE_POOL[i], TYPE_POOL[j])))
 if pair in seen_pairs:
 continue
 seen_pairs.add(pair)
 opts = fetch_dual_candidates(
 pair[0], pair[1], current_team=team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types, stat_sort_key=	otal )
 for pname in (opts or [])[:3]:
 count_dual += 1
 loop_progress(\overall dual candidates\, count_dual, freq=25)
 try:
 ptypes = fetch_pokemon_typing(pname)
 except Exception:
 ptypes = list(pair)
 consider(pname, ptypes)
    if not best_strategic_pick:
        return (0.0, 0.0, 0.0), None, None, None, None, None, None

    # Now, compare the best_strategic_pick with highest_bst_candidate
    highest_bst_loser_name = None
    highest_bst_loser_bst = 0

    if highest_bst_candidate is not None and best_strategic_pick[4] != highest_bst_candidate[1]: # If different Pokémon are chosen
        highest_bst_loser_name = highest_bst_candidate[1]
        highest_bst_loser_bst = highest_bst_candidate[0]
            
    _ranked_gain, _sim_offense, _stat_total, label, pname, types = best_strategic_pick
    return (
        (0.0, _ranked_gain, _sim_offense),
        label,
        pname,
        types,
        highest_bst_loser_name,
        highest_bst_loser_bst,
        best_reason_line,
    )


def suggestion_buckets(team, cov, chart, attack_types):
    """Generate defensive/offensive/overall suggestion lines; return (lines, best_defensive_delta_available)."""
    # Helper to keep top N but include all items tied with the last slot (can exceed N).
    def select_with_ties(items, limit, key=lambda x: x[0]):
        if not items:
            return []
        if len(items) <= limit:
            return list(items)
        threshold = key(items[limit - 1])
        top = list(items[:limit])
        idx = limit
        while idx < len(items) and key(items[idx]) == threshold:
            top.append(items[idx])
            idx += 1
        return top

    base_score = typing_score(cov)
    base_totals = coverage_totals(cov)
    # Collect deltas for singles and duals
    positive_singles = []
    missing_types = []
    all_singles = []
    for t in TYPE_POOL:
        delta, _, _ = typing_delta(team, [t], chart, attack_types, base_cov=cov, base_score=base_score)
        opts = fetch_single_type_candidates(t, current_team=team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types)
        all_singles.append((delta, t, opts))
        if delta > 0:
            if opts:
                positive_singles.append((delta, t, f"Single-type {t} delta {delta:+.0f}: " + ", ".join(opts), [t]))
            else:
                missing_types.append((delta, f"Single-type {t} delta {delta:+.0f} (no available Pokemon)"))

    positive_duals = []
    missing_duals = []
    seen_pairs = set()
    for i in range(len(TYPE_POOL)):
        for j in range(i + 1, len(TYPE_POOL)):
            pair = tuple(sorted((TYPE_POOL[i], TYPE_POOL[j])))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            delta, _, _ = typing_delta(team, list(pair), chart, attack_types, base_cov=cov, base_score=base_score)
            if delta <= 0:
                continue
            opts = fetch_dual_candidates(
                pair[0],
                pair[1],
                current_team=team,
                version_group=VERSION_GROUP,
                chart=chart,
                attack_types=attack_types,
            )
            if opts:
                positive_duals.append(
                    (delta, f"Dual-type {pair[0]} + {pair[1]} delta {delta:+.0f}: " + ", ".join(opts), list(pair))
                )
            else:
                missing_duals.append(
                    (delta, f"Dual-type {pair[0]} + {pair[1]} delta {delta:+.0f} (no available Pokemon)")
                )

    positives = sorted(
        [(d, l, types) for d, _, l, types in positive_singles] + positive_duals,
        key=lambda x: x[0],
        reverse=True,
    )
    best_defensive_delta_available = positives[0][0] if positives else 0

    # Cache best-delta calculations per simulated team (hashable by typing signature)
    best_defensive_delta_cache = {}

    def team_signature(sim_team):
        sig_parts = []
        for member in sim_team:
            types = member.get("types") or []
            sig_parts.append(tuple(types))
        return tuple(sorted(sig_parts))

    def best_defensive_delta_for_team(sim_team):
        sig = team_signature(sim_team)
        if sig in best_defensive_delta_cache:
            return best_defensive_delta_cache[sig]
        base_cov_local = compute_coverage(sim_team, chart, attack_types)
        base_score_local = typing_score(base_cov_local)
        best_local = 0
        for t in TYPE_POOL:
            delta_local, _, _ = typing_delta(
                sim_team, [t], chart, attack_types, base_cov=base_cov_local, base_score=base_score_local
            )
            if delta_local <= 0:
                continue
            best_local = max(best_local, delta_local)
        seen_pairs_local = set()
        for i in range(len(TYPE_POOL)):
            for j in range(i + 1, len(TYPE_POOL)):
                pair_local = tuple(sorted((TYPE_POOL[i], TYPE_POOL[j])))
                if pair_local in seen_pairs_local:
                    continue
                seen_pairs_local.add(pair_local)
                delta_local, _, _ = typing_delta(
                    sim_team, list(pair_local), chart, attack_types, base_cov=base_cov_local, base_score=base_score_local
                )
                if delta_local <= 0:
                    continue
                best_local = max(best_local, delta_local)
        best_defensive_delta_cache[sig] = best_local
        return best_local

    lines = []
    base_infos = team_infos_from_cache(team)

    def defensive_impact(add_types):
        sim_cov = compute_coverage(
            team + [{"name": "sim", "types": add_types, "source": "sim"}], chart, attack_types
        )
        sim_totals = coverage_totals(sim_cov)
        dweak = int(sim_totals["weak"] - base_totals["weak"])
        dres = int(sim_totals["resist"] - base_totals["resist"])
        dimm = int(sim_totals["immune"] - base_totals["immune"])
        return f"(weak {dweak:+}, resist {dres:+}, immune {dimm:+})"

    # Defensive bucket
    def_top = []
    for delta, line, _types in positives:
        if delta <= 0:
            continue
        if "no available Pokemon" in line or "none found" in line:
            continue
        def_top.append((delta, line, _types))
    def_top.sort(key=lambda x: x[0], reverse=True)
    def_top = select_with_ties(def_top, 3, key=lambda x: x[0])
    if def_top:
        for idx, (_, line, tps) in enumerate(def_top, start=1):
            impact = defensive_impact(tps)
            text = f"{line} {impact}"
            if idx == 1:
                text = f"[BEST DEF] {text}"
            lines.append(f"\033[32m{text}\033[0m")
    else:
        lines.append("[32mBalanced (no defensive gains left; stacked weaknesses may still lower defense score).[0m")

    # Offense bucket (orange)
    def current_move_types():
        mts = set()
        for member in team:
            key = board_cache_key(member.get("name", ""), member.get("level_cap"))
            cached = BOARD_CACHE.get(key) or BOARD_CACHE.get((key[0], key[1]))
            if cached:
                _populate_move_data(cached["info"], cached_entry=cached) # Add this line
                mts.update(cached["info"].get("move_types") or []) # Update here
        return mts

    base_move_types = current_move_types()
    base_offense = offense_score_with_bonuses(base_infos, cov, chart, attack_types)
    base_cov_map = {c["attack"]: c for c in cov}
    top_exposures = [c["attack"] for c in sorted(cov, key=lambda c: c["weak"], reverse=True) if c["weak"] > 0][:3]

    # Build offense candidates independently of defensive deltas
    offense_candidates = []
    for t in TYPE_POOL:
        opts = fetch_single_type_candidates(t, current_team=team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types)
        for pname in opts or []:
            offense_candidates.append((pname, [t], f"Single-type {t}"))
    seen_pairs_off = set()
    for i in range(len(TYPE_POOL)):
        for j in range(i + 1, len(TYPE_POOL)):
            pair = tuple(sorted((TYPE_POOL[i], TYPE_POOL[j])))
            if pair in seen_pairs_off:
                continue
            seen_pairs_off.add(pair)
            opts = fetch_dual_candidates(
                pair[0],
                pair[1],
                current_team=team,
                version_group=VERSION_GROUP,
                chart=chart,
                attack_types=attack_types,
            )
            for pname in opts or []:
                offense_candidates.append((pname, list(pair), f"Dual-type {pair[0]} + {pair[1]}"))

    off_top = []
    seen_off_picks = set()
    for pname, types, label in offense_candidates:
        if pname in seen_off_picks:
            continue
        try:
            cached = cache_draft_board(pname)
            _populate_move_data(cached["info"], cached_entry=cached) # Add this line
            candidate_move_types = set(cached["info"].get("move_types") or []) # Update here
            info = cached["info"]
        except Exception:
            candidate_move_types = set()
            info = {"name": pname, "types": types, "suggested_moves": []}
        try:
            if not info.get("suggested_moves") and candidate_move_types:
                # Populate synthetic moves so offense scoring can reflect coverage.
                info = dict(info)
                # Use a limited set of top coverage types to avoid over-crediting huge move pools.
                prioritized = []
                se_hits = cached["info"].get("se_hits") if 'cached' in locals() else []
                for t in se_hits or []:
                    if t in candidate_move_types and t not in prioritized:
                        prioritized.append(t)
                for t in sorted(candidate_move_types):
                    if t not in prioritized:
                        prioritized.append(t)
                limited_types = []
                for t in prioritized:
                    if t not in limited_types:
                        limited_types.append(t)
                    if len(limited_types) >= 3:
                        break
                info["suggested_moves"] = [{"name": f"{t}-coverage", "type": t} for t in limited_types]
            move_types = set(base_move_types) | set(m["type"] for m in info.get("suggested_moves", []))
            sim_infos = base_infos + [info]
            sim_cov = compute_coverage(team + [{"name": pname, "types": types, "source": "sim"}], chart, attack_types)
            sim_offense = offense_score_with_bonuses(sim_infos, sim_cov, chart, attack_types)
            gain = sim_offense - base_offense
            neutral, se_types = offense_projection(move_types, chart, attack_types)
            stat_total = pokemon_base_stat_total(pname)
            # Emphasize closing exposed weaknesses (highest) and adding new elements (second), stacked multiplicatively.
            closed_weak = 0.0
            for sc in sim_cov:
                base_c = base_cov_map.get(sc["attack"])
                if not base_c:
                    continue
                base_exposed = base_c["weak"] > (base_c["resist"] + base_c["immune"])
                sim_exposed = sc["weak"] > (sc["resist"] + sc["immune"])
                if base_exposed and not sim_exposed:
                    closed_weak += 1.0
                elif base_exposed and sc["weak"] < base_c["weak"]:
                    closed_weak += 0.5
            new_types = move_types - base_move_types
            gain_factor = (1 + 1.5 * closed_weak) * (1 + 0.4 * len(new_types))
            bst_factor = max(0.75, min(1.45, 0.65 + stat_total / 800.0))
            se_factor = 1.0 + 0.08 * min(6, len(se_types))
            coverage_penalty = 0.85 if neutral >= (len(attack_types) - 1) and len(se_types) < 5 else 1.0
            ranked_gain = gain * gain_factor * bst_factor * se_factor * coverage_penalty
            off_top.append(
                (
                    ranked_gain,
                    sim_offense,
                    stat_total,
                    f"Offense {pname}: offense {sim_offense}/100 (gain {gain:+.0f}); hits {neutral} types >= neutral; SE: {', '.join(se_types[:5]) if se_types else 'none'}",
                )
            )
            seen_off_picks.add(pname)
        except Exception:
            continue
        # Normalize order before filtering: prioritize actual offense, then ranked gain, then BST
        off_top.sort(key=lambda x: (x[1], x[0], x[2]), reverse=True)
        # Prefer positive gains; if none, fall back to raw list
        positives_off = [o for o in off_top if o[0] > 0]
        off_candidates = positives_off if positives_off else off_top
        off_candidates.sort(key=lambda x: (x[1], x[0], x[2]), reverse=True)
        # If multiple entries tie for the best offense score, show all of them (ignore limit)
        display_off = []
        if off_candidates:
            best_offense_score = off_candidates[0][1]
            tied_best_offense = [o for o in off_candidates if o[1] == best_offense_score]
            if len(tied_best_offense) > 1:
                # If more than 3 tie for first, keep only the strongest by gain/stat to avoid huge blocks.
                tied_best_offense.sort(key=lambda x: (x[1], x[0], x[2]), reverse=True)
                display_off = tied_best_offense[:3]
            else:
                # Otherwise show top 3 (with gain ties)
                display_off = select_with_ties(off_candidates, 3, key=lambda x: x[0])
            display_off.sort(key=lambda x: (x[1], x[0], x[2]), reverse=True)
        if display_off:
            lines.append("Top offense lifts:")
            for _, _, _, line in display_off:
                lines.append(f"\033[33m{line}\033[0m")
        else:
            lines.append("Top offense lifts: none (no offensive gains).")

        return lines, best_defensive_delta_available

def coverage_report(team, chart, attack_types):
    # Pre-cache draft boards for current team to avoid re-fetching later and surface offense hints early
    for member in team:
        try:
            cache_draft_board(member.get("name", ""), level_cap=member.get("level_cap"))
        except Exception:
            continue
    cov = compute_coverage(team, chart, attack_types)
    exposure_floor = 0.5
    exposure_gap = lambda c: c["weak"] - (c["resist"] + c["immune"])
    weak_gaps = [c for c in cov if exposure_gap(c) >= exposure_floor]
    weak_gaps.sort(key=lambda c: exposure_gap(c), reverse=True)
    need_offense = [c for c in cov if c["weak"] > 0]
    report_lines = []
    report_lines.append(f"Team size with typing: {sum(1 for m in team if m['types'])}")
    report_lines.append("Top exposure (weak > resist+immune):")
    if weak_gaps:
        for c in weak_gaps[:6]:
            report_lines.append(
                f" - {c['attack']} weak {c['weak']} vs resist+immune {c['resist']+c['immune']}"
            )
    else:
        report_lines.append(" - None (no net exposure)")

    # Rating engine: already computed suggestion buckets; use returned best_defensive_delta_available for rating
    suggestion_lines, best_defensive_delta_available = suggestion_buckets(team, cov, chart, attack_types)
    report_lines.extend(suggestion_lines)

    # Typing rating (defense only here)
    total_weak = sum(c["weak"] for c in cov)
    total_resist = sum(c["resist"] for c in cov)
    total_immune = sum(c["immune"] for c in cov)
    net_exposed = sum(1 for c in cov if c["weak"] > (c["resist"] + c["immune"]))
    stack_overlap = sum(max(0, c["weak"] - 1) for c in cov)
    def_score = typing_score(cov)

    # Rating: 100 when no positive delta; otherwise 100 minus the highest positive delta.
    rating_score = max(0, min(100, 100 - best_defensive_delta_available))

    # Importance: drop each member and see impact; report ties for least critical
    def score_for_team(team_variant):
        vcov = compute_coverage(team_variant, chart, attack_types)
        return typing_score(vcov)

    drop_deltas = []
    base_score = typing_score(cov)
    for idx, member in enumerate(team):
        if not member["types"]:
            continue
        variant = [dict(m) for m in team]
        variant[idx] = {"name": "", "types": [], "source": ""}
        variant_score = score_for_team(variant)
        drop_deltas.append((base_score - variant_score, member["name"] or f"slot {idx+1}"))

    if drop_deltas:
        min_delta = min(d for d, _ in drop_deltas)
        tied_last = sorted(name for d, name in drop_deltas if abs(d - min_delta) < 1e-6)
        report_lines.append(f"Least critical (tied): {', '.join(tied_last)} (delta {min_delta:+.0f})")

    # Exposure/resist summary
    sorted_weak = sorted(cov, key=lambda c: c["weak"], reverse=True)
    sorted_resist = sorted(cov, key=lambda c: (c["resist"] + c["immune"]), reverse=True)
    weak_lines = [
        f"{c['attack']} weak {c['weak']}/{c['size']}"
        for c in sorted_weak[:3]
        if c["weak"] > 0 and exposure_gap(c) >= exposure_floor
    ]
    resist_lines = [
        f"{c['attack']} resist+immune {c['resist']+c['immune']}/{c['size']}"
        for c in sorted_resist[:3]
        if (c["resist"] + c["immune"]) > 0
    ]
    if weak_lines:
        report_lines.append("Top exposure: " + "; ".join(weak_lines))
    if resist_lines:
        report_lines.append("Top resist/immune: " + "; ".join(resist_lines))

    report_lines.append(
        f"Typing rating: {rating_score}/100 (delta left on table {best_defensive_delta_available:+.0f}; weak {total_weak}, resist {total_resist}, immune {total_immune}, net exposed types {net_exposed})"
    )
    try:
        infos = team_infos_from_cache(team)
        overall_score_val, comps = predict_overall(team, infos, chart, attack_types)
        if show_suggestions:  # Only append if suggestions are shown
            report_lines.append(
                f"Typing-based Overall Preview (moves not yet factored): {overall_score_val}/100 "
                f"(def {comps.get('defense','?')}, off {comps.get('offense','?')}, stack {comps.get('stack_overlap','?')}, "
                f"delta remaining {comps.get('delta','?')}, headroom {comps.get('delta_headroom','?')}/100)"
            )
    except Exception:
        pass
    if stack_overlap > 0 and def_score < 80 and all("Balanced" in ln for ln in suggestion_lines if "Balanced" in ln):
        report_lines.append("Note: Team has stacked weaknesses, impacting its typing-based defensive score.")

    return "\n".join(report_lines), cov


def parse_name_level(raw):
    tokens = raw.split()
    level_tokens = [t for t in tokens if t.isdigit()]
    level_cap = int(level_tokens[-1]) if level_tokens else None
    name_tokens = [t for t in tokens if not t.isdigit()]
    name = " ".join(name_tokens).strip()
    return name, level_cap


def launch_wheel(team_data, wheel_path):
    # Write team to a temp json for the Tk app to load
    tmp_path = Path(wheel_path).with_name("team_payload.json")
    payload = {
        "team": team_data,
        "role_move_mix": ROLE_MOVE_MIX,
    }
    tmp_path.write_text(json.dumps(payload, indent=2))
    # launch Tk app with env var for payload
    env = os.environ.copy()
    env["TEAM_PAYLOAD_PATH"] = str(tmp_path)
    subprocess.Popen([sys.executable, wheel_path], env=env)
    print(f"Launched wheel GUI with team; payload at {tmp_path}")


def compute_best_defensive_delta(team, chart, attack_types):
    base_cov = compute_coverage(team, chart, attack_types)
    base_score = typing_score(base_cov)
    best = 0
    # singles
    for t in TYPE_POOL:
        delta, _, _ = typing_delta(team, [t], chart, attack_types, base_cov=base_cov, base_score=base_score)
        if delta > best:
            best = delta
    # duals
    seen = set()
    for i in range(len(TYPE_POOL)):
        for j in range(i + 1, len(TYPE_POOL)):
            pair = tuple(sorted((TYPE_POOL[i], TYPE_POOL[j])))
            if pair in seen:
                continue
            seen.add(pair)
            delta, _, _ = typing_delta(team, list(pair), chart, attack_types, base_cov=base_cov, base_score=base_score)
            if delta > best:
                best = delta
    return best


def compute_best_offense_gain(team, chart, attack_types):
    """Best offensive ranked_gain available given current team (matches offense bucket logic)."""
    try:
        base_infos = team_infos_from_cache(team)
        cov = compute_coverage(team, chart, attack_types)
        base_offense = offense_score_with_bonuses(base_infos, cov, chart, attack_types)
    except Exception:
        return 0
    def current_move_types():
        mts = set()
        for member in team:
            key = board_cache_key(member.get("name", ""), member.get("level_cap"))
            cached = BOARD_CACHE.get(key) or BOARD_CACHE.get((key[0], key[1]))
            if cached:
                _populate_move_data(cached["info"], cached_entry=cached) # Add this line
                mts.update(cached["info"].get("move_types") or []) # Update here
        return mts

    base_move_types = current_move_types()
    base_cov_map = {c["attack"]: c for c in cov}

    best_gain = 0.0
    offense_candidates = []
    for t in TYPE_POOL:
        opts = fetch_single_type_candidates(t, current_team=team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types)
        for pname in opts or []:
            offense_candidates.append((pname, [t]))
    seen_pairs_off = set()
    for i in range(len(TYPE_POOL)):
        for j in range(i + 1, len(TYPE_POOL)):
            pair = tuple(sorted((TYPE_POOL[i], TYPE_POOL[j])))
            if pair in seen_pairs_off:
                continue
            seen_pairs_off.add(pair)
            opts = fetch_dual_candidates(
                pair[0],
                pair[1],
                current_team=team,
                version_group=VERSION_GROUP,
                chart=chart,
                attack_types=attack_types,
            )
            for pname in opts or []:
                offense_candidates.append((pname, list(pair)))

    seen = set()
    for pname, types in offense_candidates:
        if pname in seen:
            continue
        seen.add(pname)
        try:
            cached = cache_draft_board(pname)
            _populate_move_data(cached["info"], cached_entry=cached) # Add this line
            candidate_move_types = set(cached["info"].get("move_types") or []) # Update here
            info = cached["info"]
        except Exception:
            candidate_move_types = set()
            info = {"name": pname, "types": types, "suggested_moves": []}
        try:
            if not info.get("suggested_moves") and candidate_move_types:
                info = dict(info)
                prioritized = []
                se_hits = cached["info"].get("se_hits") if 'cached' in locals() else []
                for t in se_hits or []:
                    if t in candidate_move_types and t not in prioritized:
                        prioritized.append(t)
                for t in sorted(candidate_move_types):
                    if t not in prioritized:
                        prioritized.append(t)
                limited_types = []
                for t in prioritized:
                    if t not in limited_types:
                        limited_types.append(t)
                    if len(limited_types) >= 3:
                        break
                info["suggested_moves"] = [{"name": f"{t}-coverage", "type": t} for t in limited_types]
            move_types = set(base_move_types) | set(m["type"] for m in info.get("suggested_moves", []))
            sim_infos = base_infos + [info]
            sim_cov = compute_coverage(team + [{"name": pname, "types": types, "source": "sim"}], chart, attack_types)
            sim_offense = offense_score_with_bonuses(sim_infos, sim_cov, chart, attack_types)
            gain = sim_offense - base_offense
            neutral, se_types = offense_projection(move_types, chart, attack_types)
            closed_weak = 0.0
            for sc in sim_cov:
                base_c = base_cov_map.get(sc["attack"])
                if not base_c:
                    continue
                base_exposed = base_c["weak"] > (base_c["resist"] + base_c["immune"])
                sim_exposed = sc["weak"] > (sc["resist"] + sc["immune"])
                if base_exposed and not sim_exposed:
                    closed_weak += 1.0
                elif base_exposed and sc["weak"] < base_c["weak"]:
                    closed_weak += 0.5
            new_types = move_types - base_move_types
            gain_factor = (1 + 1.5 * closed_weak) * (1 + 0.4 * len(new_types))
            stat_total = pokemon_offense_stat_total(pname)
            bst_factor = max(0.75, min(1.45, 0.65 + stat_total / 350.0))
            se_factor = 1.0 + 0.08 * min(6, len(se_types))
            coverage_penalty = 0.85 if neutral >= (len(attack_types) - 1) and len(se_types) < 5 else 1.0
            ranked_gain = gain * gain_factor * bst_factor * se_factor * coverage_penalty
            if ranked_gain > best_gain:
                best_gain = ranked_gain
        except Exception:
            continue
    return best_gain


def team_infos_from_cache(team):
    """Build minimal team_infos using cached draft boards when available, ensuring move data is populated."""
    infos = []
    for member in team:
        name = member.get("name", "")
        level_cap = member.get("level_cap")
        cache_key = board_cache_key(name, level_cap)
        cached = BOARD_CACHE.get(cache_key) or BOARD_CACHE.get((cache_key[0], cache_key[1]))
        if cached:
            _populate_move_data(cached["info"], cached_entry=cached) # Ensure move data is populated
            infos.append(cached["info"])
        else:
            # If not in cache, create a basic info dict.
            # Move data will be fetched later if needed.
            infos.append({"name": name, "types": member.get("types") or [], "suggested_moves": []})
    return infos


def shared_weak_score(cov):
    """Score that heavily penalizes overlapping weaknesses."""
    if not cov:
        return 100
    max_weak = max(c["weak"] for c in cov)
    overlap = max(0, max_weak - 1)
    stack = sum(max(0, c["weak"] - 1) for c in cov)
    if stack == 1:
        stack = 0
    exposed = sum(1 for c in cov if c["weak"] > (c["resist"] + c["immune"]))
    score = 100 - (overlap * 18) - (stack * 7) - (exposed * 5)
    return max(0, min(100, int(score)))


def offense_score_with_bonuses(team_infos, cov, chart, attack_types):
    """Offense score: start from a strong offense baseline and subtract gaps from neutral/SE coverage."""
    move_types = set()
    for info in team_infos:
        for m in info.get("suggested_moves", []):
            if m.get("type"):
                move_types.add(m["type"])
    if not move_types:
        return 0

    total_types = len(attack_types)
    neutral, se_types = offense_projection(move_types, chart, attack_types)
    se_target = 16  # tougher SE breadth target

    neutral_gap = max(0, total_types - neutral)
    se_gap = max(0, se_target - len(se_types))

    # Extra penalty if a currently exposed defensive type is not covered at least neutral.
    exposed_types = {c["attack"] for c in cov if c["weak"] > (c["resist"] + c["immune"])}
    uncovered_exposed = 0
    for t in exposed_types:
        best = max(chart[atk_type].get(t, 1.0) for atk_type in move_types)
        if best < 1.0:
            uncovered_exposed += 1

    # Penalize limited type breadth to avoid easy 100 saturation
    breadth_penalty = max(0, 4 - len(move_types)) * 3.0

    # Penalize low offensive stats (Atk + SpA)
    off_stats_total = 0
    for info in team_infos:
        off_stats_total += pokemon_offense_stat_total(info.get("name", ""))
    avg_off_stats = off_stats_total / max(1, len(team_infos))
    off_stat_penalty = max(0, 180 - avg_off_stats) * 0.15  # small nudge; typical strong attacker ~220-260

    penalty = neutral_gap * 3.5 + se_gap * 4.0 + uncovered_exposed * 6.0 + breadth_penalty + off_stat_penalty
    off_score = max(0, min(100, 100 - penalty))
    return int(off_score)


def predict_overall(team, team_infos, chart, attack_types):
    """Compute overall score for a simulated team."""
    cov = compute_coverage(
        [{"name": m.get("name", ""), "types": m.get("types") or [], "source": m.get("source", "")} for m in team],
        chart,
        attack_types,
    )
    def_score = typing_score(cov)
    shared_score = shared_weak_score(cov)
    stack_overlap = sum(max(0, c["weak"] - 1) for c in cov)
    best_defensive_delta = compute_best_defensive_delta(
        [{"name": m.get("name", ""), "types": m.get("types") or [], "source": m.get("source", "")} for m in team],
        chart,
        attack_types,
    )
    defensive_delta_headroom = max(0, min(100, 100 - best_defensive_delta))
    off_score = offense_score_with_bonuses(team_infos, cov, chart, attack_types)
    best_offense_gap = compute_best_offense_gain(team, chart, attack_types)
    overall = overall_score(
        best_defensive_delta,
        best_offense_gap,
        shared_score,
        stack_overlap=stack_overlap,
    )
    components = {
        "defense": def_score,
        "offense": off_score,
        "shared": shared_score,
        "delta": best_defensive_delta,
        "delta_headroom": defensive_delta_headroom,
        "offensive_delta": best_offense_gap,
        "stack_overlap": stack_overlap,
        "best_defensive_delta": best_defensive_delta,
        "cov": cov,
    }
    return overall, components


def overall_score(best_defensive_delta, best_offense_gap, shared_score, stack_overlap=0):
    """
    Overall score: 100 if both deltas are zero and no stacked weaknesses,
    then lose 0.5 point per remaining delta point and 5 points per stacked weakness.
    """
    delta_penalty = 0.5 * (best_defensive_delta + best_offense_gap)
    stack_penalty = 5.0 * stack_overlap
    overall = 100 - delta_penalty - stack_penalty
    return int(max(0, min(100, overall)))


def coverage_totals(cov):
    return {
        "weak": sum(c["weak"] for c in cov),
        "resist": sum(c["resist"] for c in cov),
        "immune": sum(c["immune"] for c in cov),
    }


def offense_projection(move_types, chart, attack_types):
    """Return (count >= neutral, list of SE types) for a move type set."""
    if not move_types:
        return 0, []
    se_types = []
    neutral_or_better = 0
    for def_type in attack_types:
        best = 1.0
        for atk_type in move_types:
            best = max(best, chart.get(atk_type, {}).get(def_type, 1.0))
        if best >= 1.0:
            neutral_or_better += 1
        if best >= 2.0:
            se_types.append(def_type)
    return neutral_or_better, se_types


def exposure_coverage_bonus(move_types, chart, top_exposures):
    """Return a coverage bonus based on how many top exposures are hit SE."""
    if not move_types or not top_exposures:
        return 0.0
    se_hits = 0
    for def_type in top_exposures:
        best = 1.0
        for atk_type in move_types:
            best = max(best, chart.get(atk_type, {}).get(def_type, 1.0))
        if best >= 2.0:
            se_hits += 1
    # +3 per SE hit on top exposures, +4 extra if all top exposures are covered
    bonus = 3.0 * se_hits
    if se_hits == len(top_exposures) and top_exposures:
        bonus += 4.0
    return bonus


def pick_overall_addition(team, chart, attack_types, allow_overlap: bool = False):
    """Return best overall uplift using unified metric; fallback to best overall if no uplift.
    Set allow_overlap=True to relax overlap blocking (used as last resort)."""
    base_infos = team_infos_from_cache(team)
    base_overall, base_comps = predict_overall(team, base_infos, chart, attack_types)
    base_cov = base_comps.get("cov") or compute_coverage(team, chart, attack_types)
    base_cov_map = {c["attack"]: c for c in base_cov}
    base_top_exposures = [
        c["attack"] for c in sorted(base_cov, key=lambda c: c["weak"], reverse=True) if c["weak"] > 0
    ][:3]

    def collect_move_types(infos):
        mts = set()
        for info in infos:
            for m in info.get("suggested_moves", []):
                if m.get("type"):
                    mts.add(m["type"])
        return mts

    base_move_types = collect_move_types(base_infos)
    
    best_strategic_pick = None  # (compare_tuple, uplift, line, pname, ptypes, sim_score)
    highest_bst_candidate = None # (stat_total, pname) - for pure BST comparison

    def sim_overall(pname, ptypes):
        try:
            cached = cache_draft_board(pname)
            _populate_move_data(cached["info"], cached_entry=cached) # Add this line
            info = cached["info"]
            candidate_move_types = set(cached["info"].get("move_types") or []) # Update here
            alignment_score = cached["info"].get("alignment_score", 0) # Update here
        except Exception:
            info = {"name": pname, "types": ptypes, "suggested_moves": []}
            candidate_move_types = set()
            alignment_score = 0
        sim_team = team + [{"name": pname, "types": ptypes, "source": "sim"}]
        sim_infos = base_infos + [info]
        sim_overall, comps = predict_overall(sim_team, sim_infos, chart, attack_types)
        uplift = sim_overall - base_overall
        line = (
            f"\u001b[36mOverall {pname}: {sim_overall:.0f}/100 (uplift {uplift:+.0f}; "
            f"def {comps.get('defense','?')}, off {comps.get('offense','?')}, stack {comps.get('stack_overlap','?')}, "
            f"delta {comps.get('delta','?')})\u001b[0m"
        )
        return uplift, sim_overall, line, comps, candidate_move_types, alignment_score

    def consider(pname, ptypes):
        uplift, sim_score, line, comps, candidate_move_types, alignment_score = sim_overall(pname, ptypes)
        dual_penalty = 2.0 if len(ptypes) == 2 else 0.0
        sim_team = team + [{"name": pname, "types": ptypes, "source": "sim"}]
        sim_cov = comps.get("cov") or compute_coverage(sim_team, chart, attack_types)
        overlap = stack_overlap_penalty(sim_cov)
        def_gain = typing_score(sim_cov) - typing_score(base_cov)
        shared_gain = shared_weak_score(sim_cov) - shared_weak_score(base_cov)
        stat_total = pokemon_base_stat_total(pname)
        if stat_total < 500:
            low_stat_penalty = 14.0
        elif stat_total < 550:
            low_stat_penalty = 8.0
        else:
            low_stat_penalty = 0.0
        stat_bonus = stat_total / 22.0
        alignment_bonus = (alignment_score / 22.0) * 0.5

        patched = 0
        for sc in sim_cov:
            base_c = base_cov_map.get(sc["attack"])
            if not base_c:
                continue
            base_exposed = base_c["weak"] > (base_c["resist"] + base_c["immune"])
            if base_exposed and sc["weak"] < base_c["weak"]:
                patched += 1

        coverage_bonus = exposure_coverage_bonus(
            base_move_types | candidate_move_types, chart, base_top_exposures
        )
        if allow_overlap:
            overlap_penalty = 12.0 * overlap
            compare_val = uplift - dual_penalty - overlap_penalty + (0.5 * patched) + (0.25 * coverage_bonus) + stat_bonus + alignment_bonus
            compare_tuple = (
                stat_total,
                def_gain,
                shared_gain,
                -overlap,
                patched,
                coverage_bonus,
                compare_val - low_stat_penalty,
                stat_total,
                sim_score,
            )
        else:
            overlap_blocked = overlap > 0 and sim_score <= 95
            compare_val = uplift + 0.35 * def_gain + 0.25 * shared_gain + stat_bonus - dual_penalty - low_stat_penalty + alignment_bonus
            if overlap_blocked:
                compare_val -= 500  # effectively sort blocked overlaps after any clean option
            compare_tuple = (compare_val, stat_total, def_gain, shared_gain, -overlap, sim_score)

        nonlocal best_strategic_pick, highest_bst_candidate
        if best_strategic_pick is None or compare_tuple > best_strategic_pick[0]:
            best_strategic_pick = (compare_tuple, uplift, line, pname, ptypes, sim_score)
        
        # Update highest_bst_candidate
        if highest_bst_candidate is None or stat_total > highest_bst_candidate[0]:
            highest_bst_candidate = (stat_total, pname)

    for t in TYPE_POOL:
        opts = fetch_single_type_candidates(
            t, current_team=team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types, stat_sort_key="total"
        )
        # Consider top 3 candidates per type for breadth and stat tie-breaks
        for idx, pname in enumerate((opts or [])[:3], start=1):
            loop_progress("overall single candidates", idx, freq=25, total=3)
            try:
                ptypes = fetch_pokemon_typing(pname)
            except Exception:
                ptypes = [t]
            consider(pname, ptypes)

    seen_pairs = set()
    dual_count = 0
    for i in range(len(TYPE_POOL)):
        for j in range(i + 1, len(TYPE_POOL)):
            pair = tuple(sorted((TYPE_POOL[i], TYPE_POOL[j])))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            opts = fetch_dual_candidates(
                pair[0], pair[1], current_team=team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types, stat_sort_key="total"
            )
            for pname in (opts or [])[:3]:
                dual_count += 1
                loop_progress("overall dual candidates", dual_count, freq=25)
                try:
                    ptypes = fetch_pokemon_typing(pname)
                except Exception:
                    ptypes = list(pair)
                consider(pname, ptypes)
    if not best_strategic_pick: # Use best_strategic_pick here
        # Final fallback: just pick any available final-form Pokemon not on the team
        # Simplified to guarantee a pick if one exists, bypassing complex scoring.
        final_forms_set = get_final_forms() # Get final forms once
        for p in ZA_POKEDEX:
            if p not in {m["name"] for m in team} and p in final_forms_set:
                try:
                    ptypes = fetch_pokemon_typing(p)
                    # Directly return this Pokémon as a fallback, with placeholder scores.
                    # The goal here is just to fill the team.
                    return (
                        (0.0, 0.0, 0.0),
                        f"Fallback Add: {p}",
                        p,
                        ptypes,
                        None,
                        None,
                        None,
                    )
                except Exception:
                    # If even fetching typing fails, skip this Pokemon.
                    continue
        return (0.0, 0.0, 0.0), None, None, None, None, None, None

    # Now, compare the best_strategic_pick with highest_bst_candidate
    highest_bst_loser_name = None
    highest_bst_loser_bst = 0

    if highest_bst_candidate is not None and best_strategic_pick[3] != highest_bst_candidate[1]: # best_strategic_pick[3] is pname
        highest_bst_loser_name = highest_bst_candidate[1]
        highest_bst_loser_bst = highest_bst_candidate[0]
            
    _compare_val, uplift, line, pname, ptypes, sim_score = best_strategic_pick
    # Score tuple normalized to (shared_gain, def_gain, overall_gain) for downstream printing
    return (
        (0.0, 0.0, uplift),
        line,
        pname,
        ptypes,
        highest_bst_loser_name,
        highest_bst_loser_bst,
        best_reason_line,
    )


def autofill_team(team, chart, attack_types, max_size=6):
    """Greedily add best-available overall improvements until team reaches max_size."""
    added = []
    iteration = 0
    while len(team) < max_size:
        iteration += 1
        log_verbose(f"[autofill] Start iteration {iteration}, current team size: {len(team)}")
        progress(f"Autofill iteration {iteration} (team size {len(team)})")

        best = None
        defensive_pick = pick_defensive_addition(team, chart, attack_types)
        offensive_pick = pick_offense_addition(team, chart, attack_types)
        overall_pick = pick_overall_addition(team, chart, attack_types, allow_overlap=True)

        # Prioritize defensive pick if it offers any positive gain
        if defensive_pick and (defensive_pick[0][0] > 0 or defensive_pick[0][1] > 0 or defensive_pick[0][2] > 0):
            best = defensive_pick
        # Else, prioritize offensive pick if it offers any positive gain
        elif offensive_pick and (offensive_pick[0][0] > 0 or offensive_pick[0][1] > 0 or offensive_pick[0][2] > 0):
            best = offensive_pick
        # Else, try the overall pick. If overall_pick is None, it means no valid Pokemon at all.
        elif overall_pick:
            best = overall_pick
        
        if not best:
            log_verbose("[autofill] no valid addition found. Stopping autofill.")
            break
        score_tuple, label, pname, types, *extra = best
        loser_name = extra[0] if len(extra) > 0 else None
        loser_bst = extra[1] if len(extra) > 1 else None
        reason_line = extra[2] if len(extra) > 2 else None
        
        try:
            ptypes = fetch_pokemon_typing(pname)
        except Exception as e:
            log_verbose(f"Failed to fetch typing for {pname}: {e}")
            continue

        if pname in {m["name"] for m in team}:
            log_verbose(f"[autofill] {pname} is already in the team (size {len(team)}), skipping addition.")
            continue

        try:
            winner_bst = pokemon_base_stat_total(pname)
        except Exception:
            winner_bst = None
        if (
            loser_name
            and loser_bst is not None
            and winner_bst is not None
            and winner_bst < loser_bst
        ):
            print(
                f"[Low Stat Win] {pname} (BST {winner_bst}) chosen over {loser_name} (BST {loser_bst}) "
                f"because {label} offered better gain."
            )

        if reason_line:
            print(f"[gain reason] {reason_line}")

        log_verbose(f"[autofill] Adding {pname} to team of size {len(team)}")
        print(f"Added {pname} via {label}")
        team.append({"name": pname, "types": ptypes, "source": "autofill"})
        log_verbose(f"[autofill] {pname} added, new team size: {len(team)}")
        added.append((pname, label, score_tuple))
    return added


def final_team_rating(team_infos, cov, chart, attack_types):
    # Defensive score
    total_weak = sum(c["weak"] for c in cov)
    total_resist = sum(c["resist"] for c in cov)
    total_immune = sum(c["immune"] for c in cov)
    net_exposed = sum(1 for c in cov if c["weak"] > (c["resist"] + c["immune"]))
    def_score = typing_score(cov)

    shared_score = shared_weak_score(cov)

    # Offensive score: blended current coverage + headroom (harder to reach 100)
    best_offense_gap = compute_best_offense_gain(
        [{"name": m.get("name", ""), "types": m.get("types") or [], "source": m.get("source", "")} for m in team_infos],
        chart,
        attack_types,
    )
    coverage_off = offense_score_with_bonuses(team_infos, cov, chart, attack_types)
    headroom_off = max(0, min(100, 100 - best_offense_gap))
    off_score = int(max(0, min(100, 0.55 * coverage_off + 0.45 * headroom_off)))
    move_types = set()
    for info in team_infos:
        for m in info.get("suggested_moves", []):
            if m.get("type"):
                move_types.add(m["type"])
    # Team base stat total
    stat_total = 0
    for info in team_infos:
        name = info.get("name", "")
        try:
            stat_total += pokemon_base_stat_total(name)
        except Exception:
            continue

    # Perfect team definition string
    perfect_def = "Perfect team: no net weaknesses (resist/immune >= weak for every attack type) AND offensive coverage can hit every type at least neutral, ideally super-effective."

    best_defensive_delta = compute_best_defensive_delta(
        [{"name": i["name"], "types": i["types"], "source": "final"} for i in team_infos],
        chart,
        attack_types,
    )
    defensive_delta_headroom = max(0, min(100, 100 - best_defensive_delta))
    
    offensive_delta = best_offense_gap
    stack_overlap = sum(max(0, c["weak"] - 1) for c in cov)
    overall = overall_score(
        best_defensive_delta,
        offensive_delta,
        shared_score,
        stack_overlap=stack_overlap,
    )

    scores = {
        "defense": def_score,
        "offense": off_score,
        "delta": best_defensive_delta,
        "delta_headroom": defensive_delta_headroom,
        "offensive_delta": offensive_delta,
        "shared": shared_score,
        "overall": overall,
        "perfect_text": perfect_def,
        "weak": total_weak,
        "resist": total_resist,
        "immune": total_immune,
        "net_exposed": net_exposed,
        "move_types": move_types,
        "best_defensive_delta": best_defensive_delta,
        "best_offense_gap": best_offense_gap,
        "coverage_offense": coverage_off,
        "headroom_offense": headroom_off,
        "stack_overlap": stack_overlap,
        "stat_total": stat_total,
    }
    summary = [
        perfect_def,
        f"Defensive score: {def_score}/100 (weak {total_weak}, resist {total_resist}, immune {total_immune}, net exposed types {net_exposed})",
        f"Offensive score: {off_score}/100 (coverage {coverage_off:.0f}, headroom {headroom_off:.0f}; best remaining offensive gain {best_offense_gap:+.0f}; move types: {', '.join(sorted(move_types)) if move_types else 'none'})",
        f"Shared-weakness score: {shared_score}/100 (penalizes overlapping weaknesses)",
        f"Defensive Delta headroom: {defensive_delta_headroom}/100 (best remaining defensive delta {best_defensive_delta:+.0f})",
        f"Offensive Delta (headroom): {100 - offensive_delta}/100 (best remaining offensive delta {offensive_delta:+.0f})",
        f"Overall team rating: {overall}/100",
        f"Team base stats total: {stat_total}",
    ]
    return "\n".join(summary), scores


def cache_draft_board(name: str, level_cap=None):
    """Fetch and cache basic Pokemon info, deferring move data fetching."""
    key = board_cache_key(name, level_cap=level_cap)
    cached = BOARD_CACHE.get(key)
    if not cached:
        legacy = (key[0], key[1])
        cached = BOARD_CACHE.get(legacy)
    if cached:
        BOARD_CACHE_STATS["hit"] += 1
        return cached
    BOARD_CACHE_STATS["miss"] += 1
    
    # Fetch only essential, readily available Pokémon data
    try:
        types = fetch_pokemon_typing(name)
    except Exception:
        types = []
    
    info = {
        "name": name.lower(),
        "types": types,
        "level_cap": level_cap,
        # Initialize placeholders for move-related fields
        "suggested_moves": [],
        "draft_board": [],  # pick_moves populates this
        "coverage_priority": [],  # pick_moves populates this
        "move_types": [],
        "se_hits": [],
        "role": None,
        "alignment_score": 0,
        "moves_fetched": False,
    }
    
    # Add a boolean flag to explicitly indicate that move data has not yet been loaded
    cached = {
        "info": info,
        "moves_fetched": False,
    }
    BOARD_CACHE[key] = cached
    _save_draft_cache()
    return cached

def _populate_move_data(
    info: dict,
    exclude_moves: set = None,
    used_moves: set = None,
    cached_entry: dict = None,
):
    """Lazily fetches and populates detailed move data for the provided Pokémon info."""
    global POKEMON_MOVES_FETCHED, TOTAL_POKEMON_FOR_MOVE_FETCH
    if info.get("moves_fetched"):
        return

    # Increment a global counter to support the consolidated progress bar.
    POKEMON_MOVES_FETCHED += 1
    if TOTAL_POKEMON_FOR_MOVE_FETCH > 0: # Avoid division by zero
        progress(f"Fetching moves for {info['name']} ({POKEMON_MOVES_FETCHED}/{TOTAL_POKEMON_FOR_MOVE_FETCH})...")
    else:
        progress(f"Fetching moves for {info['name']}...")


    if cached_entry is None:
        for cached in BOARD_CACHE.values():
            if cached.get("info") is info:
                cached_entry = cached
                break

    # Call the pick_moves function
    move_info = pick_moves(
        info["name"],
        level_cap=info.get("level_cap"),
        exclude_moves=exclude_moves or set(),
        used_moves=used_moves or set(),
        version_group=VERSION_GROUP,
    )

    # Populate info dictionary with results from pick_moves
    info["suggested_moves"] = move_info.get("suggested_moves", [])
    info["draft_board"] = move_info.get("draft_board", [])
    info["coverage_priority"] = move_info.get("coverage_priority", [])
    seen_types = []
    seen_types_set = set()
    for move in info.get("draft_board", []):
        move_type = move.get("type")
        if move_type and move_type not in seen_types_set:
            seen_types_set.add(move_type)
            seen_types.append(move_type)
    info["move_types"] = seen_types
    info["se_hits"] = [t for t, cnt in info.get("coverage_priority", []) if cnt > 0]
    info["role"] = move_info.get("role")
    info["alignment_score"] = move_info.get("alignment_score")

    # Set the flag to True
    info["moves_fetched"] = True
    if cached_entry is not None:
        cached_entry["moves_fetched"] = True



class TeeStream:
    """Mirror writes to multiple streams (stdout/file) and flush together."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, msg):
        for s in self.streams:
            try:
                s.write(msg)
                s.flush()
            except Exception:
                continue

    def flush(self):
        for s in self.streams:
            try:
                s.flush()
            except Exception:
                continue


def main():
    global VERBOSE
    VERBOSE = "--verbose" in sys.argv
    # force unbuffered stdout/stderr; write-through + line buffering
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(line_buffering=True, write_through=True)
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(line_buffering=True, write_through=True)
        except Exception:
            pass
    # Preload caches from disk to avoid redundant network calls
    _load_draft_cache()
    LOG_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "demo" if "--demo" in sys.argv else "run"
    log_path = LOG_DIR / f"{suffix}_{stamp}.log"
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    # line-buffered for live writes
    log_file = log_path.open("w", encoding="utf-8", buffering=1)
    sys.stdout = TeeStream(original_stdout, log_file)
    sys.stderr = TeeStream(original_stderr, log_file)
    print(f"Log start: {datetime.now().isoformat()}")
    print(f"Args: {' '.join(sys.argv)}")
    try:
        progress("Loading type chart...")
        chart, attack_types = fetch_type_chart()
        progress("Type chart ready.")
        team = []
        global_exclude = set()
        global_used = set()
        team_infos = []
        demo_mode = "--demo" in sys.argv
        if demo_mode:
            # Scripted inputs to keep demo non-interactive
            demo_inputs = iter(["next"])

            def demo_input(_prompt=""):
                try:
                    return next(demo_inputs)
                except StopIteration:
                    return "done"

            builtins.input = demo_input

        print("Team builder + move suggester. Commands: 'next' to move to moves, 'done' to finish, 'drop <name>' to remove, 'finalize' to auto-fill and continue.")

        def do_finalize():
            nonlocal team
            print("Finalizing team...")
            if len(team) < 6:
                print("Auto-filling remaining slots...")
                added = autofill_team(team, chart, attack_types, max_size=6)
                if added:
                    for name, label, score_tuple in added:
                        shared_gain, def_gain, overall_gain = score_tuple
                        print(
                            f"\033[32mAdded {name} via {label} "
                            f"(shared {shared_gain:+.0f}, def {def_gain:+.0f}, overall {overall_gain:+.0f})\033[0m"
                        )
                    report, cov = coverage_report(team, chart, attack_types)
                    print(report)
                else:
                    print("No positive additions available to auto-fill.")

            infos = team_infos_from_cache(team)
            wheel_path = Path(__file__).with_name("tk_team_builder.py")
            if wheel_path.exists():
                launch_wheel(infos, str(wheel_path))
            else:
                print("Wheel GUI not found; skipping GUI launch.")
            return True

        while True:
            raw = input("Add Pokemon (name [level]) or 'next' to move to moves: ").strip()
            if not raw:
                continue
            if raw.lower() == "next":
                # If we have a full team, show checkpoint summary
                if team:
                    report, cov = coverage_report(team, chart, attack_types)
                    print("\n=== Typing checkpoint ===")
                    print(report)
                break
            if raw.lower() == "finalize":
                if do_finalize():
                    break
            if raw.lower() == "done":
                break
            if raw.lower().startswith("drop"):
                parts = raw.split()
                if len(parts) >= 2:
                    drop_name = parts[1].lower()
                    team = [m for m in team if m["name"] != drop_name]
                    print(f"Dropped {drop_name}")
                continue
            if len(team) >= 6:
                print("Team already has 6 members. Use 'drop <name>' to remove one before adding more.")
                continue
            tokens = raw.split()
            finalize_after_add = False
            filtered_tokens = []
            for tok in tokens:
                if tok.lower() == "finalize":
                    finalize_after_add = True
                    continue
                filtered_tokens.append(tok)
            raw_filtered = " ".join(filtered_tokens)
            name, level_cap = parse_name_level(raw_filtered)
            if not name:
                print("Provide a Pokemon name.")
                continue
            try:
                types = fetch_pokemon_typing(name)
            except Exception as exc:
                print(f"Error fetching {name}: {exc}")
                continue
            team.append({"name": name.lower(), "types": types, "level_cap": level_cap})
            try:
                cached = cache_draft_board(name, level_cap=level_cap)
                _populate_move_data(cached["info"], cached_entry=cached) # Add this line
                mt_preview = ", ".join(sorted(cached["info"]["move_types"])) if cached["info"]["move_types"] else "none"
                se_preview = ", ".join(cached["info"]["se_hits"][:5]) if cached["info"]["se_hits"] else "none"
                role_label = cached["info"].get("role") or "n/a"
                print(f"Cached draft board for {name} (role {role_label}; move types: {mt_preview}; SE hits: {se_preview})")
                print(f"[progress] {name}: computing move suggestions (this can take a moment)...")
            except Exception as exc:
                if VERBOSE:
                    print(f"Draft cache failed for {name}: {exc}")
            report, cov = coverage_report(team, chart, attack_types)
            print(report)
            if len(team) >= 6:
                print("Team is full (6/6). Type 'next' to lock typings or 'drop <name>' to swap someone.")
            if finalize_after_add:
                if do_finalize():
                    break

        # Auto-fill before moves if team is undersized
        if team and len(team) < 6:
            print("Auto-filling remaining slots to reach 6 before move suggestions...")
            added = autofill_team(team, chart, attack_types, max_size=6)
            if added:
                for name, label, score_tuple in added:
                    shared_gain, def_gain, overall_gain = score_tuple
                    print(
                        f"\033[32mAdded {name} via {label} "
                        f"(shared {shared_gain:+.0f}, def {def_gain:+.0f}, overall {overall_gain:+.0f})\033[0m"
                    )
                report, cov = coverage_report(team, chart, attack_types)
                print(report)
            else:
                print("Auto-fill skipped: no positive additions available.")

        # Move suggestion phase
        if team:
            print("\n=== Before moves: defensive improvement check ===")
            print(best_defensive_improvement(team, chart, attack_types))
        print("\n=== Typing locked in. Proceeding to move suggestions ===")
        # Collect boards for draft
        boards = []
        global TOTAL_POKEMON_FOR_MOVE_FETCH, POKEMON_MOVES_FETCHED
        TOTAL_POKEMON_FOR_MOVE_FETCH = len(team) # Set total count
        POKEMON_MOVES_FETCHED = 0 # Reset fetched count

        for member in team:
            name = member["name"]
            level_cap = member.get("level_cap")
            cache_key = board_cache_key(name, level_cap)
            cached = BOARD_CACHE.get(cache_key) or BOARD_CACHE.get((cache_key[0], cache_key[1]))
            if cached:
                info = cached["info"]
                _populate_move_data(
                    info,
                    exclude_moves=global_exclude,
                    used_moves=global_used,
                    cached_entry=cached,
                )  # Ensure populated
            else:
                # If not cached at all, create a basic entry and then populate
                # This branch should ideally not be hit if all team members are processed by cache_draft_board earlier
                # but as a safeguard, ensure proper info dict is created.
                try:
                    types = fetch_pokemon_typing(name)
                except Exception:
                    types = []
                info = {
                    "name": name.lower(),
                    "types": types,
                    "level_cap": level_cap,
                    "suggested_moves": [],
                    "draft_board": [],
                    "coverage_priority": [],
                    "move_types": [],
                    "se_hits": [],
                    "role": None,
                    "alignment_score": 0,
                    "moves_fetched": False,
                }
                # Add to cache and then populate
                cached_entry = {"info": info, "moves_fetched": False}
                BOARD_CACHE[cache_key] = cached_entry
                _populate_move_data(
                    info,
                    exclude_moves=global_exclude,
                    used_moves=global_used,
                    cached_entry=cached_entry,
                )
                _save_draft_cache() # Save after population

            print(f"\nBuilding draft board for {name}...") # Moved print after potential fetch.
            boards.append(info)

        # Draft: 4 rounds, each mon picks best available from its board avoiding used/excluded
        assigned = {info["name"]: [] for info in boards}
        for _round in range(4):
            log_verbose(f"[draft] round {_round+1}")
            for info in boards:
                for mv in info.get("draft_board", []):
                    if mv["name"] in global_used or mv["name"] in global_exclude:
                        continue
                    if mv["name"] in [m["name"] for m in assigned[info["name"]]]:
                        continue
                    assigned[info["name"]].append(mv)
                    global_used.add(mv["name"])
                    log_verbose(f"[draft] {_round+1} {info['name']} picked {mv['name']}")
                    break

        # Apply assigned moves back to team_infos and print
        print("\n=== Draft results ===")
        for info in boards:
            picks = assigned.get(info["name"], [])
            info["suggested_moves"] = picks
            team_infos.append(info)
            mv_text = ", ".join(m["name"] for m in picks) if picks else "none"
            print(f"{info['name'].title()}: {mv_text}")

        # Final team summary + scores
        contrib_lines = []
        if team_infos:
            print("\nFinal team summary:")
            for info in team_infos:
                print(format_output(info))
                print("-" * 40)
            cov = compute_coverage(
                [{"name": i["name"], "types": i["types"], "source": "final"} for i in team_infos],
                chart,
                attack_types,
            )
            summary_text, scores = final_team_rating(team_infos, cov, chart, attack_types)
            print("\n=== Team Scores (final) ===")
            print(f" - Defense: {scores['defense']}/100")
            print(f" - Offense: {scores['offense']}/100")
            print(
                f" - Delta headroom: {scores['delta_headroom']}/100 "
                f"(best remaining delta {scores['delta']:+.0f})"
            )
            print(f" - Stack overlap: {scores.get('stack_overlap', 0)} (penalty applied in overall)")
            print(f" - Overall: {scores['overall']}/100")
            # Per-member defensive contribution
            baseline_def = scores["defense"]
            for idx, info in enumerate(team_infos):
                variant = [dict(m) for m in team_infos]
                variant[idx] = {"name": "", "types": [], "source": ""}
                vcov = compute_coverage(
                    [{"name": v["name"], "types": v["types"], "source": v.get("source", "")} for v in variant],
                    chart,
                    attack_types,
                )
                vscore = typing_score(vcov)
                contrib = baseline_def - vscore
                contrib_lines.append(f"   {info['name'].title()}: {contrib:+.0f}")
            print("Member defensive impact (higher = more critical):")
            for line in contrib_lines:
                print(line)
            print("\n=== Detailed breakdown ===")
            print(summary_text)
        # Upgrade pass: drop weakest, find up to 3 better replacements before launching GUI
            print("\n=== Upgrade pass: prune weakest and suggest replacements ===")
            if len(team_infos) < 6:
                print("Team not full; skipping drop/upgrade until 6 members are set.")
        if contrib_lines and len(team_infos) >= 6:
            impacts = []
            for idx, info in enumerate(team_infos):
                variant = [dict(m) for m in team_infos]
                variant[idx] = {"name": "", "types": [], "source": ""}
                vcov = compute_coverage(
                    [{"name": v["name"], "types": v["types"], "source": v.get("source", "")} for v in variant],
                    chart,
                    attack_types,
                )
                vscore = typing_score(vcov)
                contrib = baseline_def - vscore
                impacts.append((contrib, idx, info["name"]))
            impacts.sort(key=lambda x: (x[0], x[2]))
            weakest_idx = impacts[0][1]
            weakest_name = impacts[0][2]
            print("Defensive impacts (higher = more critical):")
            for contrib, _idx, nm in impacts:
                print(f" - {nm}: {contrib:+.0f}")
            print(f"Weakest (candidate drop): {weakest_name}")
            log_verbose(f"[upgrade] impacts sorted: {impacts}")
            core_team = [dict(m) for m in team_infos]
            core_team.pop(weakest_idx)
            core_cov = compute_coverage(
                [{"name": i["name"], "types": i["types"], "source": "core"} for i in core_team],
                chart,
                attack_types,
            )
            base_infos_core = team_infos_from_cache(core_team)
            base_overall_core, _ = predict_overall(core_team, base_infos_core, chart, attack_types)
            upgrades = []
            best_any = None  # track best even if uplift <= 0
            # singles (overall uplift)
            for t in TYPE_POOL:
                opts = fetch_single_type_candidates(t, current_team=core_team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types)
                for pname in opts:
                    try:
                        ptypes = fetch_pokemon_typing(pname)
                    except Exception:
                        ptypes = [t]
                    try:
                        cached = cache_draft_board(pname)
                        info = cached["info"]
                    except Exception:
                        info = {"name": pname, "types": ptypes, "suggested_moves": []}
                    sim_team = core_team + [{"name": pname, "types": ptypes, "source": "sim"}]
                    sim_infos = base_infos_core + [info]
                    sim_overall, comps = predict_overall(sim_team, sim_infos, chart, attack_types)
                    uplift = sim_overall - base_overall_core
                    if uplift > 0:
                        upgrades.append(
                            (
                                uplift,
                                f"\u001b[36mOverall {pname}: {sim_overall:.0f}/100 (uplift {uplift:+.0f}; def {comps.get('defense','?')}, off {comps.get('offense','?')}, shared {comps.get('shared','?')}, delta {comps.get('delta','?')})\u001b[0m",
                                info,
                            )
                        )
                    if best_any is None or sim_overall > best_any[0]:
                        best_any = (sim_overall, uplift, info, pname, comps)
                    log_verbose(
                        f"[upgrade] single candidate {pname} overall {sim_overall:.0f} uplift {uplift:+.0f} "
                        f"vs base {base_overall_core:.0f} (def {comps.get('defense','?')} off {comps.get('offense','?')} "
                        f"shared {comps.get('shared','?')} delta {comps.get('delta','?')})"
                    )
                    break
            # duals (overall uplift)
            seen_pairs = set()
            for i in range(len(TYPE_POOL)):
                for j in range(i + 1, len(TYPE_POOL)):
                    pair = tuple(sorted((TYPE_POOL[i], TYPE_POOL[j])))
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)
                    opts = fetch_dual_candidates(pair[0], pair[1], current_team=core_team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types)
                    for pname in opts:
                        try:
                            ptypes = fetch_pokemon_typing(pname)
                        except Exception:
                            ptypes = list(pair)
                        try:
                            cached = cache_draft_board(pname)
                            info = cached["info"]
                        except Exception:
                            info = {"name": pname, "types": ptypes, "suggested_moves": []}
                        sim_team = core_team + [{"name": pname, "types": ptypes, "source": "sim"}]
                        sim_infos = base_infos_core + [info]
                        sim_overall, comps = predict_overall(sim_team, sim_infos, chart, attack_types)
                        uplift = sim_overall - base_overall_core
                        if uplift > 0:
                            upgrades.append(
                                (
                                    uplift,
                                    f"\u001b[36mOverall {pname}: {sim_overall:.0f}/100 (uplift {uplift:+.0f}; def {comps.get('defense','?')}, off {comps.get('offense','?')}, shared {comps.get('shared','?')}, delta {comps.get('delta','?')})\u001b[0m",
                                    info,
                                )
                            )
                        if best_any is None or sim_overall > best_any[0]:
                            best_any = (sim_overall, uplift, info, pname, comps)
                        log_verbose(
                            f"[upgrade] dual candidate {pname} overall {sim_overall:.0f} uplift {uplift:+.0f} "
                            f"vs base {base_overall_core:.0f} (def {comps.get('defense','?')} off {comps.get('offense','?')} "
                            f"shared {comps.get('shared','?')} delta {comps.get('delta','?')})"
                        )
                        break
            upgrades.sort(key=lambda x: x[0], reverse=True)
            picks = upgrades[:3]
            if picks:
                for _, line, _info in picks:
                    print(line)
                if demo_mode:
                    top = picks[0]
                    replacement = top[2]
                    print(f"\nDemo mode: applying swap -> add {replacement.get('name','new')} (drop {weakest_name})")
                    team_infos.pop(weakest_idx)
                    team_infos.append(replacement)
            elif demo_mode and best_any is not None:
                # fallback: apply best overall even if uplift <= 0 to honor auto-swap requirement
                replacement = best_any[2]
                print(f"\nDemo mode: applying fallback swap -> add {replacement.get('name','new')} (drop {weakest_name}); uplift {best_any[1]:+.0f}")
                team_infos.pop(weakest_idx)
                team_infos.append(replacement)
            else:
                print("\u001b[32mNo upgrade found beyond current lineup.\u001b[0m")

        # Launch wheel GUI preloaded with team
        wheel_path = Path(__file__).with_name("tk_team_builder.py")
        if wheel_path.exists():
            launch_wheel(team_infos, str(wheel_path))
        else:
            print("Wheel GUI not found; skipping GUI launch.")
    finally:
        print(LOG_FOOTER)
        _save_draft_cache()
        log_file.flush()
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        log_file.close()
        print(f"Log written to {log_path}")


def _apply_tracing():
    """Applies the trace_call decorator to functions in the global scope if TRACE_FUNCTIONS is enabled."""
    if not TRACE_FUNCTIONS:
        return

    # Iterate over a copy of the globals dictionary to avoid issues with modification during iteration
    for name, obj in list(globals().items()):
        if inspect.isfunction(obj):
            # Avoid tracing internal functions, and also avoid tracing the _apply_tracing itself
            if (
                not name.startswith("_")
                and name != "_apply_tracing"
                and name != "trace_call"
                and name not in {"log_verbose", "progress"}
            ):
                try:
                    globals()[name] = trace_call(obj)
                except Exception as exc:
                    log_verbose(f"[TRACE] Could not apply tracing to {name}: {exc}")


_apply_tracing()


if __name__ == "__main__":
    main()
