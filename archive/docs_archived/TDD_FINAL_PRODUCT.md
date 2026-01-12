## TDD Notes (DLC)

Preferred practice when adding code:
- Write/adjust small harness cases in `test_harness.py` (e.g., `--commands "gengar\nfinalize"`).
- Validate logs are produced (non-empty, footer present) and scoring fields render.
- Add focused unit-style helpers if needed (local, not committed if temporary).

Current gaps: no formal test suite; rely on harness runs and log inspection until scoring/logging stabilizes.

Signed: Codex (2025-12-17)


