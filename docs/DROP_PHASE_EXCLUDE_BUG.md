## Bug: Drop/replace phase does not exclude dropped Pokémon

**Owner:** Codex-Autonomy  
**Status:** Open  

### Problem
In the CLI drop/replace loop, we drop a selected mon and rerun `autofill_team`, but we cannot currently exclude the dropped mon because `autofill_team` does not accept an exclude list. The dropped Pokémon can be re-added immediately, which defeats the purpose of the drop.

### Proposed Fix
- Add an `exclude` parameter to `autofill_team` (and downstream selection) to prevent re-adding recently dropped names during the drop phase.

### Acceptance
- When a mon is dropped in the numbered drop loop, it is not re-added in the same pass; replacements respect the exclusion.
