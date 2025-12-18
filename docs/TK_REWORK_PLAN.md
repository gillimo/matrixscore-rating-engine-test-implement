## Tk Rework Plan (Sprite-First, Full Breakdown UI)

Goals:
- Page 1 shows sprite-only cards; background tinted by typing color (gradient for dual types), with role label on the card.
- Each card has buttons: “More details” (full info view: typing, stats, moves, coverage/weaknesses, role, alignment) and “I don’t have this Pokémon” (triggers availability rerun flow across the team, not a 1:1 swap).
- Top bar: team rating and a centered “Tell me more” button that opens a team breakdown window (defense/offense/shared scores, deltas/headroom, move-type coverage, exposures fixed, role mix, base stat total).
- UI should allow complete breakdown navigation without CLI logs.

Architecture:
- Split Tk UI into modules: ui/cards.py (main grid + top bar), ui/details.py (per-Pokémon modal), ui/team_breakdown.py (team metrics modal), ui/colors.py (type color + gradient helpers).
- Expose a simple payload schema (team members with typing, role, moves, coverage, stats) emitted from CLI; Tk reads payload.json.
- Ensure only one Tk instance launches; reuse role/type color map in both CLI and Tk.

Move Drafting (formal pass):
- Present drafted moves in the “More details” view: up to 4 picks, categorized (STAB / coverage / utility).
- Show coverage vs team exposures (which exposed types each move hits SE/neutral).
- Avoid move overlap globally (already in CLI); mirror in UI by annotating moves that are already used by teammates.

State Flows:
- Main screen: sprites + role labels; clicking “More details” opens modal with full info; “I don’t have this Pokémon” removes it and triggers the rerun flow using the current team (excluding that slot) from CLI-provided endpoint/hook.
- “Tell me more” opens team breakdown with scores, exposures, role mix, BST total, and suggested upgrade (weakest slot + top 3 replacements if available in payload).

Visuals:
- Type-based gradients for dual types; solid tint for single types. Keep text high-contrast (auto white/black based on luminance).
- Buttons styled per type tint; consistent spacing and a clean grid (2–3 cards per row).

Next Steps:
- Wire payload export to include role, moves, coverage hits, and availability flags.
- Implement ui/colors.py and card grid with per-type gradients.
- Build details modal (full info + drafted moves + coverage vs exposures).
- Build team breakdown modal (scores, deltas/headroom, role mix, upgrade suggestions).
- Add “I don’t have this Pokémon” callback hook to call back into CLI rerun logic (or mark unavailable for next run). 
