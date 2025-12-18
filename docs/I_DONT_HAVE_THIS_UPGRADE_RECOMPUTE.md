## Bug: "I don't have this" uses static upgrade list, doesn't recompute

**Owner:** Codex-Autonomy  
**Status:** Resolved (2025-12-17)  

### Problem
The Tk "I don't have this" button clears a slot and auto-fills using the current upgrade list parsed from the payload, consuming used candidates. It does not recompute fresh upgrades based on the new team state; suggestions can become stale or misaligned after multiple replacements.

### Impact
- Replacement may not be the true best option after a drop; subsequent drops may miss better fits.

### Resolution
- Drop/replace handled in CLI with exclude-aware autofill; upgrades recomputed and exclude set maintained so dropped mons are not re-added.
- Tk UI no longer runs replacements; view-only with final team/payload.
