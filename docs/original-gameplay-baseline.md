# Original Octane Racer Gameplay Baseline

The original Octane Street Racer gameplay must be preserved and restored before additional asset ingestion.

## Required Restoration Checklist

- [x] Splash screen
- [x] Main menu
- [x] Start Engine flow
- [x] High Scores screen
- [x] Game Over screen
- [x] Manual gear shifting with A/Z
- [x] Perfect-shift scoring
- [x] Speed/gear system
- [x] Boost meter/system (near-miss filled)
- [x] Near-miss bonus
- [x] Traffic spawning
- [x] Traffic lane-switching AI
- [x] Fuel/lives system
- [x] Gas pickups
- [x] Emergency gas logic
- [ ] Rain/weather (deferred Phase 2)
- [ ] Puddles/hydroplane hazard (deferred Phase 2)
- [ ] Birds/scenery/parallax (deferred Phase 2)
- [x] Crash/spinout states
- [x] Floating text
- [x] Arcade HUD
- [ ] Mobile controls (element present, touch bindings wired; visual polish deferred)
- [x] High-score save flow

## Multiplayer Rule

Multiplayer should wrap around this arcade loop.

Do not make the simplified circular-track prototype the permanent core game.

---

## Gameplay Restoration Phase 1

**Date:** 2026-05-29  
**Status:** Core vertical arcade loop restored

### Restored

- Splash screen (bounce-in animation, click/keypress advance)
- Main menu (Start Engine, High Scores, controls guide)
- Start Engine flow (solo button + menu → initGame() → vertical arcade loop)
- Vertical road (800×600, ROAD_X=200, ROAD_W=400, scrolling lane markings, rumble strips)
- Traffic spawning (spawnEntity, up to 12, wave density, collision AABB)
- Lane-switching traffic AI (switchTimer, smooth lerp, turn-signal blink, tire smoke particles)
- Manual gear shifting A/Z with gearStats[1..3] (speed caps 250/450/700, accel per gear)
- Engine stress system (wrongGearTimer, 2s limit, spinout penalty)
- Perfect-shift scoring (+500, within ±50 of threshold, floating text, sfx)
- Near-miss bonus (+500 score, +25 boostMeter, cyan particles, floating text, sfx)
- Boost meter system (filled by near misses; Space to activate at 100%; 3s at 900 speed; boost blast clears traffic for 1000pts)
- Fuel/lives system (3 lives, drain every 30s, lives = fuel cans in HUD)
- Gas pickups (drawGasCan bounce animation, +1 life, +1000 score, spawn every 60s)
- Emergency gas logic (auto-spawn when lives===1, 15s cooldown, different lane)
- Crash/spinout (handleCrash, invulnerable 2s, 720° spinAngle, canvas shake, particles)
- Floating text feedback (floats upward, flicker, configurable color)
- Arcade HUD (canvas-drawn: score, timer, speed bar with gear notches, boost meter, gear indicator, fuel can lives, engine stress bar)
- Game over screen (CRASHED OUT, final score display, new high score entry)
- High scores screen (top 5, initials entry, rank table, default scores)
- Firebase auth guard preserved (isConfigured placeholder check)
- Room create/join preserved
- Ready state preserved
- Countdown/start sync preserved; wired to restored arcade startArcadeGame()
- Opponent ghost sync preserved; updated to arcade fields (x, y, speed, gear)
- publishRaceState updated to publish arcade fields (x, y, speed, distance, score, lives, gear, boostMeter, isBoosting, finished)
- publishFinish updated to use player.score as finalScore
- Winner logic updated: higher final score wins (not timestamp-based)
- leaveRoom cleanup preserved

### Deferred to Phase 2

- Weather/rain cycling and rain drops
- Puddles and hydroplane crash
- Birds/flocks
- Scenery/parallax trees
- Mobile controls visual polish
- Gamepad re-integration (removed during arcade restore; to add back in Phase 2)

### Asset ingestion

Still paused until restored gameplay is visually approved by user.
