import json
import sys
sys.path.insert(0, '.')
from team_cli_dlc import ZA_POKEDEX

# Load cache
with open('pokemon_cache.json') as f:
    cache = json.load(f)

cache_set = set(cache.keys())
za_set = set(ZA_POKEDEX)

missing = za_set - cache_set
extra = cache_set - za_set - {'__hits__', '__miss__'}

print(f'ZA_POKEDEX total: {len(ZA_POKEDEX)}')
print(f'Unique in ZA_POKEDEX: {len(za_set)}')
print(f'Cache total: {len(cache) - 2}')  # subtract __hits__ and __miss__ if they exist

print(f'\nMissing from cache ({len(missing)}):')
for p in sorted(missing):
    print(f'  - {p}')

print(f'\nExtra in cache (not in ZA): {len(extra)}')
for p in sorted(extra):
    print(f'  - {p}')
