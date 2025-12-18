# -*- coding: utf-8 -*-
import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import base64
import io
import re
from pathlib import Path
from PIL import Image, ImageTk

import requests

POKEAPI_BASE = "https://pokeapi.co/api/v2"
EXCLUDED_TYPES = {"shadow", "unknown"}
TRACE_FUNCTIONS = False  # tracing hard-disabled to keep GUI quiet

# Official-ish palette: type colors and Pokédex brand primaries
TYPE_COLORS = {
    "normal": "#A8A77A",
    "fire": "#EE8130",
    "water": "#6390F0",
    "electric": "#F7D02C",
    "grass": "#7AC74C",
    "ice": "#96D9D6",
    "fighting": "#C22E28",
    "poison": "#A33EA1",
    "ground": "#E2BF65",
    "flying": "#A98FF3",
    "psychic": "#F95587",
    "bug": "#A6B91A",
    "rock": "#B6A136",
    "ghost": "#735797",
    "dragon": "#6F35FC",
    "dark": "#705746",
    "steel": "#B7B7CE",
    "fairy": "#D685AD",
}
POKEDEX_YELLOW = "#FFCB05"
POKEDEX_BLUE = "#3B4CCA"
POKEDEX_RED = "#EE1515"
POKEDEX_DARK = "#1D1E2C"
POKEDEX_LIGHT = "#FFF7D6"
POKEDEX_GRAY = "#E2E4E8"
ROLE_MOVE_MIX = {
    "sweeper": "Prefers 1 STAB, 2 coverage hitting team weaknesses, and 1 priority/recoil or setup flex slot.",
    "tank": "Prefers heal/screen/hazard control first, plus 1 STAB and 1 coverage; utility takes priority.",
    "balanced": "Prefers 1 status/control, 1 STAB, 1 coverage, and 1 flex utility/buff slot.",
}
DEFAULT_ROLE_MOVE_MIX = "Prefers a balanced mix of STAB, coverage, and utility tuned to the team."
# Local fallback: use bundled icons (add PNGs under icons/types/{type}.png)
TYPE_ICON_URL = None
TYPE_ICON_LOCAL = Path(__file__).with_name("icons").joinpath("types", "{type}.png")
SPRITE_BASE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{id}.png"
TYPE_ICON_CACHE = {}
TYPE_ICON_CACHE_DIM = {}
STATS_CACHE = {}
STYLE_CACHE = {}


def trace_call(fn):
    """Wrapper to print entry/exit when tracing is enabled."""
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        return result
    return wrapper


def fetch_json(url: str):
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()

def fetch_base_stat_total(name: str):
    key = (name or "").lower()
    if not key:
        return 0
    if key in STATS_CACHE:
        return STATS_CACHE[key]
    try:
        data = fetch_json(f"{POKEAPI_BASE}/pokemon/{key}")
        total = sum(s.get("base_stat", 0) for s in data.get("stats", []))
        STATS_CACHE[key] = total
        return total
    except Exception:
        STATS_CACHE[key] = 0
        return 0

