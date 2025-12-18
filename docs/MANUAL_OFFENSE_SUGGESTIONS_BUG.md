## Bug: Manual offense suggestions ignore alignment/exposed types

**Owner:** Codex-Autonomy  
**Status:** Resolved (2025-12-17)  

### Problem
In manual flow, offense suggestions default to high-offense baseline picks (e.g., Kangaskhan) regardless of team exposures or alignment. The manual picker does not apply the alignment/exposure weighting used in autofill/offense sim, so the user sees irrelevant top suggestions.

### Impact
- Misleads manual users toward generic picks instead of coverage-aligned options.
- Breaks expected behavior: manual flow should surface coverage/role-aligned candidates, not just the highest raw offense glue.

### Resolution
- Offense ranking now weights SE/neutral hits to current exposures and alignment score; niche coverage picks surface (staryu fix).
- Generic high-offense glue no longer dominates manual suggestions when misaligned.
