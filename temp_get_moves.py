import sys
import json
import requests
from pathlib import Path

POKEAPI_BASE = "https://pokeapi.co/api/v2"

def get_pokemon_moves_from_api(name: str):
    key = name.lower()
    try:
        res = requests.get(f"{POKEAPI_BASE}/pokemon/{key}", timeout=15)
        res.raise_for_status()
        data = res.json()
        moves = []
        for move_entry in data.get("moves", []):
            moves.append(move_entry["move"]["name"])
        return moves
    except requests.exceptions.RequestException as e:
        print(f"Error fetching moves for {name}: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python temp_get_moves.py <pokemon_name>", file=sys.stderr)
        sys.exit(1)
    
    pokemon_name = sys.argv[1]
    moves = get_pokemon_moves_from_api(pokemon_name)
    print(json.dumps(moves))