def load_payload_team():
    payload_path = os.environ.get("TEAM_PAYLOAD_PATH")
    if not payload_path:
        return None, None
    try:
        with open(payload_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        team_data = payload.get("team", [])
        role_move_mix = payload.get("role_move_mix", {})
        # Expect list of {name, types, suggested_moves}
        team = []
        for entry in team_data:
            team.append(
                {
                    "name": entry.get("name", ""),
                    "types": entry.get("types", []),
                    "source": "payload",
                    "suggested_moves": entry.get("suggested_moves", []),
                    "suggested_by_category": entry.get("suggested_by_category", {}),
                    "role": entry.get("role", ""),
                }
            )
        return team, role_move_mix
    except Exception:
        return None, None

def fetch_types():
    listing = fetch_json(f"{POKEAPI_BASE}/type")
    results = [t for t in listing["results"] if t["name"] not in EXCLUDED_TYPES]
    details = []
    for t in results:
        data = fetch_json(t["url"])
        rel = data["damage_relations"]
        details.append(
            {
                "name": t["name"],
                "double_damage_to": [x["name"] for x in rel["double_damage_to"]],
                "half_damage_to": [x["name"] for x in rel["half_damage_to"]],
                "no_damage_to": [x["name"] for x in rel["no_damage_to"]],
            }
        )
    return details

def build_matrix(details):
    attack_types = [d["name"] for d in details]
    matrix = {a: {d: 1.0 for d in attack_types} for a in attack_types}
    for d in details:
        atk = d["name"]
        for target in d["double_damage_to"]:
            matrix[atk][target] = 2.0
        for target in d["half_damage_to"]:
            matrix[atk][target] = 0.5
        for target in d["no_damage_to"]:
            matrix[atk][target] = 0.0
    return matrix

def fetch_pokemon_typing(name: str):
    data = fetch_json(f"{POKEAPI_BASE}/pokemon/{name.lower()}")
    types = sorted(data["types"], key=lambda x: x["slot"])
    return [t["type"]["name"] for t in types]

def fetch_sprite_image(name: str):
    try:
        data = fetch_json(f"{POKEAPI_BASE}/pokemon/{name.lower()}")
        sprite_url = (
            data.get("sprites", {})
            .get("other", {})
            .get("official-artwork", {})
            .get("front_default")
            or data.get("sprites", {}).get("front_default")
        )
        if not sprite_url:
            return None
        img_bytes = requests.get(sprite_url, timeout=15).content
        im = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        im.thumbnail((72, 72), Image.LANCZOS)
        return ImageTk.PhotoImage(im)
    except Exception:
        return None

def fetch_type_icon(t: str):
    """Return lit icon; also populates dim cache."""
    if t in TYPE_ICON_CACHE:
        return TYPE_ICON_CACHE[t]
    try:
        path = str(TYPE_ICON_LOCAL).format(type=t)
        with open(path, "rb") as f:
            img_bytes = f.read()
        im = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        im.thumbnail((40, 40), Image.LANCZOS)
        icon = ImageTk.PhotoImage(im)
        TYPE_ICON_CACHE[t] = icon
        # dim version
        dim_im = im.copy()
        dim_im.putalpha(90)
        TYPE_ICON_CACHE_DIM[t] = ImageTk.PhotoImage(dim_im)
        return icon
    except Exception:
        TYPE_ICON_CACHE[t] = None
        TYPE_ICON_CACHE_DIM[t] = None
        return None

def _hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

def _rgb_to_hex(rgb):
    r, g, b = rgb
    return f"#{int(r):02X}{int(g):02X}{int(b):02X}"

def _contrast_color(hex_color: str):
    r, g, b = _hex_to_rgb(hex_color)
    # relative luminance
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#0b0d14" if lum > 0.6 else "#f8fafc"

def type_gradient(types):
    if not types:
        return ["#e2e8f0", "#e2e8f0"]
    if len(types) == 1:
        c = TYPE_COLORS.get(types[0], "#e2e8f0")
        return [c, c]
    c1 = TYPE_COLORS.get(types[0], "#e2e8f0")
    c2 = TYPE_COLORS.get(types[1], "#cbd5e1")
    # Simple blend for dual types to mimic dual tint
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    blend = _rgb_to_hex(((r1 + r2) / 2, (g1 + g2) / 2, (b1 + b2) / 2))
    return [blend, blend]

def _get_card_style(style: ttk.Style, types, key_prefix="Card"):
    """Return a ttk style name tinted by typing; cache per type combo."""
    tkey = ",".join(types) if types else "none"
    cache_key = f"{key_prefix}.{tkey}"
    if cache_key in STYLE_CACHE:
        return STYLE_CACHE[cache_key]
    colors = type_gradient(types)
    base = colors[0]
    text_color = _contrast_color(base)
    style_name = f"{key_prefix}.{tkey}.TFrame"
    style.configure(style_name, background=base)
    STYLE_CACHE[cache_key] = (style_name, text_color, base)
    return STYLE_CACHE[cache_key]

def defensive_multiplier(attack_type: str, defense_types, matrix):
    base = matrix.get(attack_type)
    if not base:
        return 1.0
    mult = 1.0
    for dt in defense_types:
        mult *= base.get(dt, 1.0)
    return mult

def compute_coverage(team, matrix):
    attacks = list(matrix.keys())
    cov = []
    for atk in attacks:
        weak = resist = immune = neutral = 0
        for member in team:
            if not member["types"]:
                continue
            m = defensive_multiplier(atk, member["types"], matrix)
            if m == 0:
                immune += 1
            elif m > 1:
                weak_inc = 1.0
                if atk in member["types"]:
                    weak_inc *= 0.25
                weak += weak_inc
            elif m < 1:
                resist += 1
            else:
                neutral += 1
        size = sum(1 for m in team if m["types"])
        cov.append(
            {
                "attack": atk,
                "weak": weak,
                "resist": resist,
                "immune": immune,
                "neutral": neutral,
                "size": size,
            }
        )
    return cov
def team_type_presence(team):
    """Return a set of defensive types present on the team."""
    present = set()
    for member in team:
        for t in member.get("types") or []:
            present.add(t)
    return present


def get_icon_for_type(t, lit=True):
    # Return cached icon, optionally dimmed
    icon = fetch_type_icon(t)
    if not icon:
        return None
    if lit:
        return icon
    return TYPE_ICON_CACHE_DIM.get(t) or icon
def typing_score(cov):
    total_weak = sum(c["weak"] for c in cov)
    total_resist = sum(c["resist"] for c in cov)
    total_immune = sum(c["immune"] for c in cov)
    net_exposed = sum(1 for c in cov if c["weak"] > (c["resist"] + c["immune"]))
    stack_overlap = sum(max(0, c["weak"] - 1) for c in cov)
    def_score = (
        100
        - 2.1 * total_weak
        + 1.4 * total_resist
        + 2.2 * total_immune
        - 12 * net_exposed
        - 14 * stack_overlap
    )
    return max(0, min(100, int(def_score)))

def offense_score_with_bonuses(team_infos, cov, chart, attack_types):
    move_types = set()
    for info in team_infos:
        for m in info.get("suggested_moves", []):
            if m.get("type"):
                move_types.add(m["type"])
    if not move_types:
        return 0
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
        if best > 1.0:
            base = 0.35
        elif best == 1.0:
            base = 0.06
        else:
            base = 0.0
        multiplier = 1.0
        if def_type in weak_types and best >= 1.0:
            weight = 1 + 1.6 * exposure_weight.get(def_type, 0)
            multiplier *= weight
        if best >= 2.0:
            se_types.add(def_type)
            se_mult = 1.15 if def_type in weak_types else 0.65
            multiplier *= se_mult
        elif best < 1 and def_type in weak_types:
            multiplier *= 0.6
        total += base * multiplier
    raw = (total / len(attack_types)) * 100
    breadth_bonus = min(5.0, len(se_types) * 0.8)
    diversity = len(move_types)
    diversity_bonus = min(4.0, max(0, diversity - 2) * 0.7)
    se_penalty = max(0, 18 - len(se_types)) * 0.7
    off_score = max(0, min(100, raw + breadth_bonus + diversity_bonus - se_penalty))
    if off_score > 80:
        off_score = 80 + (off_score - 80) * 0.55
    return int(off_score)

def typing_delta_display(team, add_types, matrix, attack_types, base_cov=None, base_score=None):
    if base_cov is None:
        base_cov = compute_coverage(team, matrix)
    if base_score is None:
        base_score = typing_score(base_cov)
    sim_cov = compute_coverage(team + [{"name": "sim", "types": add_types, "source": "sim"}], matrix)
    sim_score = typing_score(sim_cov)
    return sim_score - base_score, sim_score, base_score

def adjust_color(hex_color: str, factor: float):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    return f"#{r:02X}{g:02X}{b:02X}"

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PokeAPI Team Wheel (Tk)")
        self._set_initial_geometry()
        self.root.configure(bg=POKEDEX_LIGHT)

        self.status_var = tk.StringVar(value="Team view ready.")
        self.metrics = {}
        self.score_text_var = tk.StringVar(value="No metrics")
        payload_team, role_move_mix = load_payload_team()
        self.role_move_mix = role_move_mix or ROLE_MOVE_MIX
        self.upgrades_raw = []
        if payload_team:
            base_team = payload_team[:6]
            while len(base_team) < 6:
                base_team.append({"name": "", "types": [], "source": ""})
            self.team = base_team
            self.payload_moves = [t.get("suggested_moves", []) for t in payload_team[:6]]
            self.payload_by_cat = [t.get("suggested_by_category", {}) for t in payload_team[:6]]
            try:
                # Attempt to load metrics from payload if present
                import json
                payload_path = Path(os.environ.get("TEAM_PAYLOAD_PATH", Path(__file__).with_name("team_payload.json")))
                if payload_path.exists():
                    payload_json = json.loads(payload_path.read_text())
                    self.metrics = payload_json.get("metrics", {}) or {}
                    self.upgrades_raw = payload_json.get("metrics", {}).get("upgrades", []) or []
            except Exception:
                self.metrics = {}
        else:
            self.team = [{"name": "", "types": [], "source": ""} for _ in range(6)]
            self.payload_moves = [[] for _ in range(6)]
            self.payload_by_cat = [{} for _ in range(6)]
        self.parsed_upgrades = self._parse_upgrades(self.upgrades_raw)
        self.sprite_cache = {}
        self.cached_move_blocks = [None] * 6

        self._build_ui()
        self._render_payload_panel()
        self._refresh_metrics_and_ui(initial=True)

    def _set_initial_geometry(self):
        # Size window relative to screen, with sensible bounds
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        width = min(1600, max(1100, int(sw * 0.85)))
        height = min(1000, max(800, int(sh * 0.85)))
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(900, 720)
        try:
            self.root.iconify()
            self.root.deiconify()
        except Exception:
            pass

    def _build_ui(self):
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("TFrame", background=POKEDEX_LIGHT)
        self.style.configure("TLabel", background=POKEDEX_LIGHT, foreground=POKEDEX_DARK)
        self.style.configure("Glass.TLabelframe", background="#f7fbff", bordercolor="#cbd5e1")
        self.style.configure("Glass.TLabelframe.Label", background="#f7fbff")
        self.style.configure("CardHeader.TLabel", background="#f7fbff", foreground=POKEDEX_DARK, font=("Segoe UI", 11, "bold"))
        self.style.configure("Tag.TLabel", background="#0f172a", foreground="#f8fafc", font=("Segoe UI", 8, "bold"))
        # Button palette: primary = red, secondary = blue
        self.style.configure(
            "Primary.TButton",
            background=POKEDEX_RED,
            foreground="#f8fafc",
            bordercolor=POKEDEX_RED,
            focusthickness=3,
        )
        self.style.map("Primary.TButton", background=[("active", "#c01010")])
        self.style.configure(
            "Secondary.TButton",
            background=POKEDEX_BLUE,
            foreground="#f8fafc",
            bordercolor=POKEDEX_BLUE,
            focusthickness=3,
        )
        self.style.map("Secondary.TButton", background=[("active", "#2a3799")])

        wrapper = ttk.Frame(self.root)
        wrapper.pack(fill="both", expand=True, padx=16, pady=12)

        header = ttk.Frame(wrapper)
        header.pack(fill="x", pady=(0, 8))
        ttk.Label(header, text="Team Cards (PokeAPI)", font=("Segoe UI", 18, "bold")).pack(
            anchor="w"
        )
        ttk.Label(
            header,
            text="Team cards only: typing, role, and move mix per slot.",
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        # Metrics banner if payload metrics exist
        self.metrics = getattr(self, "metrics", {})
        metrics_frame = tk.Frame(wrapper, bg=POKEDEX_BLUE, padx=8, pady=6, highlightthickness=0, bd=0)
        metrics_frame.pack(fill="x", pady=(0, 6))
        tk.Label(metrics_frame, text="Team Score:", font=("Segoe UI", 10, "bold"), fg="#f8fafc", bg=POKEDEX_BLUE).pack(side="left", padx=(0, 6))
        tk.Label(metrics_frame, textvariable=self.score_text_var, font=("Segoe UI", 10), fg="#f8fafc", bg=POKEDEX_BLUE).pack(side="left")
        tk.Button(
            metrics_frame,
            text="Tell me more",
            bg=POKEDEX_RED,
            fg="#f8fafc",
            activebackground="#c01010",
            activeforeground="#f8fafc",
            relief="flat",
            command=self._show_team_breakdown,
            padx=10,
            pady=4,
        ).pack(side="right")

        self.final_panel = ttk.Labelframe(wrapper, text="Team (6 slots)", style="Glass.TLabelframe")
        self.final_panel.pack(fill="both", expand=True)

        self.final_panel_inner = ttk.Frame(self.final_panel, padding=10)
        self.final_panel_inner.pack(fill="both", expand=True)
        for col in range(3):
            self.final_panel_inner.columnconfigure(col, weight=1, uniform="cards")

        status_bar = tk.Frame(wrapper, bg=POKEDEX_DARK, padx=6, pady=4, highlightthickness=0, bd=0)
        status_bar.pack(fill="x", pady=(8, 0))
        tk.Label(
            status_bar,
            textvariable=self.status_var,
            font=("Segoe UI", 9, "italic"),
            fg="#f8fafc",
            bg=POKEDEX_DARK,
            anchor="w",
        ).pack(fill="x")

    def _load_types(self):
        try:
            details = fetch_types()
            matrix = build_matrix(details)
            self.types = [d["name"] for d in details]
            self.matrix = matrix
            self.status_var.set("Types loaded.")
            self._redraw()
            # if payload, refresh panel now that matrix is ready
            self._render_payload_panel()
        except Exception as exc:
            self.status_var.set(f"Failed to load types: {exc}")
            messagebox.showerror("Error", f"Failed to load types:\n{exc}")

    def add_pokemon(self):
        name = self.name_entry.get().strip()
        if not name:
            return
        slot = next((i for i, m in enumerate(self.team) if not m["types"]), None)
        if slot is None:
            messagebox.showinfo("Team full", "All 6 slots are filled. Remove one first.")
            return
        self.status_var.set(f"Loading typing for {name}...")
        threading.Thread(target=self._add_pokemon_thread, args=(name, slot), daemon=True).start()

    def _add_pokemon_thread(self, name, slot):
        try:
            types = fetch_pokemon_typing(name)
            self.team[slot] = {"name": name, "types": types, "source": "api"}
            self.status_var.set(f"Added {name} ({', '.join(types)})")
            self.cached_move_blocks[slot] = None
            self._render_payload_panel()
        except Exception as exc:
            self.status_var.set(f"Failed to load {name}: {exc}")
            messagebox.showerror("Error", f"Failed to load {name}:\n{exc}")

    def apply_manual(self):
        slot = next((i for i, m in enumerate(self.team) if not m["types"]), None)
        if slot is None:
            slot = 0
        raw = self.manual_entry.get().strip()
        parts = [p.strip().lower() for p in raw.split(",") if p.strip()]
        if not parts:
            return
        self.team[slot] = {"name": "custom", "types": parts, "source": "manual"}
        self.status_var.set(f"Manual types set: {', '.join(parts)} in slot {slot+1}")
        self.cached_move_blocks[slot] = None
        self._render_payload_panel()

    def remove_slot(self, idx):
        self.team[idx] = {"name": "", "types": [], "source": ""}
        self.status_var.set(f"Cleared slot {idx+1}")
        self.cached_move_blocks[idx] = None
        self._render_payload_panel()

    def _render_payload_panel(self):
        for child in self.final_panel_inner.winfo_children():
            child.destroy()

        total_slots = 6
        row = 0
        col = 0
        cols = 3
        for idx in range(total_slots):
            member = self.team[idx] if idx < len(self.team) else {"name": "", "types": [], "source": ""}
            name = member.get("name") or f"Slot {idx+1}"
            types = member.get("types") or []
            role = (member.get("role") or "").lower() or "balanced"
            role_label = role.title() if role else "Unassigned"
            card_style, text_color, bg_color = _get_card_style(self.style, types)

            card = ttk.Frame(self.final_panel_inner, padding=12, style=card_style)
            card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
            self.final_panel_inner.rowconfigure(row, weight=1)

            header = ttk.Frame(card)
            header.pack(fill="x")
            img = None
            if member.get("name"):
                img = self.sprite_cache.get(member["name"])
                if img is None:
                    img = fetch_sprite_image(member["name"])
                    self.sprite_cache[member["name"]] = img
            if img:
                lbl_img = ttk.Label(header, image=img, background=bg_color)
                lbl_img.image = img
                lbl_img.pack(side="left", padx=(0, 10), pady=4)
            ttk.Label(header, text=name.title(), style="CardHeader.TLabel").pack(anchor="w", pady=2, padx=2)

            role_tag = ttk.Label(card, text=f"Role: {role_label}", style="Tag.TLabel")
            role_tag.configure(background=bg_color, foreground=_contrast_color(bg_color))
            role_tag.pack(anchor="w", padx=2, pady=(0, 2))

            type_frame = tk.Frame(card, bg=bg_color, highlightthickness=0, bd=0)
            type_frame.pack(anchor="w", pady=(2, 8))
            if types:
                for t in types:
                    color = TYPE_COLORS.get(t, "#94a3b8")
                    icon = fetch_type_icon(t)
                    if icon:
                        lbl = ttk.Label(type_frame, image=icon, background=bg_color)
                        lbl.image = icon
                        lbl.pack(side="left", padx=2)
                    else:
                        lbl = tk.Label(type_frame, text=t.upper(), bg=color, fg=_contrast_color(color), padx=6, pady=2)
                        lbl.pack(side="left", padx=2)
            else:
                ttk.Label(type_frame, text="Types: --", foreground="#64748b", background=bg_color).pack(anchor="w")
            btn_row = ttk.Frame(card, style=card_style)
            btn_row.pack(fill="x", pady=(6, 0))
            ttk.Button(
                btn_row, text="More details", style="Secondary.TButton", command=lambda m=member: self._show_details(m)
            ).pack(side="left", padx=(0, 6))
            ttk.Button(
                btn_row,
                text="I don't have this",
                style="Primary.TButton",
                command=lambda idx=idx: self._mark_unavailable_idx(idx),
            ).pack(side="left")

            col += 1
            if col >= cols:
                col = 0
                row += 1

    def _get_cached_move_options(self, idx, member):
        """Cache move blocks per slot; movelist is static for payloads."""
        if 0 <= idx < len(self.cached_move_blocks) and self.cached_move_blocks[idx] is not None:
            return self.cached_move_blocks[idx]
        block = self._get_move_options(idx, member)
        if 0 <= idx < len(self.cached_move_blocks):
            self.cached_move_blocks[idx] = block
        return block

    def _summarize_moves(self, moves):
        if not moves:
            return "No moves cached."
        parts = []
        for m in moves[:4]:
            name = (m.get("name") or "(open slot)").replace("-", " ").title()
            mtype = m.get("type", "-")
            cat = m.get("cat", "")
            parts.append(f"{name} [{mtype}/{cat}]")
        return "; ".join(parts)

    def _get_move_options(self, idx, member):
        """Return ordered category->moves for UI flipping."""
        cat_data = member.get("suggested_by_category") or (self.payload_by_cat[idx] if idx < len(self.payload_by_cat) else {})
        moves = member.get("suggested_moves") or (self.payload_moves[idx] if idx < len(self.payload_moves) else [])
        limit = 4
        # Derive categories if missing
        if not cat_data:
            stab = []
            coverage = []
            utility = []
            types = set(member.get("types") or [])
            for m in moves:
                if m.get("cat") == "status":
                    utility.append(m)
                elif m.get("type") in types:
                    stab.append(m)
                else:
                    coverage.append(m)
            cat_data = {"stab": stab[:limit], "coverage": coverage[:limit], "utility": utility[:limit]}
        ordered = []
        label_map = {"stab": "STAB", "coverage": "Coverage", "utility": "Utility"}
        for key in ("stab", "coverage", "utility"):
            mv_list = list(cat_data.get(key) or [])
            mv_list = mv_list[:limit]
            while len(mv_list) < limit and moves:
                # pull extras from the overall move list to fill slots
                extra = moves[len(mv_list) % len(moves)]
                mv_list.append(extra)
            while len(mv_list) < limit:
                mv_list.append({"name": "(open slot)", "type": "-", "cat": "", "method": "choose"})
            if mv_list:
                ordered.append((label_map.get(key, key.title()), mv_list))
        # If we still have nothing, fall back to the raw moves list
        if not ordered and moves:
            trimmed = list(moves[:limit])
            while len(trimmed) < limit:
                trimmed.append({"name": "(open slot)", "type": "-", "cat": "", "method": "choose"})
            ordered.append(("Moves", trimmed))
        return dict(ordered)

    def _show_team_breakdown(self):
        win = tk.Toplevel(self.root)
        win.title("Team Breakdown")
        win.configure(bg="#f7fbff")
        txt = tk.Text(win, wrap="word", width=90, height=28, bg="#f7fbff", relief="flat")
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        metrics = getattr(self, "metrics", {}) or {}
        lines = []
        scores = metrics.get("scores") or {}
        if scores:
            lines.append("Scores:")
            lines.append(
                f" - Overall {scores.get('overall','?')}/100 (Def {scores.get('defense','?')}, Off {scores.get('offense','?')}, Delta headroom {scores.get('delta_headroom','?')})"
            )
            if scores.get("role_penalty"):
                lines.append(f" - Role balance penalty: -{scores['role_penalty']}")
            if scores.get("bst_penalty"):
                lines.append(f" - BST penalty: -{scores['bst_penalty']}")
        exposures = metrics.get("exposures") or []
        if exposures:
            lines.append("\nExposed types (weak > resist+immune):")
            for c in exposures:
                lines.append(
                    f" - {c.get('attack')}: weak {c.get('weak')} vs resist {c.get('resist')} immune {c.get('immune')}"
                )
        roles = metrics.get("role_counts") or {}
        if roles:
            lines.append("\nRole mix:")
            for r, cnt in roles.items():
                lines.append(f" - {r}: {cnt}")
        upgrades = metrics.get("upgrades") or []
        if upgrades:
            lines.append("\nTop upgrade ideas:")
            for line in upgrades:
                lines.append(f" - {line}")
        if not lines:
            lines.append("No metrics available in payload.")
        txt.insert("1.0", "\n".join(lines))
        txt.config(state="disabled")

    def _show_details(self, member):
        win = tk.Toplevel(self.root)
        win.title(f"Details: {member.get('name','(empty)')}")
        win.configure(bg="#f7fbff")
        txt = tk.Text(win, wrap="word", width=80, height=26, bg="#f7fbff", relief="flat")
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        name = member.get("name", "(empty)")
        types = member.get("types", [])
        role = member.get("role", "balanced")
        bst = fetch_base_stat_total(name) if name else 0
        lines = [f"{name.title()} ({'/'.join(types) or '—'})", f"Role: {role.title()} | BST: {bst}"]
        if member.get("coverage_priority"):
            prio = ", ".join(f"{t} ({w})" for t, w in member["coverage_priority"][:6])
            lines.append(f"Coverage priority: {prio}")
        if member.get("weaknesses"):
            weak = ", ".join(f"{w} x{mult}" for w, mult in member["weaknesses"][:6])
            lines.append(f"Weaknesses: {weak}")
        # Coverage vs team exposures
        exposures = set()
        try:
            exposures = {c.get("attack") for c in (self.metrics.get("exposures") or [])}
        except Exception:
            exposures = set()
        move_types = set(member.get("move_types") or [])
        se_hits = set(member.get("se_hits") or [])
        if exposures:
            hits = exposures & se_hits
            neutral = {t for t in exposures if t not in hits and move_types}
            lines.append("\nTeam exposures this mon helps with:")
            lines.append(f" - Super-effective: {', '.join(sorted(hits)) or '—'}")
            lines.append(f" - Neutral: {', '.join(sorted(neutral)) or '—'}")
        moves = member.get("suggested_moves", [])
        if moves:
            lines.append("\nMoves:")
            for mv in moves[:8]:
                lines.append(f" - {mv.get('name','?')} [{mv.get('type','-')}/{mv.get('cat','')}]")
        cats = member.get("suggested_by_category") or {}
        if cats:
            lines.append("\nBy category:")
            for key, mv_list in cats.items():
                nice = key.title()
                mv_txt = ", ".join(m.get("name", "?") for m in mv_list[:4])
                lines.append(f" - {nice}: {mv_txt or '—'}")
        txt.insert("1.0", "\n".join(lines))
        txt.config(state="disabled")

    def _mark_unavailable_idx(self, idx):
        if 0 <= idx < len(self.team):
            name = self.team[idx].get("name", "(empty)")
            # Remove current slot, then attempt to auto-replace using parsed upgrades
            self.team[idx] = {"name": "", "types": [], "source": "unavailable"}
            self.cached_move_blocks[idx] = None
            replaced = self._auto_replace(idx, dropped=name)
            if replaced:
                self.status_var.set(f"Replaced {name} with {replaced}.")
            else:
                self.status_var.set(f"Marked unavailable: {name}. Slot cleared; rerun finalize to replace.")
            self._refresh_metrics_and_ui()
        else:
            self.status_var.set("Invalid slot to mark unavailable.")

    def _parse_upgrades(self, lines):
        """Parse upgrade lines into candidate names in order."""
        names = []
        for line in lines:
            try:
                clean = re.sub(r"\x1b\[[0-9;]*m", "", line)
                if "Overall " in clean:
                    segment = clean.split("Overall ", 1)[1]
                    cand = segment.split(":")[0].strip()
                    names.append(cand.lower())
            except Exception:
                continue
        return names

    def _auto_replace(self, idx, dropped=None):
        """Fill a cleared slot with the best upgrade candidate not already on the team."""
        current_names = {m.get("name", "").lower() for m in self.team if m.get("name")}
        # Rebuild upgrade list fresh each time from raw to avoid running out
        available = [c for c in self._parse_upgrades(self.upgrades_raw) if c not in current_names and c != (dropped or "").lower()]
        if not available:
            return None
        cand = available[0]
        try:
            types = fetch_pokemon_typing(cand)
        except Exception:
            types = []
        self.team[idx] = {"name": cand, "types": types, "source": "upgrade"}
        self.cached_move_blocks[idx] = None
        return cand.title()

    def _ensure_types(self):
        if getattr(self, "matrix", None):
            return
        try:
            details = fetch_types()
            self.types = [d["name"] for d in details]
            self.matrix = build_matrix(details)
        except Exception:
            self.types = []
            self.matrix = {}

    def _refresh_metrics_and_ui(self, initial=False):
        """Recompute simple metrics locally and refresh top banner/status."""
        # If we already have scores from payload and it's the initial render, prefer those
        if initial and self.metrics.get("scores"):
            sc = self.metrics["scores"]
            self.score_text_var.set(
                f"Overall {sc.get('overall','?')}/100 | Def {sc.get('defense','?')}/100 | Off {sc.get('offense','?')}/100"
            )
            return
        self._ensure_types()
        chart = getattr(self, "matrix", {})
        attack_types = list(chart.keys())
        if not attack_types:
            self.score_text_var.set("No metrics")
            return
        cov = compute_coverage(self.team, chart)
        def_score = typing_score(cov)
        stack_overlap = sum(max(0, c["weak"] - 1) for c in cov)
        # Use available move data if present
        team_infos = []
        for m in self.team:
            info = dict(m)
            info.setdefault("suggested_moves", info.get("suggested_moves", []))
            info.setdefault("suggested_by_category", info.get("suggested_by_category", {}))
            info.setdefault("move_types", info.get("move_types", []))
            info.setdefault("se_hits", info.get("se_hits", []))
            info.setdefault("role", info.get("role", "balanced"))
            team_infos.append(info)
        off_score = offense_score_with_bonuses(team_infos, cov, chart, attack_types)
        overall = int(min(100, max(0, (def_score + off_score) / 2 - 2.0 * stack_overlap)))
        exposures = [c for c in cov if c["weak"] > (c["resist"] + c["immune"])]
        role_counts = {}
        for info in self.team:
            role = (info.get("role") or "balanced").lower()
            role_counts[role] = role_counts.get(role, 0) + 1
        self.metrics = {
            "scores": {
                "overall": overall,
                "defense": def_score,
                "offense": off_score,
                "stack_overlap": stack_overlap,
                "delta_headroom": max(
                    0,
                    min(
                        100,
                        100
                        - max(
                            (c["weak"] - (c["resist"] + c["immune"])) for c in cov + [{"weak": 0, "resist": 0, "immune": 0}]
                        ),
                    ),
                ),
            },
            "exposures": exposures,
            "role_counts": role_counts,
            "upgrades": self.upgrades_raw,
        }
        self.score_text_var.set(f"Overall {overall}/100 | Def {def_score}/100 | Off {off_score}/100")
        if not initial:
            self._render_payload_panel()
def _apply_tracing():
    """Wrap module-level functions with trace_call for entry/exit visibility."""
    if not TRACE_FUNCTIONS:
        return
    skip = {"trace_call", "_apply_tracing"}
    for name, fn in list(globals().items()):
        if callable(fn) and getattr(fn, "__module__", None) == __name__ and not name.startswith("_") and name not in skip:
            globals()[name] = trace_call(fn)


_apply_tracing()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
