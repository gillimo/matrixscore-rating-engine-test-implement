import json
import math
from pathlib import Path
from collections import defaultdict

MOVE_RARITY_CACHE = {}


def _load_move_rarity_cache(path: Path):
    global MOVE_RARITY_CACHE
    if MOVE_RARITY_CACHE:
        return
    if path.exists():
        try:
            MOVE_RARITY_CACHE = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            MOVE_RARITY_CACHE = {}


def _save_move_rarity_cache(path: Path):
    try:
        path.write_text(json.dumps(MOVE_RARITY_CACHE), encoding="utf-8")
    except Exception:
        pass


def _build_move_rarity_cache(move_cache: dict, path: Path):
    global MOVE_RARITY_CACHE
    move_entries = []
    type_counts = defaultdict(list)
    for name, data in move_cache.items():
        learned_by = len(data.get("learned_by_pokemon", []) or [])
        mtype = (data.get("type") or {}).get("name")
        move_entries.append((name, learned_by, mtype))
        if mtype:
            type_counts[mtype].append(learned_by)
    if not move_entries:
        MOVE_RARITY_CACHE = {}
        return
    counts = [c for _, c, _ in move_entries]
    mean = sum(counts) / max(1, len(counts))
    variance = sum((c - mean) ** 2 for c in counts) / max(1, len(counts))
    std = math.sqrt(variance) if variance > 0 else 1.0
    rare_threshold = max(1, mean - std)

    type_stats = {}
    for tname, vals in type_counts.items():
        tmean = sum(vals) / max(1, len(vals))
        tvar = sum((c - tmean) ** 2 for c in vals) / max(1, len(vals))
        tstd = math.sqrt(tvar) if tvar > 0 else 1.0
        type_stats[tname] = {"mean": tmean, "std": tstd}

    def _cdf(z):
        return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

    def _rarity_score(count, mean_val, std_val):
        if std_val <= 0:
            return 0
        z = (count - mean_val) / std_val
        return int(round(100 * (1.0 - _cdf(z))))

    moves = {}
    for name, learned_by, mtype in move_entries:
        tstats = type_stats.get(mtype, {"mean": mean, "std": std})
        rarity_score = _rarity_score(learned_by, mean, std)
        type_rarity_score = _rarity_score(learned_by, tstats["mean"], tstats["std"])
        if learned_by <= 1:
            tier = "unique"
        elif learned_by <= 3:
            tier = "near-unique"
        elif learned_by <= rare_threshold:
            tier = "rare"
        else:
            tier = ""
        moves[name] = {
            "learned_by": learned_by,
            "rarity_score": rarity_score,
            "type_rarity_score": type_rarity_score,
            "rarity_tier": tier,
        }

    MOVE_RARITY_CACHE = {
        "global": {"mean": mean, "std": std, "rare_threshold": rare_threshold},
        "types": type_stats,
        "moves": moves,
    }
    _save_move_rarity_cache(path)


def get_rarity_for_move(name: str, mtype: str, learned_by: int, move_cache: dict, path: Path):
    _load_move_rarity_cache(path)
    if not MOVE_RARITY_CACHE:
        _build_move_rarity_cache(move_cache, path)
    if not MOVE_RARITY_CACHE:
        return {"rarity_score": 0, "type_rarity_score": 0, "rarity_tier": ""}
    moves = MOVE_RARITY_CACHE.get("moves", {})
    entry = moves.get(name)
    if entry:
        return entry
    _build_move_rarity_cache(move_cache, path)
    moves = MOVE_RARITY_CACHE.get("moves", {})
    entry = moves.get(name)
    if entry:
        return entry
    global_stats = MOVE_RARITY_CACHE.get("global", {"mean": 0, "std": 1})
    type_stats = MOVE_RARITY_CACHE.get("types", {}).get(mtype, global_stats)
    mean = global_stats.get("mean", 0)
    std = global_stats.get("std", 1)
    tmean = type_stats.get("mean", mean)
    tstd = type_stats.get("std", std)
    if std <= 0:
        rarity_score = 0
    else:
        rarity_score = int(round(100 * (1.0 - 0.5 * (1.0 + math.erf(((learned_by - mean) / std) / math.sqrt(2.0))))))
    if tstd <= 0:
        type_rarity_score = 0
    else:
        type_rarity_score = int(round(100 * (1.0 - 0.5 * (1.0 + math.erf(((learned_by - tmean) / tstd) / math.sqrt(2.0))))))
    return {"rarity_score": rarity_score, "type_rarity_score": type_rarity_score, "rarity_tier": ""}
