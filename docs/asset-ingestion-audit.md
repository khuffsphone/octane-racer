# Octane Racer — Asset Ingestion Audit

Branch: `agent/ag-assets-aesthetics` (from `restore/vertical-arcade-baseline` @ 46815d5)
Source: User-provided Google Drive asset folder
(`https://drive.google.com/open?id=1H_Et-anNSFAPNfpwFVDLrZCk934yY-NP`)
Audited: 2026-06-10, from Drive metadata + filename inspection (50 files, ~40 MB total).
Owner of all files: kylerhuffsphone@gmail.com (user). Generated batch `202606092004`.
License basis for all entries: **user-provided; project use approved by owner.**

## Acquisition status — STOPPED at Phase 2

This audit was performed from a cloud sandbox whose network policy blocks
`drive.google.com`, and whose Drive connector returns file content inline
(impractical beyond ~100 KB). **No binaries were downloaded; nothing is
integrated yet.** Per mission rules, no substitute/fake assets were created.

To proceed locally (real Antigravity worktree):
1. Download the Drive folder into `.local-source-packs/drive-assets-review/`
   (this path is gitignored — never commit it or any raw ZIP).
2. Run the conversion pipeline below for approved candidates only.
3. Copy converted outputs into `assets/<category>/`, update
   `asset-manifest.json`, then integrate per the manifest keys listed below.

## Inventory and decisions

### Vehicle sprite sheets — 19 JPEG, 0.58–1.0 MB each — DEFERRED (strong candidates)
| Group | Count | Proposed use |
|---|---|---|
| Vehicle_sprite_junkyard_muscle (1–4) | 4 | player car candidate |
| Slickback_Coupe_arcade_sprite (1–4) | 4 | traffic variant |
| Neon_Lowrider_vehicle_sprite (1–4) | 4 | traffic variant |
| Police_cruiser_sprite_arcade_game (1–4) | 4 | traffic variant (visual only — no police mechanic exists; do not imply one) |
| Luxury_Rival_Sedan_sprite (1–3) | 3 | traffic variant |

Reason deferred (not rejected): best fit for the game's 32×64 car slots, but
JPEG has no alpha channel and these are scene renders, not sprite-ready cuts.
Required pipeline per selected image: crop the top-down/¾ vehicle → remove
background → export PNG-24 with alpha → downscale to 64×128 (2× the in-game
32×64 slot, `image-rendering:pixelated` handles the rest) → target ≤50 KB.
First-pack limit: select **1 player car + up to 2 traffic variants** (cap: 3
car visuals). Pick the cleanest render per group; defer the other variants.

### UI panel backgrounds — 4 JPEG, 0.62–0.66 MB — DEFERRED (candidates)
`UI_panel_background_arcade_racing` (1–4). Proposed use: splash/menu overlay
backdrop behind the existing 'Press Start 2P' titles. Requirements: recompress
to ≤200 KB (q≈70, max 1280px), verify text contrast (overlay already uses
rgba(0,0,0,.88) — background must not fight it), keep CSS fallback color.
Select at most 1 for the first pack.

### Garage scenes — 4 JPEG, 0.64–0.90 MB — DEFERRED
`Neon_garage_with_custom_cars` (1–4). Menu/branding flavor, not runtime
gameplay art. Possible later use on game-over or high-score screens. Not in
first pack (UI slot budget goes to the panel background).

### Character portraits — 12 JPEG, 0.60–1.0 MB — DEFERRED
Vega_Volt (5), Mama_Midnight (5), Johnny_Law (2). The runtime loop has no
character/driver-select system, and adding one is out of AG scope (new
mechanic). Keep for future menu/character-select feature. Not in first pack.

### Videos — 10 MP4, 2.4–5.3 MB — REJECTED for runtime integration
Neon_city_street_background_video (4), Vega_Volt_beside_electric_racer (2),
Ruby_Rims_in_neon_garage (2), Slickback_Jimmy_in_neon_garage (1),
Johnny_Law_beside_cruiser (1), Mama_Midnight_arcade_racing_preview (1).
Reasons: the game is a canvas arcade loop — background video conflicts with
the pixelated aesthetic, costs mobile battery/perf, and 2–5 MB per file is
poor weight-to-value for a static-host game. Keep as marketing/preview
material outside the repo. Revisit only if a menu attract-loop is explicitly
requested (would need ≤2 MB, muted, `playsinline`, with poster fallback).

## License issues
None identified: all files user-owned, single generated batch, no third-party
or trademarked names. Police cruiser is generic. AI-generated provenance
should be noted in the manifest `source` field on integration.

## Integration plan (for whoever holds the binaries)
Manifest keys the runtime should expect (procedural fallbacks stay mandatory):
- `playerCar` → assets/cars/player-muscle-v1.png
- `trafficCar1..N` → assets/cars/traffic-*.png
- `menuPanelBg` → assets/ui/menu-panel-bg-v1.jpg
Wire-up: extend the existing draw functions with image-if-loaded/fallback
pattern (same approach the old prototype used for `assetState.images`). The
restored baseline currently has no asset loader — port the manifest loader
from the parts-bin branch (`claude/game-polish-punk-16i5wo` has a fixed
`getAssetBase()` returning `./assets/`) rather than rewriting it.

## First-pack budget vs. limits
- car/traffic visuals: 3 allowed → 3 planned (1 player + 2 traffic)
- road/track visual: 1 allowed → 0 planned (no road art in this drop)
- UI/fx visuals: 3 allowed → 1 planned (menu panel bg)
- SFX: 5 allowed → 0 available (no audio files in this drop)
- music loop: optional → none in this drop
