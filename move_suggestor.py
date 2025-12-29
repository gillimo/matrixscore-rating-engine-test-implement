import os
import sys
import re
import json
import requests
from pathlib import Path
from collections import defaultdict

from globals import TOTAL_POKEMON_FOR_MOVE_FETCH, POKEMON_MOVES_FETCHED

POKEAPI_BASE = "https://pokeapi.co/api/v2"
EXCLUDED_TYPES = {"shadow", "unknown"}
MOVE_VERSION_FALLBACKS = [
    "legends-za",
    "scarlet-violet",
    "the-indigo-disk",
    "the-teal-mask",
    "sword-shield",
]
TRACE_FUNCTIONS = False  # tracing hard-disabled to avoid noisy logs
MOVE_CACHE_PATH = Path(__file__).with_name("move_cache.json")
TYPE_CACHE_PATH = Path(__file__).with_name("type_chart_cache.json")
POKEMON_CACHE_PATH = Path(__file__).with_name("pokemon_cache.json")
MOVE_CACHE = {}
MOVE_CACHE_STATS = {"hit": 0, "miss": 0, "persist_fail": 0}
def _load_move_cache():
    global MOVE_CACHE
    if MOVE_CACHE:
        return
    if MOVE_CACHE_PATH.exists():
        try:
            MOVE_CACHE = json.loads(MOVE_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            MOVE_CACHE = {}

def _load_pokemon_cache():
    global POKEMON_CACHE
    if POKEMON_CACHE:
        return
    if POKEMON_CACHE_PATH.exists():
        try:
            POKEMON_CACHE = json.loads(POKEMON_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            POKEMON_CACHE = {}

_load_move_cache() # Load cache once at module import
TYPE_CHART_GLOBAL_CACHE = {} # In-memory cache for type chart
TYPE_CACHE_STATS = {"hit": 0, "miss": 0}
POKEMON_CACHE = {}
POKEMON_CACHE_STATS = {"hit": 0, "miss": 0}
_load_pokemon_cache() # Load cache once at module import
ROLE_MOVE_MIX = {
    "sweeper": "Prefers strong STAB and coverage moves to maximize offensive pressure.",
    "tank": "Prefers defensive moves, a heal/soak option when available, and tools that absorb damage.",
    "balanced": "Prefers a balanced mix of STAB, coverage, and utility tuned to the team.",
}


# Lightweight progress helpers (prefers tqdm if installed).
def _fallback_tqdm(iterable, total=None, desc=None):
    # This function is now always silent to avoid individual progress spam
    # The consolidated progress bar in team_cli_v3.py handles the progress reporting.
    for item in iterable:
        yield item
    return

_real_tqdm = None # Force fallback tqdm as per user request to control progress bar


def progress(msg: str):
    print(f"[progress] {msg}")


def tqdm_iter(iterable, total=None, desc=None):
    if _real_tqdm:
        return _real_tqdm(iterable, total=total, desc=desc, leave=False)
    return _fallback_tqdm(iterable, total=total, desc=desc)





def _save_move_cache():
    try:
        MOVE_CACHE_PATH.write_text(json.dumps(MOVE_CACHE), encoding="utf-8")
    except Exception:
        MOVE_CACHE_STATS["persist_fail"] += 1


def _save_type_chart():
    global TYPE_CHART_GLOBAL_CACHE
    if not TYPE_CHART_GLOBAL_CACHE: # Only save if populated
        return
    try:
        TYPE_CACHE_PATH.write_text(json.dumps({"chart": TYPE_CHART_GLOBAL_CACHE}), encoding="utf-8")
    except Exception:
        TYPE_CACHE_STATS["persist_fail"] += 1 # Or add a specific persist fail stat for type cache




def _save_pokemon_cache():
    try:
        POKEMON_CACHE_PATH.write_text(json.dumps(POKEMON_CACHE), encoding="utf-8")
    except Exception:
        POKEMON_CACHE_STATS["persist_fail"] += 1


def get_move_cache_stats():
    return dict(MOVE_CACHE_STATS)

def save_all_caches():
    _save_move_cache()
    _save_type_chart() # Save type chart if it was loaded/modified.
    _save_pokemon_cache() # Save pokemon cache if it was loaded/modified.

# Lightweight tracing to show entry/exit of functions for progress visibility.
def trace_call(fn):
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        return result
    return wrapper


# Allowed moves list (normalized to PokeAPI-style hyphenated lowercase)
ALLOWED_MOVES_RAW = """
10 000 000 Volt Thunderbolt
Absorb
Accelerock
Acid
Acid Armor
Acid Downpour
Acid Spray
Acrobatics
Acupressure
Aerial Ace
Aeroblast
After You
Agility
Air Cutter
Air Slash
All Out Pummeling
Alluring Voice
Ally Switch
Amnesia
Anchor Shot
Ancient Power
Apple Acid
Aqua Cutter
Aqua Jet
Aqua Ring
Aqua Step
Aqua Tail
Arm Thrust
Armor Cannon
Aromatherapy
Aromatic Mist
Assist
Assurance
Astonish
Astral Barrage
Attack Order
Attract
Aura Sphere
Aura Wheel
Aurora Beam
Aurora Veil
Autotomize
Avalanche
Axe Kick
Baby Doll Eyes
Baddy Bad
Baneful Bunker
Barb Barrage
Barrage
Barrier
Baton Pass
Beak Blast
Beat Up
Behemoth Bash
Behemoth Blade
Belch
Belly Drum
Bestow
Bide
Bind
Bite
Bitter Blade
Bitter Malice
Black Hole Eclipse
Blast Burn
Blaze Kick
Blazing Torque
Bleakwind Storm
Blizzard
Block
Blood Moon
Bloom Doom
Blue Flare
Body Press
Body Slam
Bolt Beak
Bolt Strike
Bone Club
Bone Rush
Bonemerang
Boomburst
Bounce
Bouncy Bubble
Branch Poke
Brave Bird
Breaking Swipe
Breakneck Blitz
Brick Break
Brine
Brutal Swing
Bubble
Bubble Beam
Bug Bite
Bug Buzz
Bulk Up
Bulldoze
Bullet Punch
Bullet Seed
Burn Up
Burning Bulwark
Burning Jealousy
Buzzy Buzz
Calm Mind
Camouflage
Captivate
Catastropika
Ceaseless Edge
Celebrate
Charge
Charge Beam
Charm
Chatter
Chilling Water
Chilly Reception
Chip Away
Chloroblast
Circle Throw
Clamp
Clanging Scales
Clangorous Soul
Clangorous Soulblaze
Clear Smog
Close Combat
Coaching
Coil
Collision Course
Combat Torque
Comet Punch
Comeuppance
Confide
Confuse Ray
Confusion
Constrict
Continental Crush
Conversion
Conversion 2
Copycat
Core Enforcer
Corkscrew Crash
Corrosive Gas
Cosmic Power
Cotton Guard
Cotton Spore
Counter
Court Change
Covet
Crabhammer
Crafty Shield
Cross Chop
Cross Poison
Crunch
Crush Claw
Crush Grip
Curse
Cut
Dark Pulse
Dark Void
Darkest Lariat
Dazzling Gleam
Decorate
Defend Order
Defense Curl
Defog
Destiny Bond
Detect
Devastating Drake
Diamond Storm
Dig
Dire Claw
Disable
Disarming Voice
Discharge
Dive
Dizzy Punch
Doodle
Doom Desire
Double Edge
Double Hit
Double Iron Bash
Double Kick
Double Shock
Double Slap
Double Team
Draco Meteor
Dragon Ascent
Dragon Breath
Dragon Cheer
Dragon Claw
Dragon Dance
Dragon Darts
Dragon Energy
Dragon Hammer
Dragon Pulse
Dragon Rage
Dragon Rush
Dragon Tail
Drain Punch
Draining Kiss
Dream Eater
Drill Peck
Drill Run
Drum Beating
Dual Chop
Dual Wingbeat
Dynamax Cannon
Dynamic Punch
Earth Power
Earthquake
Echoed Voice
Eerie Impulse
Eerie Spell
Egg Bomb
Electric Terrain
Electrify
Electro Ball
Electro Drift
Electro Shot
Electroweb
Embargo
Ember
Encore
Endeavor
Endure
Energy Ball
Entrainment
Eruption
Esper Wing
Eternabeam
Expanding Force
Explosion
Extrasensory
Extreme Evoboost
Extreme Speed
Facade
Fairy Lock
Fairy Wind
Fake Out
Fake Tears
False Surrender
False Swipe
Feather Dance
Feint
Feint Attack
Fell Stinger
Fickle Beam
Fiery Dance
Fiery Wrath
Fillet Away
Final Gambit
Fire Blast
Fire Fang
Fire Lash
Fire Pledge
Fire Punch
Fire Spin
First Impression
Fishious Rend
Fissure
Flail
Flame Burst
Flame Charge
Flame Wheel
Flamethrower
Flare Blitz
Flash
Flash Cannon
Flatter
Fleur Cannon
Fling
Flip Turn
Floaty Fall
Floral Healing
Flower Shield
Flower Trick
Fly
Flying Press
Focus Blast
Focus Energy
Focus Punch
Follow Me
Force Palm
Foresight
Forests Curse
Foul Play
Freeze Dry
Freeze Shock
Freezing Glare
Freezy Frost
Frenzy Plant
Frost Breath
Frustration
Fury Attack
Fury Cutter
Fury Swipes
Fusion Bolt
Fusion Flare
Future Sight
Gastro Acid
Gear Grind
Gear Up
Genesis Supernova
Geomancy
Giga Drain
Giga Impact
Gigaton Hammer
Gigavolt Havoc
Glacial Lance
Glaciate
Glaive Rush
Glare
Glitzy Glow
Grass Knot
Grass Pledge
Grass Whistle
Grassy Glide
Grassy Terrain
Grav Apple
Gravity
Growl
Growth
Grudge
Guard Split
Guard Swap
Guardian Of Alola
Guillotine
Gunk Shot
Gust
Gyro Ball
Hail
Hammer Arm
Happy Hour
Hard Press
Harden
Haze
Head Charge
Head Smash
Headbutt
Headlong Rush
Heal Bell
Heal Block
Heal Order
Heal Pulse
Healing Wish
Heart Stamp
Heart Swap
Heat Crash
Heat Wave
Heavy Slam
Helping Hand
Hex
Hidden Power
High Horsepower
High Jump Kick
Hold Back
Hold Hands
Hone Claws
Horn Attack
Horn Drill
Horn Leech
Howl
Hurricane
Hydro Cannon
Hydro Pump
Hydro Steam
Hydro Vortex
Hyper Beam
Hyper Drill
Hyper Fang
Hyper Voice
Hyperspace Fury
Hyperspace Hole
Hypnosis
Ice Ball
Ice Beam
Ice Burn
Ice Fang
Ice Hammer
Ice Punch
Ice Shard
Ice Spinner
Icicle Crash
Icicle Spear
Icy Wind
Imprison
Incinerate
Infernal Parade
Inferno
Inferno Overdrive
Infestation
Ingrain
Instruct
Ion Deluge
Iron Defense
Iron Head
Iron Tail
Ivy Cudgel
Jaw Lock
Jet Punch
Judgment
Jump Kick
Jungle Healing
Karate Chop
Kinesis
Kings Shield
Knock Off
Kowtow Cleave
Lands Wrath
Laser Focus
Lash Out
Last Resort
Last Respects
Lava Plume
Leaf Blade
Leaf Storm
Leaf Tornado
Leafage
Leech Life
Leech Seed
Leer
Lets Snuggle Forever
Lick
Life Dew
Light Of Ruin
Light Screen
Light That Burns The Sky
Liquidation
Lock On
Lovely Kiss
Low Kick
Low Sweep
Lucky Chant
Lumina Crash
Lunar Blessing
Lunar Dance
Lunge
Luster Purge
Mach Punch
Magic Coat
Magic Powder
Magic Room
Magical Leaf
Magical Torque
Magma Storm
Magnet Bomb
Magnet Rise
Magnetic Flux
Magnitude
Make It Rain
Malicious Moonsault
Malignant Chain
Mat Block
Matcha Gotcha
Max Airstream
Max Darkness
Max Flare
Max Flutterby
Max Geyser
Max Guard
Max Hailstorm
Max Knuckle
Max Lightning
Max Mindstorm
Max Ooze
Max Overgrowth
Max Phantasm
Max Quake
Max Rockfall
Max Starfall
Max Steelspike
Max Strike
Max Wyrmwind
Me First
Mean Look
Meditate
Mega Drain
Mega Kick
Mega Punch
Megahorn
Memento
Menacing Moonraze Maelstrom
Metal Burst
Metal Claw
Metal Sound
Meteor Assault
Meteor Beam
Meteor Mash
Metronome
Mighty Cleave
Milk Drink
Mimic
Mind Blown
Mind Reader
Minimize
Miracle Eye
Mirror Coat
Mirror Move
Mirror Shot
Mist
Mist Ball
Misty Explosion
Misty Terrain
Moonblast
Moongeist Beam
Moonlight
Morning Sun
Mortal Spin
Mountain Gale
Mud Bomb
Mud Shot
Mud Slap
Mud Sport
Muddy Water
Multi Attack
Mystical Fire
Mystical Power
Nasty Plot
Natural Gift
Nature Power
Natures Madness
Needle Arm
Never Ending Nightmare
Night Daze
Night Shade
Night Slash
Nightmare
No Retreat
Noble Roar
Noxious Torque
Nuzzle
Oblivion Wing
Obstruct
Oceanic Operetta
Octazooka
Octolock
Odor Sleuth
Ominous Wind
Order Up
Origin Pulse
Outrage
Overdrive
Overheat
Pain Split
Parabolic Charge
Parting Shot
Pay Day
Payback
Peck
Perish Song
Petal Blizzard
Petal Dance
Phantom Force
Photon Geyser
Pika Papow
Pin Missile
Plasma Fists
Play Nice
Play Rough
Pluck
Poison Fang
Poison Gas
Poison Jab
Poison Powder
Poison Sting
Poison Tail
Pollen Puff
Poltergeist
Population Bomb
Pounce
Pound
Powder
Powder Snow
Power Gem
Power Shift
Power Split
Power Swap
Power Trick
Power Trip
Power Up Punch
Power Whip
Precipice Blades
Present
Prismatic Laser
Protect
Psybeam
Psyblade
Psych Up
Psychic
Psychic Fangs
Psychic Noise
Psychic Terrain
Psycho Boost
Psycho Cut
Psycho Shift
Psyshield Bash
Psyshock
Psystrike
Psywave
Pulverizing Pancake
Punishment
Purify
Pursuit
Pyro Ball
Quash
Quick Attack
Quick Guard
Quiver Dance
Rage
Rage Fist
Rage Powder
Raging Bull
Raging Fury
Rain Dance
Rapid Spin
Razor Leaf
Razor Shell
Razor Wind
Recover
Recycle
Reflect
Reflect Type
Refresh
Relic Song
Rest
Retaliate
Return
Revelation Dance
Revenge
Reversal
Revival Blessing
Rising Voltage
Roar
Roar Of Time
Rock Blast
Rock Climb
Rock Polish
Rock Slide
Rock Smash
Rock Throw
Rock Tomb
Rock Wrecker
Role Play
Rolling Kick
Rollout
Roost
Rototiller
Round
Ruination
Sacred Fire
Sacred Sword
Safeguard
Salt Cure
Sand Attack
Sand Tomb
Sandsear Storm
Sandstorm
Sappy Seed
Savage Spin Out
Scald
Scale Shot
Scary Face
Scorching Sands
Scratch
Screech
Searing Shot
Searing Sunraze Smash
Secret Power
Secret Sword
Seed Bomb
Seed Flare
Seismic Toss
Self Destruct
Shadow Ball
Shadow Blast
Shadow Blitz
Shadow Bolt
Shadow Bone
Shadow Break
Shadow Chill
Shadow Claw
Shadow Down
Shadow End
Shadow Fire
Shadow Force
Shadow Half
Shadow Hold
Shadow Mist
Shadow Panic
Shadow Punch
Shadow Rave
Shadow Rush
Shadow Shed
Shadow Sky
Shadow Sneak
Shadow Storm
Shadow Wave
Sharpen
Shattered Psyche
Shed Tail
Sheer Cold
Shell Side Arm
Shell Smash
Shell Trap
Shelter
Shift Gear
Shock Wave
Shore Up
Signal Beam
Silk Trap
Silver Wind
Simple Beam
Sing
Sinister Arrow Raid
Sizzly Slide
Sketch
Skill Swap
Skitter Smack
Skull Bash
Sky Attack
Sky Drop
Sky Uppercut
Slack Off
Slam
Slash
Sleep Powder
Sleep Talk
Sludge
Sludge Bomb
Sludge Wave
Smack Down
Smart Strike
Smelling Salts
Smog
Smokescreen
Snap Trap
Snarl
Snatch
Snipe Shot
Snore
Snowscape
Soak
Soft Boiled
Solar Beam
Solar Blade
Sonic Boom
Soul Stealing 7 Star Strike
Spacial Rend
Spark
Sparkling Aria
Sparkly Swirl
Spectral Thief
Speed Swap
Spicy Extract
Spider Web
Spike Cannon
Spikes
Spiky Shield
Spin Out
Spirit Break
Spirit Shackle
Spit Up
Spite
Splash
Splintered Stormshards
Splishy Splash
Spore
Spotlight
Springtide Storm
Stealth Rock
Steam Eruption
Steamroller
Steel Beam
Steel Roller
Steel Wing
Sticky Web
Stockpile
Stoked Sparksurfer
Stomp
Stomping Tantrum
Stone Axe
Stone Edge
Stored Power
Storm Throw
Strange Steam
Strength
Strength Sap
String Shot
Struggle
Struggle Bug
Stuff Cheeks
Stun Spore
Submission
Substitute
Subzero Slammer
Sucker Punch
Sunny Day
Sunsteel Strike
Super Fang
Supercell Slam
Superpower
Supersonic
Supersonic Skystrike
Surf
Surging Strikes
Swagger
Swallow
Sweet Kiss
Sweet Scent
Swift
Switcheroo
Swords Dance
Synchronoise
Synthesis
Syrup Bomb
Tachyon Cutter
Tackle
Tail Glow
Tail Slap
Tail Whip
Tailwind
Take Down
Take Heart
Tar Shot
Taunt
Tearful Look
Teatime
Techno Blast
Tectonic Rage
Teeter Dance
Telekinesis
Teleport
Temper Flare
Tera Blast
Tera Starstorm
Terrain Pulse
Thief
Thousand Arrows
Thousand Waves
Thrash
Throat Chop
Thunder
Thunder Cage
Thunder Fang
Thunder Punch
Thunder Shock
Thunder Wave
Thunderbolt
Thunderclap
Thunderous Kick
Tickle
Tidy Up
Topsy Turvy
Torch Song
Torment
Toxic
Toxic Spikes
Toxic Thread
Trailblaze
Transform
Tri Attack
Trick
Trick Or Treat
Trick Room
Triple Arrows
Triple Axel
Triple Dive
Triple Kick
Trop Kick
Trump Card
Twin Beam
Twineedle
Twinkle Tackle
Twister
U Turn
Upper Hand
Uproar
V Create
Vacuum Wave
Veevee Volley
Venom Drench
Venoshock
Vice Grip
Victory Dance
Vine Whip
Vital Throw
Volt Switch
Volt Tackle
Wake Up Slap
Water Gun
Water Pledge
Water Pulse
Water Shuriken
Water Sport
Water Spout
Waterfall
Wave Crash
Weather Ball
Whirlpool
Whirlwind
Wicked Blow
Wicked Torque
Wide Guard
Wild Charge
Wildbolt Storm
Will O Wisp
Wing Attack
Wish
Withdraw
Wonder Room
Wood Hammer
Work Up
Worry Seed
Wrap
Wring Out
X Scissor
Yawn
Zap Cannon
Zen Headbutt
Zing Zap
Zippy Zap
"""


def normalize_move_name(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace("’", "")
        .replace("'", "")
        .replace(" ", "-")
    )


ALLOWED_MOVES = {normalize_move_name(n) for n in ALLOWED_MOVES_RAW.splitlines() if n.strip()}

# Special move groups for hybrid/control logic
FORCE_FAINT_MOVES = {
    "perish-song",
    "destiny-bond",
    "final-gambit",
    "explosion",
    "self-destruct",
    "memento",
}
FORCE_SWITCH_MOVES = {
    "roar",
    "whirlwind",
    "dragon-tail",
    "circle-throw",
}
FORCE_TRAP_MOVES = {
    "mean-look",
    "spider-web",
    "block",
    "spirit-shackle",
    "anchor-shot",
    "octolock",
}
SLEEP_MOVES = {
    "spore",
    "sleep-powder",
    "lovely-kiss",
    "hypnosis",
    "sing",
    "grass-whistle",
    "yawn",
}
HAZARD_MOVES = {
    "stealth-rock",
    "spikes",
    "toxic-spikes",
    "sticky-web",
    "ceaseless-edge",
    "stone-axe",
}
RECOIL_OR_TRADE_MOVES = {
    "flare-blitz",
    "wild-charge",
    "brave-bird",
    "head-smash",
    "double-edge",
    "takedown",
    "final-gambit",
    "explosion",
    "self-destruct",
    "memento",
    "destiny-bond",
}
OFFENSE_SETUP_MOVES = {
    "swords-dance",
    "nasty-plot",
    "dragon-dance",
    "agility",
    "bulk-up",
    "calm-mind",
    "tailwind",
}
HEAL_SOAK_MOVES = {
    "recover",
    "roost",
    "slack-off",
    "milk-drink",
    "heal-order",
    "shore-up",
    "morning-sun",
    "moonlight",
    "life-dew",
    "strength-sap",
    "rest",
    "protect",
    "kings-shield",
    "baneful-bunker",
    "detect",
}
SCREENS_DEBUFF = {
    "reflect",
    "light-screen",
    "aurora-veil",
    "will-o-wisp",
    "haze",
    "chilling-water",
    "acid-spray",
    "scary-face",
}
BINDING_MOVES = {
    "whirlpool",
    "fire-spin",
    "magma-storm",
    "infestation",
    "bind",
    "clamp",
    "snap-trap",
    "sand-tomb",
    "wrap",
    "constrict",
    "octolock",
}
SELF_WEAK_TYPES = {"ghost", "dragon"}


# Simplified type chart multipliers for attack -> defense
# We will fetch live types for weaknesses, but this fallback helps for coverage logic.
def fetch_type_chart():
    global TYPE_CHART_GLOBAL_CACHE
    if TYPE_CHART_GLOBAL_CACHE:
        TYPE_CACHE_STATS["hit"] += 1
        return TYPE_CHART_GLOBAL_CACHE

    if TYPE_CACHE_PATH.exists():
        try:
            data = json.loads(TYPE_CACHE_PATH.read_text(encoding="utf-8"))
            chart = data.get("chart", {})
            if chart:
                TYPE_CHART_GLOBAL_CACHE = chart
                TYPE_CACHE_STATS["hit"] += 1
                return chart
        except Exception:
            # Cache corrupted, will re-fetch
            pass
    
    TYPE_CACHE_STATS["miss"] += 1
    # Fetch all types
    res = requests.get(f"{POKEAPI_BASE}/type", timeout=15)
    res.raise_for_status()
    type_list = [t["name"] for t in res.json()["results"] if t["name"] not in EXCLUDED_TYPES]
    chart = {t: {} for t in type_list}
    
    # Fetch details for each type
    for t in type_list:
        try:
            d = requests.get(f"{POKEAPI_BASE}/type/{t}", timeout=15).json()
            rel = d["damage_relations"]
            for target in type_list:
                chart[t][target] = 1.0
            for rr in rel["double_damage_to"]:
                chart[t][rr["name"]] = 2.0
            for rr in rel["half_damage_to"]:
                chart[t][rr["name"]] = 0.5
            for rr in rel["no_damage_to"]:
                chart[t][rr["name"]] = 0.0
        except requests.exceptions.RequestException as exc:
            print(f"[ERROR] Failed to fetch details for type '{t}': {exc}")
            # Depending on severity, you might want to re-raise, or return partial chart
            # For now, we'll continue with other types but this type will be incomplete
        except json.JSONDecodeError as exc:
            print(f"[ERROR] Failed to decode JSON for type '{t}': {exc}")
            # Similar to above, skip this type and continue
        except Exception as exc:
            print(f"[ERROR] An unexpected error occurred for type '{t}': {exc}")
    
    # Save to disk cache
    try:
        TYPE_CACHE_PATH.write_text(json.dumps({"chart": chart}), encoding="utf-8")
    except Exception:
        # Log failure to persist cache, but don't prevent returning the chart
        pass
    
    TYPE_CHART_GLOBAL_CACHE = chart
    return chart

def fetch_pokemon(name: str):
    key = name.lower()
    if key in POKEMON_CACHE:
        POKEMON_CACHE_STATS["hit"] += 1
        return POKEMON_CACHE[key]
    POKEMON_CACHE_STATS["miss"] += 1
    res = requests.get(f"{POKEAPI_BASE}/pokemon/{key}", timeout=15)
    res.raise_for_status()
    data = res.json()
    POKEMON_CACHE[key] = data
    return data

def pokemon_in_version(name: str, version_group="legends-za"):
    """Return True if the Pokemon has a game index in the requested version group."""
    data = fetch_pokemon(name)
    return any(gi.get("version", {}).get("name") == version_group for gi in data.get("game_indices", []))

def compute_defensive_weaknesses(types, chart):
    # types: list of defensive types
    weaknesses = []
    for atk_type in chart.keys():
        mult = 1.0
        for dt in types:
            mult *= chart[atk_type].get(dt, 1.0)
        if mult > 1:
            weaknesses.append((atk_type, mult))
    weaknesses.sort(key=lambda x: x[1], reverse=True)
    return weaknesses

def classify_role(stats):
    hp = stats["hp"]
    atk = stats["attack"]
    defe = stats["defense"]
    spa = stats["special-attack"]
    spd = stats["special-defense"]
    spe = stats["speed"]

    # Offense favors main attacking stat + speed; bulk favors HP and defenses
    main_atk = max(atk, spa)
    off_support = min(atk, spa)
    offense = main_atk * 1.2 + off_support * 0.4 + spe * 1.3
    bulk = hp * 1.2 + (defe + spd) * 1.1

    # Sweeper if very fast and offense close to/above bulk, or offense far above bulk
    if spe >= 115 and offense >= bulk * 0.88:
        return "sweeper"
    if offense >= bulk * 1.28:
        return "sweeper"
    # Tank if bulk leads meaningfully and speed is modest
    if spe < 90 and bulk >= offense * 1.05:
        return "tank"
    return "balanced"

def collect_move_pool(poke_json, level_cap=None, version_group="legends-za", fallbacks=None):
    """Return unique moves learnable in the given version group, with fallbacks if empty."""
    groups = [version_group] if version_group else []
    if fallbacks:
        groups += [g for g in fallbacks if g and g != version_group]
    # Always attempt at least once
    if not groups:
        groups = [None]

    for vg in groups:
        moves = []
        for m in poke_json["moves"]:
            name = m["move"]["name"]
            if normalize_move_name(name) not in ALLOWED_MOVES:
                continue
            if vg:
                vg_details = [d for d in m["version_group_details"] if d["version_group"]["name"] == vg]
            else:
                vg_details = m["version_group_details"]
            if not vg_details:
                continue
            d = vg_details[0]
            learn_method = d["move_learn_method"]["name"]
            if learn_method not in ("level-up", "machine", "tutor", "egg"):
                continue
            level = d.get("level_learned_at", 0)
            if level_cap is not None and learn_method == "level-up" and level > level_cap:
                continue
            moves.append((name, learn_method, level))
        if moves:
            return list({m[0]: m for m in moves}.values())
    return []

def fetch_move_detail(name: str):
    key = name.lower()
    if key in MOVE_CACHE:
        MOVE_CACHE_STATS["hit"] += 1
        return MOVE_CACHE[key]
    MOVE_CACHE_STATS["miss"] += 1
    res = requests.get(f"{POKEAPI_BASE}/move/{name}", timeout=15)
    res.raise_for_status()
    data = res.json()
    MOVE_CACHE[key] = data
    return data

def pick_moves(
    name: str,
    level_cap=None,
    exclude_moves=None,
    used_moves=None,
    version_group="legends-za",
    exposed_types=None,
    needed_offense=None,
):
    _load_pokemon_cache()
    chart = fetch_type_chart()
    poke = fetch_pokemon(name)
    types = [t["type"]["name"] for t in sorted(poke["types"], key=lambda x: x["slot"])]
    stats = {s["stat"]["name"]: s["base_stat"] for s in poke["stats"]}
    role = classify_role(stats)
    weaknesses = compute_defensive_weaknesses(types, chart)
    move_pool = collect_move_pool(
        poke,
        level_cap=level_cap,
        version_group=version_group,
        fallbacks=MOVE_VERSION_FALLBACKS,
    )
    exclude_moves = set((exclude_moves or []))
    used_moves = set((used_moves or []))
    exposed_types = set(exposed_types or [])
    needed_offense = set(needed_offense or [])

    # Score moves lazily: fetch details only for candidates
    stab_types = set(types)
    def_type_hits = defaultdict(float)
    for atk_type in chart.keys():
        hit_count = sum(1 for w, mult in weaknesses if chart[atk_type].get(w, 1.0) >= 2.0)
        def_type_hits[atk_type] = hit_count
    coverage_priority = sorted(def_type_hits.items(), key=lambda x: x[1], reverse=True)

    # Grab moves with detail (full pool; Emboar coverage like thunder-punch should appear). Allow duplicate names if they come from different methods/levels; dedupe later by name.
    candidate_moves = []
    eligible_pool = [(mv, method, lvl) for mv, method, lvl in move_pool if mv not in exclude_moves and mv not in used_moves]
    # Cap pool size to limit network fetch; prioritize unique names
    seen_mv = set()
    limited_pool = []
    for mv, method, lvl in eligible_pool:
        if mv in seen_mv:
            continue
        seen_mv.add(mv)
        limited_pool.append((mv, method, lvl))
        if len(limited_pool) >= 120:
            break
    total_moves = len(limited_pool)
    for mv, method, lvl in limited_pool:
        try:
            md = fetch_move_detail(mv)
        except Exception:
            continue
        mtype = md["type"]["name"]
        category = md["damage_class"]["name"]
        power = md.get("power") or 0
        accuracy = md.get("accuracy") or 100
        candidate_moves.append(
            {
                "name": mv,
                "type": mtype,
                "cat": category,
                "power": power,
                "acc": accuracy,
                "method": method,
                "level": lvl,
                "priority": md.get("priority", 0),
            }
        )

    physical = stats["attack"] >= stats["special-attack"]

    def move_score(m):
        cat_match = (m["cat"] == "physical" and physical) or (m["cat"] == "special" and not physical)
        stab = m["type"] in stab_types
        base = m["power"] if m["power"] else 0
        score = base
        if stab:
            score += 30
        if cat_match:
            score += 15
        score += def_type_hits[m["type"]] * 25  # weight coverage count higher
        # Coverage bonus for exposed/needed types
        coverage_bonus = 0
        for t in exposed_types:
            mult = chart[m["type"]].get(t, 1.0)
            if mult >= 2.0:
                coverage_bonus += 40
            elif mult >= 1.0:
                coverage_bonus += 15
        # Light bonus for broader offense needs
        for t in needed_offense:
            mult = chart[m["type"]].get(t, 1.0)
            if mult >= 2.0:
                coverage_bonus += 5
        score += coverage_bonus
        score += m["priority"] * 10
        return score

    # Bucket moves
    stab_moves = [m for m in candidate_moves if m["type"] in stab_types and m["cat"] != "status"]
    coverage_moves = [m for m in candidate_moves if m["type"] not in stab_types and m["cat"] != "status"]
    status_moves = [m for m in candidate_moves if m["cat"] == "status"]

    def status_score(m):
        name = m["name"]
        nname = normalize_move_name(name)
        base = def_type_hits[m["type"]] * 10
        if nname in FORCE_FAINT_MOVES:
            base += 120
        if nname in HAZARD_MOVES:
            base += 80
        if nname in FORCE_SWITCH_MOVES:
            base += 60
        if nname in FORCE_TRAP_MOVES:
            base += 50
        if nname in SLEEP_MOVES:
            base += 70
        if m.get("priority", 0) > 0:
            base += 10
        # Coverage utility bonus
        for t in exposed_types:
            mult = chart[m["type"]].get(t, 1.0)
            if mult >= 2.0:
                base += 25
            elif mult >= 1.0:
                base += 8
        return base

    stab_sorted = sorted(stab_moves, key=move_score, reverse=True)
    cov_sorted = sorted(
        coverage_moves,
        key=lambda m: (def_type_hits[m["type"]], move_score(m)),
        reverse=True,
    )
    stat_sorted = sorted(status_moves, key=status_score, reverse=True)

    suggested_by_category = {
        "stab": stab_sorted[:4],
        "coverage": cov_sorted[:4],
        "utility": stat_sorted[:4],
    }

    def role_alignment_label(m):
        nname = normalize_move_name(m["name"])
        if m["cat"] == "status":
            if nname in FORCE_FAINT_MOVES:
                return "force_faint"
            if nname in FORCE_SWITCH_MOVES:
                return "force_switch"
            if nname in FORCE_TRAP_MOVES or nname in BINDING_MOVES:
                return "trap"
            if nname in HAZARD_MOVES:
                return "hazard"
            if nname in SLEEP_MOVES:
                return "sleep"
            if nname in HEAL_SOAK_MOVES:
                return "heal"
            if nname in SCREENS_DEBUFF:
                return "screen"
            if nname in OFFENSE_SETUP_MOVES:
                return "setup_offense"
            return "status_other"
        else:
            if nname in RECOIL_OR_TRADE_MOVES:
                return "recoil"
            if m["type"] in stab_types:
                return "stab_offense"
            return "coverage_offense"

    suggestions = []
    # Ensure self-weak typings (ghost/dragon) carry STAB of that type; this is the highest priority.
    self_weak_types = set(types) & SELF_WEAK_TYPES
    if self_weak_types:
        for self_weak_type in self_weak_types:
            fallback = next((m for m in stab_sorted if m["type"] == self_weak_type), None)
            if fallback and fallback not in suggestions:
                suggestions.append(fallback)

    # Dual-typing rule: ensure at least one STAB move for each type if available.
    if len(types) == 2:
        for t in types:
            stab_pick = next((m for m in stab_sorted if m["type"] == t), None)
            if not stab_pick:
                stab_pick = next((m for m in candidate_moves if m["type"] == t), None)
            if stab_pick and stab_pick not in suggestions:
                suggestions.append(stab_pick)

    # Role-specific priorities
    if role == "sweeper":
        # Strongest STAB, coverage, priority, recoil/trade, then filler coverage/setup
        if stab_sorted:
            for m in stab_sorted:
                if m not in suggestions:
                    suggestions.append(m)
                    break
        if cov_sorted:
            for m in cov_sorted:
                if m not in suggestions:
                    suggestions.append(m)
                    break
        prio_moves = [m for m in stab_sorted + cov_sorted if m.get("priority", 0) > 0]
        if prio_moves:
            for m in prio_moves:
                if m not in suggestions:
                    suggestions.append(m)
                    break
        recoil_moves = [m for m in stab_sorted + cov_sorted if normalize_move_name(m["name"]) in RECOIL_OR_TRADE_MOVES]
        if recoil_moves:
            for m in recoil_moves:
                if m not in suggestions:
                    suggestions.append(m)
                    break
        # Fill with best coverage
        for m in cov_sorted:
            if len(suggestions) >= 4:
                break
            if m not in suggestions:
                suggestions.append(m)
        # If still room, offensive setup
        if len(suggestions) < 4:
            setup_moves = [m for m in stat_sorted if normalize_move_name(m["name"]) in OFFENSE_SETUP_MOVES]
            for m in setup_moves:
                if len(suggestions) >= 4:
                    break
                if m not in suggestions:
                    suggestions.append(m)
    elif role == "tank":
        # Heal/soak -> screen/debuff -> hazard/trap -> coverage -> stab -> any status
        heal_pool = [m for m in stat_sorted if normalize_move_name(m["name"]) in HEAL_SOAK_MOVES]
        screen_pool = [m for m in stat_sorted if normalize_move_name(m["name"]) in SCREENS_DEBUFF]
        hazard_pool = [m for m in stat_sorted if normalize_move_name(m["name"]) in HAZARD_MOVES or normalize_move_name(m["name"]) in BINDING_MOVES or normalize_move_name(m["name"]) in FORCE_TRAP_MOVES]
        if heal_pool:
            for m in heal_pool:
                if m not in suggestions:
                    suggestions.append(m)
                    break
        for m in screen_pool:
            if len(suggestions) >= 4:
                break
            if m not in suggestions:
                suggestions.append(m)
        for m in hazard_pool:
            if len(suggestions) >= 4:
                break
            if m not in suggestions:
                suggestions.append(m)
        for m in cov_sorted:
            if len(suggestions) >= 4:
                break
            if m not in suggestions:
                suggestions.append(m)
        for m in stab_sorted:
            if len(suggestions) >= 4:
                break
            if m not in suggestions:
                suggestions.append(m)
        if len(suggestions) < 4:
            for m in stat_sorted:
                if len(suggestions) >= 4:
                    break
                if m not in suggestions:
                    suggestions.append(m)
    else:  # balanced/hybrid
        # Require 1 status first (stat_sorted already favors control/force-faint/hazard/sleep)
        if stat_sorted:
            for m in stat_sorted:
                if m not in suggestions:
                    suggestions.append(m)
                    break
        extra_status = [m for m in stat_sorted if m not in suggestions]
        buff_moves = [m for m in extra_status if normalize_move_name(m["name"]) in OFFENSE_SETUP_MOVES or normalize_move_name(m["name"]) in SCREENS_DEBUFF]
        if buff_moves:
            for m in buff_moves:
                if m not in suggestions:
                    suggestions.append(m)
                    break
        if stab_sorted:
            for m in stab_sorted:
                if m not in suggestions:
                    suggestions.append(m)
                    break
        if cov_sorted:
            for m in cov_sorted:
                if m not in suggestions:
                    suggestions.append(m)
                    break
        if len(suggestions) < 4:
            for m in extra_status:
                if len(suggestions) >= 4:
                    break
                if m not in suggestions:
                    suggestions.append(m)

    # Deduplicate while preserving order; keep up to 4
    seen = set()
    final_moves = []
    for m in suggestions:
        if m["name"] in seen:
            continue
        seen.add(m["name"])
        final_moves.append(m)
        if len(final_moves) >= 4:
            break
    # If still short, fill from best coverage/STAB/utility
    if len(final_moves) < 4:
        for m in cov_sorted + stab_sorted + stat_sorted:
            if m["name"] in seen:
                continue
            seen.add(m["name"])
            final_moves.append(m)
            if len(final_moves) >= 4:
                break

    # Draft board: top 12 unique moves favoring coverage/STAB/utility
    draft_board = []
    seen_board = set()
    for m in cov_sorted + stab_sorted + stat_sorted:
        if m["name"] in seen_board:
            continue
        draft_board.append(m)
        seen_board.add(m["name"])
        if len(draft_board) >= 12:
            break
    if not draft_board:
        draft_board = final_moves[:]
    if len(types) == 2:
        required_stabs = []
        for t in types:
            stab_pick = next((m for m in stab_sorted if m["type"] == t), None)
            if not stab_pick:
                stab_pick = next((m for m in candidate_moves if m["type"] == t), None)
            if stab_pick and stab_pick["name"] not in {m["name"] for m in required_stabs}:
                required_stabs.append(stab_pick)
        if required_stabs:
            existing = [m for m in draft_board if m["name"] not in {r["name"] for r in required_stabs}]
            draft_board = (required_stabs + existing)[:12]

    # Alignment score: how well moves fit role priorities
    role_weights = {
        "sweeper": {
            "stab_offense": 15,
            "coverage_offense": 12,
            "recoil": 10,
            "setup_offense": 8,
            "priority": 5,
        },
        "tank": {
            "heal": 26,
            "screen": 15,
            "hazard": 12,
            "trap": 10,
            "sleep": 8,
            "coverage_offense": 6,
            "stab_offense": 4,
            "status_other": 3,
        },
        "balanced": {
            "force_faint": 18,
            "sleep": 14,
            "hazard": 12,
            "trap": 10,
            "force_switch": 9,
            "screen": 8,
            "heal": 6,
            "stab_offense": 6,
            "coverage_offense": 5,
            "setup_offense": 5,
            "status_other": 3,
        },
    }
    weights = role_weights.get(role, role_weights["balanced"])
    max_w = max(weights.values()) if weights else 1
    total = 0
    for m in final_moves:
        label = role_alignment_label(m)
        score = weights.get(label, 0)
        if m.get("priority", 0) > 0 and role == "sweeper":
            score += weights.get("priority", 0)
        total += score
    max_possible = max_w * max(1, len(final_moves))
    alignment_score = int(max(0, min(100, (total / max_possible) * 100)))

    _save_move_cache()
    _save_pokemon_cache()
    return {
        "name": name,
        "types": types,
        "role": role,
        "weaknesses": weaknesses,
        "coverage_priority": coverage_priority,
        "suggested_moves": final_moves,
        "suggested_by_category": suggested_by_category,
        "draft_board": draft_board,
        "alignment_score": alignment_score,
    }

def format_output(info):
    lines = []
    role_profiles = {
        "sweeper": "Sweeper profile: 2 coverage moves (hit most weaknesses), 1 STAB (aligned to main offensive stat), 1 buff/utility if present.",
        "tank": "Tank profile: 1 heal/soak if available, 1 screen/defensive debuff, 1 STAB, 1 coverage beater (highest weakness coverage).",
        "balanced": "Hybrid profile: self buff/defense, 1 STAB, 1 coverage, optional utility.",
    }
    lines.append(f"Pokemon: {info['name'].title()} ({'/'.join(info['types'])})")
    lines.append(f"Role: {info['role']}")
    if info.get("alignment_score") is not None:
        lines.append(f"Move alignment score: {info['alignment_score']}/100")
    if info["role"] in role_profiles:
        lines.append(role_profiles[info["role"]])
    weak_str = ", ".join(f"{w} x{mult}" for w, mult in info["weaknesses"][:6]) or "None"
    lines.append(f"Weaknesses: {weak_str}")
    cov_str = ", ".join(f"{t}({cnt})" for t, cnt in info["coverage_priority"] if cnt > 0) or "None"
    lines.append(f"Coverage priority (types hitting weaknesses): {cov_str}")
    top_cov = [
        f"{idx}) {t} (hits {cnt} weakness{'es' if cnt != 1 else ''})"
        for idx, (t, cnt) in enumerate(
            [c for c in info["coverage_priority"] if c[1] > 0][:5], start=1
        )
    ]
    if top_cov:
        lines.append("Coverage ranking: " + "; ".join(top_cov))
    lines.append("Suggested moves:")
    for m in info["suggested_moves"]:
        method = m.get("method", "unknown")
        cat = m.get("cat", "")
        lvl = m.get("level")
        lvl_txt = f" lvl {lvl}" if method == "level-up" and lvl else ""
        lines.append(
            f" - {m.get('name','?')} [{m.get('type','-')}/{cat}] pow={m.get('power','?')} acc={m.get('acc','?')} via {method}{lvl_txt}"
        )
    lines.append("Top by category:")
    for cat_label, moves in (
        ("STAB", info["suggested_by_category"].get("stab", [])),
        ("Coverage", info["suggested_by_category"].get("coverage", [])),
        ("Utility", info["suggested_by_category"].get("utility", [])),
    ):
        if not moves:
            lines.append(f" {cat_label}: none")
            continue
        lines.append(f" {cat_label}:")
        for idx, m in enumerate(moves, start=1):
            method = m.get("method", "unknown")
            cat = m.get("cat", "")
            lvl = m.get("level")
            lvl_txt = f" lvl {lvl}" if method == "level-up" and lvl else ""
            lines.append(
                f"   {idx}) {m.get('name','?')} [{m.get('type','-')}/{cat}] pow={m.get('power','?')} acc={m.get('acc','?')} via {method}{lvl_txt}"
            )
    return "\n".join(lines)

def format_team(team_infos):
    if not team_infos:
        return "Team: (none)"
    lines = ["\n=== Team Summary ==="]
    for info in team_infos:
        lines.append(f"{info['name'].title()} ({'/'.join(info['types'])}) - role: {info['role']}")
        for m in info["suggested_moves"]:
            lvl_txt = f" lvl {m['level']}" if m["method"] == "level-up" and m["level"] else ""
            lines.append(f"  - {m['name']} [{m['type']}/{m['cat']}] via {m['method']}{lvl_txt}")
        lines.append("")
    return "\n".join(lines)

def main():
    global_exclude = set()
    team_infos = []
    done_all = False

    def parse_name_and_level(raw: str):
        tokens = raw.split()
        level_tokens = [t for t in tokens if t.isdigit()]
        level_cap = int(level_tokens[-1]) if level_tokens else None
        name_tokens = [t for t in tokens if not t.isdigit()]
        name = " ".join(name_tokens).strip()
        return name, level_cap

    while True:
        raw = input("Enter Pokemon name (or 'done' to finish team; you can add level e.g., emboar 45): ").strip()
        if not raw:
            continue
        if raw.lower() == "done":
            break
        name, level_cap = parse_name_and_level(raw)
        if not name:
            print("Please provide a Pokemon name.")
            continue

        current_info = None
        while True:
            try:
                lvl_msg = f" up to level {level_cap}" if level_cap is not None else ""
                ex_msg = f", excluding {', '.join(sorted(global_exclude))}" if global_exclude else ""
                print(f"Fetching data for {name} from PokeAPI{lvl_msg}{ex_msg}...")
                info = pick_moves(name, level_cap=level_cap, exclude_moves=global_exclude)
                current_info = info
            except Exception as exc:
                print(f"Error: {exc}")
                current_info = None
                break
            print("Done. Suggestions:")
            print(format_output(info))

            user_in = input("Enter moves to exclude (comma), 'next' for new Pokemon, 'done' to finish team: ").strip()
            if not user_in or user_in.lower() == "next":
                if current_info:
                    team_infos.append(current_info)
                break
            if user_in.lower() == "done":
                if current_info:
                    team_infos.append(current_info)
                done_all = True
                break
            new_ex = [m.strip().lower() for m in user_in.split(",") if m.strip()]
            global_exclude.update(new_ex)

        if done_all:
            break

    print(format_team(team_infos))


def _apply_tracing():
    """Tracing disabled; no-op."""
    return


_apply_tracing()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
