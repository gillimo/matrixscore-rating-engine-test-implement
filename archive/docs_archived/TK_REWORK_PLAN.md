## Tk Rework Plan (Sprite-First, Full Breakdown UI)

Goals:
- Page 1 shows sprite-only cards; background tinted by typing color (gradient for dual types), with role label on the card.
- Each card has buttons: â€œMore detailsâ€ (full info view: typing, stats, moves, coverage/weaknesses, role, alignment) and â€œI donâ€™t have this PokÃ©monâ€ (triggers availability rerun flow across the team, not a 1:1 swap).
- Top bar: team rating and a centered â€œTell me moreâ€ button that opens a team breakdown window (defense/offense/shared scores, deltas/headroom, move-type coverage, exposures fixed, role mix, base stat total).
- UI should allow complete breakdown navigation without CLI logs.

Architecture:
- Split Tk UI into modules: ui/cards.py (main grid + top bar), ui/details.py (per-PokÃ©mon modal), ui/team_breakdown.py (team metrics modal), ui/colors.py (type color + gradient helpers).
- Expose a simple payload schema (team members with typing, role, moves, coverage, stats) emitted from CLI; Tk reads payload.json.
- Ensure only one Tk instance launches; reuse role/type color map in both CLI and Tk.

Move Drafting (formal pass):
- Present drafted moves in the â€œMore detailsâ€ view: up to 4 picks, categorized (STAB / coverage / utility).
- Show coverage vs team exposures (which exposed types each move hits SE/neutral).
- Avoid move overlap globally (already in CLI); mirror in UI by annotating moves that are already used by teammates.

State Flows:
- Main screen: sprites + role labels; clicking â€œMore detailsâ€ opens modal with full info; â€œI donâ€™t have this PokÃ©monâ€ removes it and triggers the rerun flow using the current team (excluding that slot) from CLI-provided endpoint/hook.
- â€œTell me moreâ€ opens team breakdown with scores, exposures, role mix, BST total, and suggested upgrade (weakest slot + top 3 replacements if available in payload).

Visuals:
- Type-based gradients for dual types; solid tint for single types. Keep text high-contrast (auto white/black based on luminance).
- Buttons styled per type tint; consistent spacing and a clean grid (2â€“3 cards per row).

Next Steps:
- Wire payload export to include role, moves, coverage hits, and availability flags.
- Implement ui/colors.py and card grid with per-type gradients.
- Build details modal (full info + drafted moves + coverage vs exposures).
- Build team breakdown modal (scores, deltas/headroom, role mix, upgrade suggestions).
- Add â€œI donâ€™t have this PokÃ©monâ€ callback hook to call back into CLI rerun logic (or mark unavailable for next run). 


