## Bug: Manual offense suggestions ignore alignment/exposed types

**Owner:** Codex-Autonomy  
**Status:** Open  

### Problem
In manual flow, offense suggestions default to high-offense baseline picks (e.g., Kangaskhan) regardless of team exposures or alignment. The manual picker does not apply the alignment/exposure weighting used in autofill/offense sim, so the user sees irrelevant top suggestions.

### Impact
- Misleads manual users toward generic picks instead of coverage-aligned options.
- Breaks expected behavior: manual flow should surface coverage/role-aligned candidates, not just the highest raw offense glue.

### Proposed Fix
- Apply the same alignment/exposure-weighted scoring used in offense sim to manual offense suggestions.
- Filter/sort manual suggestions by: (1) SE hits vs current exposures, (2) alignment_score, (3) BST/role fit, before raw offense.

### Acceptance
- Manual offense suggestions reflect exposed types/coverage needs and role alignment; Kangaskhan no longer appears by default when misaligned.

