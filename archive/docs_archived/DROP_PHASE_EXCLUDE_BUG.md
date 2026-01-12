## Bug: Drop/replace phase does not exclude dropped PokÃ©mon

**Owner:** Codex-Autonomy  
**Status:** Resolved (2025-12-17)  

### Problem
In the CLI drop/replace loop, we drop a selected mon and rerun `autofill_team`, but we cannot currently exclude the dropped mon because `autofill_team` does not accept an exclude list. The dropped PokÃ©mon can be re-added immediately, which defeats the purpose of the drop.

### Resolution
- `autofill_team` and candidate pools honor an exclude set; drop loop keeps a running exclude so dropped mons are not re-added during refill.


