# Octane Racer — Asset Ingestion Audit

## Source and Initial Discovery (Claude's Drive Audit)
- **Source**: User-provided Google Drive folder
- **Folder Status**: Enumerated directly from Drive metadata. 
- **Observations**: Many assets were scene renders rather than sprite-ready cutouts. 19 vehicle sprite sheets were identified as strong candidates. Videos were evaluated and rejected for runtime use due to size.
- **Conversion Needs**: Assets should be converted, cropped, and downscaled to pixel-perfect sizes before integration where needed.

## Actual Integration Findings (AG's Pass)
- **Total files reviewed**: 92 assets evaluated locally.
- **Integration**: 5 approved assets have been safely integrated into tracked directories.
- **Components Wired**: 1 player car, 2 traffic variants, and 2 UI/background elements (splash and menu garage).
- **Architecture**: `asset-manifest.json` updated. Procedural fallbacks fully implemented if image loading fails.
- **Git Hygiene**: Raw `.local-source-packs` and `.zip` files were strictly excluded from commits.

---

## Asset Status Sections

### Approved and Integrated
| File | Type | Decision | Path |
|------|------|----------|------|
| `Slickback_Coupe_arcade_sprite_v1` | Car sprite (player) | ✅ Integrated | `assets/cars/player-slickback-coupe.jpeg` |
| `Police_cruiser_sprite_v1` | Car sprite (traffic) | ✅ Integrated | `assets/cars/traffic-police-cruiser.jpeg` |
| `Vehicle_sprite_junkyard_muscle_v1` | Car sprite (traffic) | ✅ Integrated | `assets/cars/traffic-junkyard-muscle.jpeg` |
| `Arcade_racing_game_title_splash_v1` | UI background | ✅ Integrated | `assets/ui/title-splash-bg.jpeg` |
| `Neon_garage_with_custom_cars_v1` | UI background | ✅ Integrated | `assets/ui/menu-garage-bg.jpeg` |

### Approved but Not Integrated
| File | Type | Decision | Path |
|------|------|----------|------|
| `HUD_frame_for_racing_game_v1` | UI overlay | ✅ Approved | `assets/ui/hud-frame.jpeg` |

### Deferred
- **Vehicle Variants**: `Slickback_Coupe` (v2-v4), `Police_cruiser` (v2-v4), `Junkyard_muscle` (v2-v4), `Neon_Lowrider` (v1-v4), `Armored_Hauler` (v1-v4), `Luxury_Rival_Sedan` (v1-v3).
- **Character Portraits**: 12 files deferred. Require a dedicated character select UI which is currently out of scope.
- **UI/Background Variants**: Additional title splashes, HUD frames, and garage scenes.

### Rejected
- **Videos**: 16 MP4 video files (e.g., `Neon_city_street_background_video`). Rejected for runtime use due to heavy file sizes and conflict with the canvas pixelated aesthetic.
- **Generic Sprites**: `Create_a_top-down_orthographic_vehicle` (rejected for lacking project identity).

### Required Conversion Work
Deferred scene renders (e.g., vehicle sprites) will require cropping top-down/¾ views, removing backgrounds, exporting as PNG-24 with alpha, and downscaling to fit 64x128 slots (`image-rendering:pixelated` handles the rest in-game) while targeting ≤50 KB per asset.

### Licensing and Source Notes
- **Source**: User-provided Google Drive folder.
- **License**: User-provided; project use approved by owner.
- **Attribution**: AI-generated for Octane Racer project.
- **Clearance**: No third-party content or trademarked names detected. Police cruiser is generic.

### File-size Notes
- Integrated JPEGs are 580–940 KB.
- Rejected MP4s range from 2.4–7.7 MB, which exceeds the weight-to-value budget for a static HTML canvas game.

---

This audit is the combined source of truth for the first asset pass.
