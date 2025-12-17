#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combined CLI: build team typings first, then suggest moves, then launch Tk wheel with final team.
"""
import json
import os
import subprocess
import sys
import builtins
import threading
from datetime import datetime
from pathlib import Path
import json

from move_suggestor import pick_moves, format_output
from move_suggestor import get_move_cache_stats

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
LOG_DIR = Path(__file__).with_name("logs")
TYPE_CACHE_PATH = Path(__file__).with_name("type_chart_cache.json")
DRAFT_CACHE_PATH = Path(__file__).with_name("draft_cache.json")
TYPE_POKEMON_CACHE_PATH = Path(__file__).with_name("type_pokemon_cache.json")
FINAL_FORMS_CACHE_PATH = Path(__file__).with_name("final_forms_cache.json")
LOG_FOOTER = "Permissions: full access to OneDrive/Desktop/teambuilder_v2 granted by user on 2025-12-12. Signed: Atlas"
VERBOSE = False  # enable for detailed loop progress during test runs
TRACE_FUNCTIONS = False  # tracing disabled to avoid noisy logs
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
    """Wrapper to print entry/exit when tracing is enabled."""
    if not TRACE_FUNCTIONS:
        return fn

    def wrapper(*args, **kwargs):
        print(f"[TRACE] {fn.__name__} start")
        result = fn(*args, **kwargs)
        print(f"[TRACE] {fn.__name__} done")
        return result
    return wrapper


def log_verbose(msg: str):
    if VERBOSE:
        print(f"[VERBOSE] {msg}")


def progress(msg: str):
    """Always-on progress indicator for long steps."""
    print(f"[progress] {msg}")


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

def fetch_single_type_candidates(t, current_team=None, version_group: str = VERSION_GROUP, chart=None, attack_types=None):
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

    base_infos = team_infos_from_cache(current_team or [])
    try:
        base_overall, _ = predict_overall(current_team or [], base_infos, chart, attack_types)
    except Exception:
        base_overall = 0

    scored = []
    for n in candidates:
        try:
            if not pokemon_in_version(n, version_group=version_group):
                continue
            typing = fetch_pokemon_typing(n)
            if len(typing) != 1 or typing[0] != t:
                continue
            try:
                cached = cache_draft_board(n)
                info = cached["info"]
                align = cached.get("alignment_score") or 0
                mt_count = len(cached.get("move_types") or [])
            except Exception:
                info = {"name": n, "types": typing, "suggested_moves": []}
                align = 0
                mt_count = 0
            sim_team = (current_team or []) + [{"name": n, "types": typing, "source": "sim"}]
            sim_infos = base_infos + [info]
            sim_overall, _ = predict_overall(sim_team, sim_infos, chart, attack_types)
            overlap = stack_overlap_penalty(compute_coverage(sim_team, chart, attack_types))
            # Favor stronger offensive profiles and alignment, while penalizing overlap.
            score = sim_overall - 5 * overlap + 0.25 * align + min(6, mt_count * 0.6)
            uplift = sim_overall - base_overall
            scored.append((score, uplift, n))
        except Exception:
            continue
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [n for _, _, n in scored[:6]]

def fetch_species_info(name: str):
    res = requests.get(f"{POKEAPI_BASE}/pokemon-species/{name.lower()}", timeout=15)
    res.raise_for_status()
    return res.json()

def fetch_dual_candidates(type_a, type_b, current_team=None, version_group: str = VERSION_GROUP, chart=None, attack_types=None):
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

    base_infos = team_infos_from_cache(current_team or [])
    try:
        base_overall, _ = predict_overall(current_team or [], base_infos, chart, attack_types)
    except Exception:
        base_overall = 0
    scored = []
    for n in inter:
        try:
            if not pokemon_in_version(n, version_group=version_group):
                continue
            typing = fetch_pokemon_typing(n)
            if set(typing) != {type_a, type_b}:
                continue
            try:
                cached = cache_draft_board(n)
                info = cached["info"]
                align = cached.get("alignment_score") or 0
                mt_count = len(cached.get("move_types") or [])
            except Exception:
                info = {"name": n, "types": typing, "suggested_moves": []}
                align = 0
                mt_count = 0
            sim_team = (current_team or []) + [{"name": n, "types": typing, "source": "sim"}]
            sim_infos = base_infos + [info]
            sim_overall, _ = predict_overall(sim_team, sim_infos, chart, attack_types)
            overlap = stack_overlap_penalty(compute_coverage(sim_team, chart, attack_types))
            score = sim_overall - 5 * overlap + 0.25 * align + min(6, mt_count * 0.6)
            uplift = sim_overall - base_overall
            scored.append((score, uplift, n))
        except Exception:
            continue
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [n for _, _, n in scored[:6]]
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
    # Balanced scoring: weaknesses and exposed types penalize; resist/immune reward
    def_score = (
        100
        - 2.5 * total_weak
        + 1.0 * total_resist
        + 1.5 * total_immune
        - 9 * net_exposed
        - 16 * stack_overlap  # heavier penalty for stacking existing weaknesses
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
    best = None  # (delta, label, pname, types)
    for t in TYPE_POOL:
        delta, _, _ = typing_delta(team, [t], chart, attack_types, base_cov=base_cov, base_score=base_score)
        if delta <= 0:
            continue
        opts = fetch_single_type_candidates(t, current_team=team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types)
        pname = opts[0] if opts else t
        candidate = (delta, f"DEF {t} delta {delta:+.0f}", pname, [t])
        if best is None or candidate[0] > best[0]:
            best = candidate
    if best is None:
        return None
    delta, label, pname, types = best
    # Normalize to (shared_gain, def_gain, overall_gain) for downstream printing
    return (0.0, delta, delta), label, pname, types


def pick_defensive_addition_fast(team, chart, attack_types):
    """Fast path: only consider single-type candidates without move fetch for harness."""
    base_cov = compute_coverage(team, chart, attack_types)
    base_score = typing_score(base_cov)
    best = None
    for t in attack_types:
        delta, _, _ = typing_delta(team, [t], chart, attack_types, base_cov=base_cov, base_score=base_score)
        if delta <= 0:
            continue
        opts = fetch_single_type_candidates(t, current_team=team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types)
        pname = opts[0] if opts else t
        if best is None or delta > best[0]:
            best = (delta, f"DEF {t} delta {delta:+.0f}", pname, [t])
    if not best:
        return None
    delta, label, pname, types = best
    return (0.0, delta, delta), label, pname, types


def pick_offense_addition(team, chart, attack_types):
    """Use overall addition as offensive fallback (keeps shape consistent)."""
    return pick_overall_addition(team, chart, attack_types)


def suggestion_buckets(team, cov, chart, attack_types):
    """Generate defensive/offensive/overall suggestion lines; return (lines, best_delta_available)."""
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
    best_delta_available = positives[0][0] if positives else 0

    # Cache best-delta calculations per simulated team (hashable by typing signature)
    best_delta_cache = {}

    def team_signature(sim_team):
        sig_parts = []
        for member in sim_team:
            types = member.get("types") or []
            sig_parts.append(tuple(types))
        return tuple(sorted(sig_parts))

    def best_delta_for_team(sim_team):
        sig = team_signature(sim_team)
        if sig in best_delta_cache:
            return best_delta_cache[sig]
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
        best_delta_cache[sig] = best_local
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
                mts.update(cached.get("move_types") or [])
        return mts

    base_move_types = current_move_types()
    base_offense = offense_score_with_bonuses(base_infos, cov, chart, attack_types)
    base_cov_map = {c["attack"]: c for c in cov}
    top_exposures = [c["attack"] for c in sorted(cov, key=lambda c: c["weak"], reverse=True) if c["weak"] > 0][:3]

    # Build offense candidates independently of defensive deltas
    offense_candidates = []
    for t in TYPE_POOL:
        opts = fetch_single_type_candidates(t, current_team=team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types)
        if opts:
            offense_candidates.append((opts[0], [t], f"Single-type {t}"))
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
            if opts:
                offense_candidates.append((opts[0], list(pair), f"Dual-type {pair[0]} + {pair[1]}"))

    off_top = []
    seen_off_picks = set()
    for pname, types, label in offense_candidates:
        if pname in seen_off_picks:
            continue
        try:
            cached = cache_draft_board(pname)
            candidate_move_types = set(cached.get("move_types") or [])
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
                se_hits = cached.get("se_hits") if 'cached' in locals() else []
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
                    if len(limited_types) >= 4:
                        break
                info["suggested_moves"] = [{"name": f"{t}-coverage", "type": t} for t in limited_types]
            move_types = set(base_move_types) | set(m["type"] for m in info.get("suggested_moves", []))
            sim_infos = base_infos + [info]
            sim_cov = compute_coverage(team + [{"name": pname, "types": types, "source": "sim"}], chart, attack_types)
            sim_offense = offense_score_with_bonuses(sim_infos, sim_cov, chart, attack_types)
            gain = sim_offense - base_offense
            neutral, se_types = offense_projection(move_types, chart, attack_types)
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
            ranked_gain = gain * gain_factor
            off_top.append(
                (
                    ranked_gain,
                    f"Offense {pname}: offense {sim_offense}/100 (gain {gain:+.0f}); hits {neutral} types >= neutral; SE: {', '.join(se_types[:5]) if se_types else 'none'}",
                )
            )
            seen_off_picks.add(pname)
        except Exception:
            continue
    off_top.sort(key=lambda x: x[0], reverse=True)
    # Prefer positive gains; if none, show top 3 (could be 0)
    positives_off = [o for o in off_top if o[0] > 0]
    if positives_off:
        off_top = select_with_ties(positives_off, 3, key=lambda x: x[0])
    else:
        off_top = select_with_ties(off_top, 3, key=lambda x: x[0])
    if off_top:
        lines.append("Top offense lifts:")
        for _, line in off_top:
            lines.append(f"\033[33m{line}\033[0m")
    else:
        lines.append("Top offense lifts: none (no offensive gains).")

    # Overall bucket (cyan) - type-first (titles), then mon examples
    base_infos = team_infos_from_cache(team)
    base_overall, _ = predict_overall(team, base_infos, chart, attack_types)
    ovl_top = []
    seen_ovl_picks = set()
    for delta, line, types in positives:
        if delta <= 0:
            continue
        # type label from defensive line
        type_label = line.split(":")[0] if ":" in line else line
        # pick mon examples for this type combo
        if ":" in line:
            cand_text = line.split(":", 1)[1].strip()
            opts = [c.strip() for c in cand_text.split(",") if c.strip()]
        else:
            opts = []
        examples = []
        for pname in opts:
            if pname in seen_ovl_picks:
                continue
            try:
                ptypes = fetch_pokemon_typing(pname)
            except Exception:
                ptypes = types
            try:
                cached = cache_draft_board(pname)
                info = cached["info"]
            except Exception:
                info = {"name": pname, "types": ptypes, "suggested_moves": []}
            sim_team = team + [{"name": pname, "types": ptypes, "source": "sim"}]
            sim_infos = base_infos + [info]
            sim_overall, comps = predict_overall(sim_team, sim_infos, chart, attack_types)
            gain = sim_overall - base_overall
            examples.append(
                (
                    gain,
                    pname,
                    f"\033[36mOverall {pname}: {sim_overall:.0f}/100 (uplift {gain:+.0f}; def {comps.get('defense','?')}, off {comps.get('offense','?')}, shared {comps.get('shared','?')}, delta {comps.get('delta','?')})\033[0m",
                )
            )
        examples.sort(key=lambda x: x[0], reverse=True)
        if examples:
            best_example = examples[0]
            seen_ovl_picks.add(best_example[1])
            ovl_top.append((best_example[0], type_label, best_example[2]))
    ovl_top.sort(key=lambda x: x[0], reverse=True)
    ovl_top = select_with_ties(ovl_top, 3, key=lambda x: x[0])
    if ovl_top:
        lines.append("Top overall lifts:")
        for _, type_label, line in ovl_top:
            lines.append(f"{type_label} -> {line}")

    return lines, best_delta_available


def coverage_report(team, chart, attack_types):
    # Pre-cache draft boards for current team to avoid re-fetching later and surface offense hints early
    for member in team:
        try:
            cache_draft_board(member.get("name", ""), level_cap=member.get("level_cap"))
        except Exception:
            continue
    cov = compute_coverage(team, chart, attack_types)
    weak_gaps = [c for c in cov if c["weak"] > (c["resist"] + c["immune"])]
    weak_gaps.sort(key=lambda c: (c["weak"] - (c["resist"] + c["immune"])), reverse=True)
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

    # Rating engine: already computed suggestion buckets; use returned best_delta_available for rating
    suggestion_lines, best_delta_available = suggestion_buckets(team, cov, chart, attack_types)
    report_lines.extend(suggestion_lines)

    # Typing rating (defense only here)
    total_weak = sum(c["weak"] for c in cov)
    total_resist = sum(c["resist"] for c in cov)
    total_immune = sum(c["immune"] for c in cov)
    net_exposed = sum(1 for c in cov if c["weak"] > (c["resist"] + c["immune"]))
    stack_overlap = sum(max(0, c["weak"] - 1) for c in cov)
    def_score = typing_score(cov)

    # Rating: 100 when no positive delta; otherwise 100 minus the highest positive delta.
    rating_score = max(0, min(100, 100 - best_delta_available))

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
    weak_lines = [f"{c['attack']} weak {c['weak']}/{c['size']}" for c in sorted_weak[:3] if c["weak"] > 0]
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
        f"Typing rating: {rating_score}/100 (delta left on table {best_delta_available:+.0f}; weak {total_weak}, resist {total_resist}, immune {total_immune}, net exposed types {net_exposed})"
    )
    try:
        infos = team_infos_from_cache(team)
        overall_score_val, comps = predict_overall(team, infos, chart, attack_types)
        report_lines.append(
            f"Overall preview: {overall_score_val}/100 (def {comps.get('defense','?')}, off {comps.get('offense','?')}, shared {comps.get('shared','?')}, delta {comps.get('delta','?')})"
        )
    except Exception:
        pass
    if stack_overlap > 0 and def_score < 80 and all("Balanced" in ln for ln in suggestion_lines if "Balanced" in ln):
        report_lines.append("Note: stacked weaknesses present; overall defensive score reduced by stacking penalty.")

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
    tmp_path.write_text(json.dumps(team_data, indent=2))
    # launch Tk app with env var for payload
    env = os.environ.copy()
    env["TEAM_PAYLOAD_PATH"] = str(tmp_path)
    subprocess.Popen([sys.executable, wheel_path], env=env)
    print(f"Launched wheel GUI with team; payload at {tmp_path}")


def compute_best_delta(team, chart, attack_types):
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


def team_infos_from_cache(team):
    """Build minimal team_infos using cached draft boards when available."""
    infos = []
    for member in team:
        name = member.get("name", "")
        level_cap = member.get("level_cap")
        cache_key = board_cache_key(name, level_cap)
        cached = BOARD_CACHE.get(cache_key) or BOARD_CACHE.get((cache_key[0], cache_key[1]))
        if cached:
            infos.append(cached["info"])
        else:
            infos.append({"name": name, "types": member.get("types") or [], "suggested_moves": []})
    return infos


def shared_weak_score(cov):
    """Score that heavily penalizes overlapping weaknesses."""
    if not cov:
        return 100
    max_weak = max(c["weak"] for c in cov)
    overlap = max(0, max_weak - 1)
    score = 100 - (overlap * 25)
    return max(0, min(100, int(score)))


def offense_score_with_bonuses(team_infos, cov, chart, attack_types):
    """Offense score with bonuses for covering team-weak types and unlocking new SE hits."""
    move_types = set()
    for info in team_infos:
        for m in info.get("suggested_moves", []):
            if m.get("type"):
                move_types.add(m["type"])
    if not move_types:
        return 0
    # Determine exposure severity per type to weight SE hits that patch weaknesses
    exposures = []
    for c in cov:
        exposure = max(0, c["weak"] - (c["resist"] + c["immune"]))
        exposures.append((c["attack"], exposure))
    exposures.sort(key=lambda x: x[1], reverse=True)
    max_exposure = exposures[0][1] if exposures else 0
    exposure_weight = {t: (exp / max_exposure) if max_exposure > 0 else 0 for t, exp in exposures}
    weak_types = {t for t, exp in exposures if exp > 0}

    total = 0.0
    se_types = set()
    for def_type in attack_types:
        best = 1.0
        for atk_type in move_types:
            mult = chart[atk_type].get(def_type, 1.0)
            if mult > best:
                best = mult
        if best >= 2.0:
            base = 1.0
            se_types.add(def_type)
        elif best > 1.0:
            base = 0.65
        elif best == 1.0:
            base = 0.25
        else:
            base = 0.0
        multiplier = 1.0
        if def_type in weak_types and best >= 1.0:
            # Double-weight coverage that addresses our exposed weaknesses.
            weight = 1 + 1.0 * exposure_weight.get(def_type, 0)
            multiplier *= weight
        if best >= 2.0:
            multiplier *= 1.08  # tempered bonus for super-effective unlock
            if def_type not in weak_types:
                multiplier *= 0.85  # stronger penalty if it's not addressing a weakness
        total += base * multiplier
    off_score = (total / len(attack_types)) * 100
    # Bonus for adding new SE coverage breadth
    breadth_bonus = min(6.0, len(se_types) * 0.9)
    off_score += breadth_bonus
    return int(max(0, min(100, off_score)))


def predict_overall(team, team_infos, chart, attack_types):
    """Compute overall score for a simulated team."""
    cov = compute_coverage(
        [{"name": m.get("name", ""), "types": m.get("types") or [], "source": m.get("source", "")} for m in team],
        chart,
        attack_types,
    )
    def_score = typing_score(cov)
    shared_score = shared_weak_score(cov)
    best_delta = compute_best_delta(
        [{"name": m.get("name", ""), "types": m.get("types") or [], "source": m.get("source", "")} for m in team],
        chart,
        attack_types,
    )
    delta_score = max(0, min(100, 100 - best_delta))
    off_score = offense_score_with_bonuses(team_infos, cov, chart, attack_types)
    overall = overall_score(def_score, off_score, delta_score, shared_score)
    components = {
        "defense": def_score,
        "offense": off_score,
        "shared": shared_score,
        "delta": delta_score,
        "best_delta": best_delta,
        "cov": cov,
    }
    return overall, components


def overall_score(def_score, off_score, delta_score, shared_score):
    """Unified overall score with strong weight on avoiding shared weaknesses."""
    overall = (
        0.35 * def_score
        + 0.30 * off_score
        + 0.15 * delta_score
        + 0.20 * shared_score
    )
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
    best = None  # (compare_tuple, uplift, line, pname, ptypes, sim_score)

    def sim_overall(pname, ptypes):
        try:
            cached = cache_draft_board(pname)
            info = cached["info"]
            candidate_move_types = set(cached.get("move_types") or [])
        except Exception:
            info = {"name": pname, "types": ptypes, "suggested_moves": []}
            candidate_move_types = set()
        sim_team = team + [{"name": pname, "types": ptypes, "source": "sim"}]
        sim_infos = base_infos + [info]
        sim_overall, comps = predict_overall(sim_team, sim_infos, chart, attack_types)
        uplift = sim_overall - base_overall
        line = (
            f"\u001b[36mOverall {pname}: {sim_overall:.0f}/100 (uplift {uplift:+.0f}; "
            f"def {comps.get('defense','?')}, off {comps.get('offense','?')}, shared {comps.get('shared','?')}, "
            f"delta {comps.get('delta','?')})\u001b[0m"
        )
        return uplift, sim_overall, line, comps, candidate_move_types

    def consider(pname, ptypes):
        uplift, sim_score, line, comps, candidate_move_types = sim_overall(pname, ptypes)
        dual_penalty = 2.0 if len(ptypes) == 2 else 0.0
        sim_team = team + [{"name": pname, "types": ptypes, "source": "sim"}]
        sim_cov = comps.get("cov") or compute_coverage(sim_team, chart, attack_types)
        overlap = stack_overlap_penalty(sim_cov)

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
            compare_val = uplift - dual_penalty - overlap_penalty + (0.5 * patched) + (0.3 * coverage_bonus)
            compare_tuple = (-overlap, patched, coverage_bonus, compare_val, sim_score)
        else:
            overlap_blocked = overlap > 0 and sim_score <= 95
            compare_val = uplift - dual_penalty
            if overlap_blocked:
                compare_val -= 500  # effectively sort blocked overlaps after any clean option
            compare_tuple = (compare_val, -overlap, sim_score)

        nonlocal best
        if best is None or compare_tuple > best[0]:
            best = (compare_tuple, uplift, line, pname, ptypes, sim_score)

    for t in TYPE_POOL:
        opts = fetch_single_type_candidates(t, current_team=team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types)
        if not opts:
            continue
        pname = opts[0]
        try:
            ptypes = fetch_pokemon_typing(pname)
        except Exception:
            ptypes = [t]
        consider(pname, ptypes)

    seen_pairs = set()
    for i in range(len(TYPE_POOL)):
        for j in range(i + 1, len(TYPE_POOL)):
            pair = tuple(sorted((TYPE_POOL[i], TYPE_POOL[j])))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            opts = fetch_dual_candidates(pair[0], pair[1], current_team=team, version_group=VERSION_GROUP, chart=chart, attack_types=attack_types)
            if not opts:
                continue
            pname = opts[0]
            try:
                ptypes = fetch_pokemon_typing(pname)
            except Exception:
                ptypes = list(pair)
            consider(pname, ptypes)
    if best is None:
        return None
    _compare_val, uplift, line, pname, ptypes, sim_score = best
    # Score tuple normalized to (shared_gain, def_gain, overall_gain) for downstream printing
    return (0.0, 0.0, uplift), line, pname, ptypes


def autofill_team(team, chart, attack_types, max_size=6):
    """Greedily add best-available defensive/shared improvements until team reaches max_size or no positives remain."""
    added = []
    iteration = 0
    while len(team) < max_size:
        iteration += 1
        progress(f"Autofill iteration {iteration} (team size {len(team)})")
        # Slot 6: always take best overall uplift
        if len(team) == max_size - 1:
            best = pick_overall_addition(team, chart, attack_types)
        else:
            best = pick_defensive_addition(team, chart, attack_types)
            if not best:
                best = pick_offense_addition(team, chart, attack_types)
            if not best:
                best = pick_overall_addition(team, chart, attack_types)
        if not best:
            log_verbose("[autofill] no positive addition found")
            break
        score_tuple, label, pname, types = best
        # Block additions that would create overlap unless overall would exceed 95
        try:
            if not addition_allows_overlap(team, pname, types, chart, attack_types):
                log_verbose(f"[autofill] rejected {pname} due to overlap rule; attempting fallback with overlap allowed")
                fallback = pick_overall_addition(team, chart, attack_types, allow_overlap=True)
                if fallback:
                    score_tuple, label, pname, types = fallback
                    log_verbose(f"[autofill] fallback selected {pname} (overlap allowed)")
                else:
                    break
        except Exception:
            log_verbose(f"[autofill] overlap check failed for {pname}; skipping")
            break
        try:
            ptypes = fetch_pokemon_typing(pname)
        except Exception:
            ptypes = types
        team.append({"name": pname, "types": ptypes, "level_cap": None})
        added.append((pname, label, score_tuple))
        log_verbose(f"[autofill] added {pname} via {label} (scores {score_tuple})")
    return added


def final_team_rating(team_infos, cov, chart, attack_types):
    # Defensive score
    total_weak = sum(c["weak"] for c in cov)
    total_resist = sum(c["resist"] for c in cov)
    total_immune = sum(c["immune"] for c in cov)
    net_exposed = sum(1 for c in cov if c["weak"] > (c["resist"] + c["immune"]))
    def_score = typing_score(cov)

    shared_score = shared_weak_score(cov)

    # Offensive score: bonus-weighted coverage
    off_score = offense_score_with_bonuses(team_infos, cov, chart, attack_types)
    move_types = set()
    for info in team_infos:
        for m in info.get("suggested_moves", []):
            if m.get("type"):
                move_types.add(m["type"])

    # Perfect team definition string
    perfect_def = "Perfect team: no net weaknesses (resist/immune >= weak for every attack type) AND offensive coverage can hit every type at least neutral, ideally super-effective."

    # Delta score: how much improvement remains (headroom)
    best_delta = compute_best_delta(
        [{"name": i["name"], "types": i["types"], "source": "final"} for i in team_infos],
        chart,
        attack_types,
    )
    delta_score = max(0, min(100, 100 - best_delta))

    overall = overall_score(def_score, off_score, delta_score, shared_score)
    scores = {
        "defense": def_score,
        "offense": off_score,
        "delta": delta_score,
        "shared": shared_score,
        "overall": overall,
        "perfect_text": perfect_def,
        "weak": total_weak,
        "resist": total_resist,
        "immune": total_immune,
        "net_exposed": net_exposed,
        "move_types": move_types,
        "best_delta": best_delta,
    }
    summary = [
        perfect_def,
        f"Defensive score: {def_score}/100 (weak {total_weak}, resist {total_resist}, immune {total_immune}, net exposed types {net_exposed})",
        f"Offensive score: {off_score}/100 (coverage from suggested move types: {', '.join(sorted(move_types)) if move_types else 'none'})",
        f"Shared-weakness score: {shared_score}/100 (penalizes overlapping weaknesses)",
        f"Delta score (headroom): {delta_score}/100 (best remaining delta {best_delta:+.0f})",
        f"Overall team rating: {overall}/100",
    ]
    return "\n".join(summary), scores


def cache_draft_board(name: str, level_cap=None):
    """Fetch and cache draft board + offense hints for a Pokemon (version group no longer used)."""
    key = board_cache_key(name, level_cap=level_cap)
    cached = BOARD_CACHE.get(key)
    if not cached:
        legacy = (key[0], key[1])
        cached = BOARD_CACHE.get(legacy)
    if cached:
        BOARD_CACHE_STATS["hit"] += 1
        return cached
    BOARD_CACHE_STATS["miss"] += 1
    progress(f"Fetching moves for {name}...")
    info = pick_moves(
        name,
        level_cap=level_cap,
        exclude_moves=set(),
        used_moves=set(),
        version_group=VERSION_GROUP,
    )
    move_types = {m["type"] for m in info.get("draft_board", []) if m.get("type")}
    se_hits = [t for t, cnt in info.get("coverage_priority", []) if cnt > 0]
    cached = {
        "info": info,
        "move_types": move_types,
        "se_hits": se_hits,
        "role": info.get("role"),
        "alignment_score": info.get("alignment_score"),
    }
    BOARD_CACHE[key] = cached
    _save_draft_cache()
    return cached


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
        if HARNESS_SMOKE:
            # Minimal harness: feed gengar finalize in one go to pop GUI quickly
            harness_inputs = iter(["gengar finalize"])

            def harness_input(_prompt=""):
                try:
                    return next(harness_inputs)
                except StopIteration:
                    return ""

            builtins.input = harness_input
        if demo_mode:
            print("Running demo mode with: gengar, sableye, honedge, mewtwo (auto-fill to 6, auto-apply best swap).")
            demo_names = ["gengar", "sableye", "honedge", "mewtwo"]
            for name in demo_names:
                try:
                    types = fetch_pokemon_typing(name)
                except Exception as exc:
                    print(f"Error fetching {name}: {exc}")
                    types = []
                team.append({"name": name.lower(), "types": types, "level_cap": None})
                try:
                    cached = cache_draft_board(name)
                    mt_preview = ", ".join(sorted(cached["move_types"])) if cached["move_types"] else "none"
                    se_preview = ", ".join(cached["se_hits"][:5]) if cached["se_hits"] else "none"
                    role_label = cached.get("role") or "n/a"
                    print(f"Cached draft board for {name} (role {role_label}; move types: {mt_preview}; SE hits: {se_preview})")
                except Exception as exc:
                    if VERBOSE:
                        print(f"Draft cache failed for {name}: {exc}")
            added = autofill_team(team, chart, attack_types, max_size=6)
            if added:
                for name, label, score_tuple in added:
                    shared_gain, def_gain, overall_gain = score_tuple
                    print(
                        f"\033[32mAdded {name} via {label} "
                        f"(shared {shared_gain:+.0f}, def {def_gain:+.0f}, overall {overall_gain:+.0f})\033[0m"
                    )
            report, cov = coverage_report(team, chart, attack_types)
            print("\n=== Typing checkpoint ===")
            print(report)

        print("Team builder + move suggester. Commands: 'next' to move to moves, 'done' to finish, 'drop <name>' to remove, 'finalize' to auto-fill and continue.")

        def do_finalize():
            nonlocal team
            if HARNESS_SMOKE:
                print("Harness mode: running autofill to 6 and launching GUI.")
                added = []
                if len(team) < 6:
                    added = autofill_team(team, chart, attack_types, max_size=6)
                    if added:
                        for name, label, score_tuple in added:
                            shared_gain, def_gain, overall_gain = score_tuple
                            print(
                                f"\033[32mAdded {name} via {label} "
                                f"(shared {shared_gain:+.0f}, def {def_gain:+.0f}, overall {overall_gain:+.0f})\033[0m"
                            )
                    else:
                        print("Harness autofill added nothing (team may remain undersized).")
                infos = team_infos_from_cache(team)
                wheel_path = Path(__file__).with_name("tk_team_builder.py")
                if wheel_path.exists():
                    launch_wheel(infos, str(wheel_path))
                else:
                    print("Wheel GUI not found; skipping GUI launch.")
                return True
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
                mt_preview = ", ".join(sorted(cached["move_types"])) if cached["move_types"] else "none"
                se_preview = ", ".join(cached["se_hits"][:5]) if cached["se_hits"] else "none"
                role_label = cached.get("role") or "n/a"
                print(f"Cached draft board for {name} (role {role_label}; move types: {mt_preview}; SE hits: {se_preview})")
                print(f"[progress] {name}: computing move suggestions (this can take a moment)...")
            except Exception as exc:
                if VERBOSE:
                    print(f"Draft cache failed for {name}: {exc}")
            if HARNESS_SMOKE:
                print("Harness mode: skipping coverage report to keep fast path.")
            else:
                report, cov = coverage_report(team, chart, attack_types)
                print(report)
                if len(team) >= 6:
                    print("Team is full (6/6). Type 'next' to lock typings or 'drop <name>' to swap someone.")
            if finalize_after_add:
                if do_finalize():
                    break

        # Auto-fill before moves if team is undersized
        if team and len(team) < 6 and not HARNESS_SMOKE:
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

        if HARNESS_SMOKE:
            print("Harness mode: launching GUI and exiting before move suggestions.")
            infos = team_infos_from_cache(team)
            wheel_path = Path(__file__).with_name("tk_team_builder.py")
            if wheel_path.exists():
                launch_wheel(infos, str(wheel_path))
            else:
                print("Wheel GUI not found; skipping GUI launch.")
            return

        # Move suggestion phase
        if team:
            print("\n=== Before moves: defensive improvement check ===")
            print(best_defensive_improvement(team, chart, attack_types))
        print("\n=== Typing locked in. Proceeding to move suggestions ===")
        # Collect boards for draft
        boards = []
        for member in team:
            name = member["name"]
            level_cap = member.get("level_cap")
            print(f"\nBuilding draft board for {name}...")
            cache_key = board_cache_key(name, level_cap)
            cached = BOARD_CACHE.get(cache_key) or BOARD_CACHE.get((cache_key[0], cache_key[1]))
            if cached:
                info = cached["info"]
            else:
                info = pick_moves(
                    name,
                    level_cap=level_cap,
                    exclude_moves=global_exclude,
                    used_moves=global_used,
                    version_group=VERSION_GROUP,
                )
                cache_draft_board(name, level_cap=level_cap)
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
            print("\nTeam scores:")
            print(f" - Defense: {scores['defense']}/100")
            print(f" - Offense: {scores['offense']}/100")
            print(f" - Delta headroom: {scores['delta']}/100 (best remaining delta {scores['best_delta']:+.0f})")
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
            # Keep original detailed summary
            print("\n" + summary_text)
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
            best_any = None  # track best even if uplift <=0
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
        log_file.flush()
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        log_file.close()
        print(f"Log written to {log_path}")


def _apply_tracing():
    """Wrap module-level functions with trace_call for entry/exit visibility."""
    if not TRACE_FUNCTIONS:
        return
    skip = {"trace_call", "_apply_tracing", "log_verbose"}
    for name, fn in list(globals().items()):
        if callable(fn) and getattr(fn, "__module__", None) == __name__ and not name.startswith("_") and name not in skip:
            globals()[name] = trace_call(fn)


_apply_tracing()


if __name__ == "__main__":
    main()
