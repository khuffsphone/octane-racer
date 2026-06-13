# Changelog — Octane Street Racer

## [2.0.0-m2] — Milestone 2: Gameplay Balancing & Playability Tuning
### Added
- 5-gear RPM transmission (caps 40/75/110/145/185 MPH; redline 10000).
- Perfect-shift scoring (9000–9500 RPM → +200 + speed kick); engine bog on
  early upshift; overheat penalty at sustained redline.
- Nitro/Overdrive: +25% top speed, 2.5s active, 8.0s cooldown, double fuel drain.
- Fuel as the core timer (tank 100, gear-scaled drain, gas pickups +35);
  game over on empty tank.
- Near-miss multiplier chain ×1→×5 (12–35px lateral gap, +100×mult).
- 4-state weather machine (sunny→warning→rain→clearing, 90s) with rain
  handling penalty, puddles, and 360° hydroplane spin.
- Progressive difficulty: every 2000 pts traffic +6% / spawn −8%, cap 12000.
- localStorage high-score persistence (try/catch → in-memory fallback).
- Touch overlay shift + nitro buttons; `M` to mute; prefers-reduced-motion support.
- In-canvas HUD: MPH speedometer, RPM/redline bar, nitro gauge, fuel bar, combo.

### Changed
- Player car palette to #ff3300 (vector fallback); PNG sprites retained as primary art.
- Menu/controls copy updated for the new transmission, nitro, and fuel model.

### Removed
- 3-gear transmission and the discrete 3-"lives" (fuel-can) model.
- Boost meter (superseded by Nitro).

### Notes
- Single-file, zero-dependency, 800×600 canvas, Firebase shelled — all preserved.
- Interactive QA matrix (TC-01…22) pending manual/browser verification.

## [1.x] — demo-candidate-v1 lineage
- Restored vertical arcade baseline, asset integration, gameplay tuning,
  transparent PNG sprites, mobile-layout polish, underglow cleanup, QA package.
