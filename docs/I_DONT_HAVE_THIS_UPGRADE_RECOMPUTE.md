## Bug: "I don't have this" uses static upgrade list, doesn't recompute

**Owner:** Codex-Autonomy  
**Status:** Open  

### Problem
The Tk "I don't have this" button clears a slot and auto-fills using the current upgrade list parsed from the payload, consuming used candidates. It does not recompute fresh upgrades based on the new team state; suggestions can become stale or misaligned after multiple replacements.

### Impact
- Replacement may not be the true best option after a drop; subsequent drops may miss better fits.

### Proposed Fix
- Add a local recompute of upgrade candidates after each drop using a lightweight scoring (exposure hits + alignment + BST) or call back into CLI to fetch a fresh upgrade list.

### Acceptance
- After a drop, replacements are chosen from a recomputed list reflecting the current team state; repeated drops remain accurate without rerunning the CLI.

