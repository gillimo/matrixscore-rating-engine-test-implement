## Ticket: Official Pokémon Look & Feel for Tk UI

Owner: Codex-Autonomy  
Status: Resolved (2025-12-17)

### Objectives
- Align the Tk UI with a clean “official” Pokémon presentation while keeping the current lazy-loading/lite behavior.
- Ensure all visible elements (bars, cards, modals, buttons) use consistent palette, gradients, and high-contrast text.
- Keep move detail off the main card; details modal shows the full breakdown.

### Requirements
- **Palette**: Use official type colors for cards/badges; dual-types get a true gradient (top->bottom or diagonal) blending the two type colors. Global UI uses Pokédex primaries (red `#EE1515`, blue `#3B4CCA`, yellow `#FFCB05`, dark `#1D1E2C`, light `#FFF7D6`).
- **Cards**: Sprite, name, role tag, type badges, buttons only. Background uses type gradient; text uses auto-contrast. Buttons use primary/secondary styles (red/blue).
- **Metrics bar**: Solid Pokédex-blue strip with white text; shows payload scores exactly; “Tell me more” as a red button.
- **Status bar**: Solid dark strip with white text.
- **Details modal**: Styled container using the palette; shows name, types, role, BST, alignment, weaknesses, coverage priority, SE/neutral help vs exposures, and moves grouped by category with type badges. High-contrast text; headings colored.
- **Breakdown modal**: Styled container; shows scores, exposures, role mix, BST total, stack overlap, penalties, upgrades.
- **“I don’t have this”**: One-shot clear + auto-fill from upgrades, then re-score locally; banner updates without rerunning CLI.

### Tasks
1) Implement type gradients for dual types and apply to card backgrounds; ensure text uses contrast color.
2) Theme buttons globally (primary/secondary) and apply to modals; remove default ttk grays.
3) Style details/breakdown modals with palette backgrounds/borders; add headings/icons where helpful.
4) Ensure metrics bar uses payload scores on initial load; local re-score only on “I don’t have this”.
5) Add type badges in details/move lists; ensure coverage vs exposures section is clear.
6) Optional: add light drop shadow or border to cards for depth (non-intrusive).

### Outcome
- Palette themed with Pokédex primaries; type tints applied with dual-type blends; high-contrast text; buttons/status/metrics bars styled.
- Cards are sprite-first (name/role/type/badges/buttons); move info moved to details modal.
- Details modal: coverage vs exposures, unique coverage, role plan, move blueprint (Phys/Spec tags).
- Breakdown modal: full scores, exposures, role mix, BST total, stack overlap/penalties, upgrades, per-mon metrics.
- CLI handles drops; Tk is view-only with final payload/metrics. No Tk style/ANSI errors.
