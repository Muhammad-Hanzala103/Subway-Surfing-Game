# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-02-20
### Refactored
- Extracted main logic into dedicated scenes (GameApp, MenuScene, PlayScene).
- Implemented robust `SaveRepository` with schema versioning and atomic writes.
- Segregated business logic into `ShopService`, `ProgressService` for cleaner architecture.
- Added performance optimizations: text texture caching, FPS-aware particle scaling.
- Added comprehensive action-based input system with rebinding support in UI.
- Added settings toggles for Screen Shake, Particles, FPS counter, and High Contrast mode.

### Fixed
- P0 crashes in shop handling logic when switching states.
- Replaced ambiguous bare `except` blocks with precise error handling.
- Centralized audio initialization to prevent conflict crashes.

## [1.0.0] - Initial Release
- Baseline version with player movement, obstacles, procedurally generated tracks, and coins.
