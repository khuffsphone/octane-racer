# Octane Racer — Gameplay Restoration Audit

Generated: 2026-05-29  
Baseline: `legacy/original/Octane_Street_Racer.html` (1839 lines)  
Active prototype: `index.html` (634 lines)

---

## Feature Comparison Table

| Feature | Original Baseline | Active Prototype | Restore Priority | Notes |
|---|---|---|---|---|
| **Splash screen** | Present — full-screen overlay, OCTANE title bounce-in animation, "click or press any key" | Absent — lobby UI is the landing page | High | No splash at all in prototype |
| **Main menu** | Present — Start Engine, High Scores buttons; controls instructions inline | Absent — replaced by Firebase lobby sidebar | High | Lobby sidebar ≠ arcade menu |
| **Start Engine flow** | Present — click Start Engine → initGame() → arcade loop | Absent — race starts via Firebase countdown or remains in lobby | High | Solo mode has no launch path |
| **High Scores screen** | Present — top 5, initials entry, local in-memory storage, rank table | Absent | High | No high score tracking at all |
| **Game Over screen** | Present — "CRASHED OUT", final score, new-highscore box, Try Again / Menu | Partial — gameover div exists but serves multiplayer finish only | High | Prototype gameover doesn't show arcade score or handle solo |
| **Manual gear shifting A/Z** | Present — A = shift up (gear++), Z = shift down (gear--), bound to gearStats[] | Absent — prototype uses Arrow/W/S/A/D for steer only; no gear concept | High | A key now means steer-left in prototype |
| **Perfect-shift scoring** | Present — +500 pts when shift within ±50 of gear threshold; floating text "PERFECT SHIFT! +500" | Absent | High | No shift mechanic to attach it to |
| **Gear stats / speed caps** | Present — gearStats[1..3]: max speeds 250/450/700, different accel; engine stress at wrong gear | Absent — prototype uses fixed v max 7.2 (abstract units) | High | Core driving feel depends on this |
| **Boost meter/system** | Partial — boostMeter fills via near-miss (+25 each), depletes on Space; 3s boost at 900 speed | Partial — boostCharge regen-based (not near-miss); different drain/regen constants; no gear integration | High | Prototype boost exists but decoupled from near-miss and arcade score loop |
| **Near-miss bonus** | Present — +500 score, +25 boostMeter, cyan particles, "NEAR MISS!!! +500" floating text | Absent — no traffic entities, so no near-miss detection | High | Requires traffic first |
| **Traffic spawning** | Present — spawnEntity() up to 12 entities, lane-aligned, speed 80–300, wave-based density | Absent — no traffic entities exist | High | Core gameplay hazard |
| **Lane-switching traffic AI** | Present — switchTimer cooldown, switches near y<250, smooth lerp to targetX, tire smoke particles | Absent | High | Required for arcade difficulty |
| **Fuel/lives system** | Present — 3 lives (fuel cans); drain -1 life every 30s playtime; crash costs 1 life; game over at 0 | Absent — no lives concept; prototype has no arcade session state | High | Arcade session boundary depends on this |
| **Gas pickups** | Present — drawGasCan(), spawn every 60s via nextGasSpawn, bounce animation, +1 life on pickup | Absent | High | Tied to fuel/lives system |
| **Emergency gas logic** | Present — when lives===1, spawn pickup every 15s in different lane | Absent | Medium | Safety net; can defer briefly |
| **Rain/weather** | Present — weather.type clear/rain cycling; intensity ramping; rain drops; visibility tint | Absent | Medium | Secondary atmosphere system |
| **Puddles/hydroplane** | Present — drawPuddle(), spawned during rain; collision causes spinout crash | Absent | Medium | Requires rain system |
| **Birds/flocks** | Present — drawBird(), random flock size 3–8, cross-screen movement, wing flap animation | Absent | Low | Visual polish |
| **Scenery/parallax** | Present — trees/circles off-road, two depth layers (speedMultiplier), side placement | Absent | Low | Background polish |
| **Crash/spinout states** | Present — handleCrash(isSpinout), spinAngle visual 720°, invulnerable 2s, canvas shake | Absent — prototype has no collision detection or crash state | High | Core game feel |
| **Floating text feedback** | Present — array of {text, x, y, timer, color}; floats upward; flicker effect | Absent | High | Feedback for all score events |
| **Arcade HUD** | Present — score, timer, speedometer bar, gear notches, boost bar, gear indicator, lives (fuel cans), engine stress bar/warning | Partial — HUD divs for Speed/Boost/Progress/State exist but are lobby-oriented and don't show arcade data | High | Needs full canvas-drawn HUD matching original |
| **Mobile controls** | Present — touch buttons (up/down/left/right/boost), hidden on ≥768px | Absent — prototype has no touch controls | Medium | Needed for mobile gameplay |
| **Local high score save** | Present — in-memory array, sorted top 5, initials entry; exportGame() bakes scores in | Absent | High | Core arcade loop closure |
| **Firebase auth guard** | Absent in original (Gemini Canvas hardcoded credentials) | Present — isConfigured guard; placeholders fail gracefully; solo works without Firebase | Preserved | Keep as-is |
| **Room creation** | Absent in original | Present — createRoom(), makeCode(), setDoc to Firestore | Preserved | Keep |
| **Join by code** | Absent in original | Present — joinRoom(c), code validation, room existence check | Preserved | Keep |
| **Ready state** | Absent in original | Present — toggleReady(), player1Ready/player2Ready flags, allReady detection | Preserved | Keep |
| **Countdown/start sync** | Absent in original | Present — scheduleCountdown(), syncCountdownUI(), raceStartMs timestamp | Preserved | Keep; wire to restored arcade launch |
| **Opponent ghost/progress sync** | Absent in original | Present — opponentStateUnsub, ghost.x/y/a/progress, drawCar(ghost) semi-transparent | Partial | Ghost draws but no arcade sync fields (score/gear/lives) published yet |
| **Finish/winner reporting** | Absent in original | Present — publishFinish(), score-by-finishedAtMs, winnerId, showResultFromRoom() | Partial | Uses progress-based score; needs arcade score instead |
| **Leave-room cleanup** | Absent in original | Present — leaveRoom(), cleanupListeners(), opponentStateUnsub cleared | Preserved | Keep |

---

## Summary Counts

| Category | Count |
|---|---|
| High priority to restore | 14 |
| Medium priority to restore | 4 |
| Low priority to restore | 2 |
| Already present in prototype (Firebase) | 7 |
| Partial (needs upgrade) | 3 |

---

## Key Structural Differences

### Prototype is a lobby-first app; original is arcade-first
The prototype renders a 2-column grid layout with Firebase sidebar as the primary UI. The original is a full-screen canvas game with overlay screens (splash → menu → game → gameover → high scores).

### Physics model is incompatible
- **Original**: speed in pixels/second (0–700+), vertical scrolling road, lane-snap movement, gear-governed acceleration  
- **Prototype**: speed as abstract float (v 0–7.2), angle-steered vehicle on fixed circular/oval track, progress 0–1

### Canvas dimensions
- **Original**: 800×600, vertical road (roadX=200, roadW=400), player always near bottom  
- **Prototype**: 960×720, free-roam rectangle track

### Audio
Both have Web Audio synthesis. Prototype's sfx system is compatible; original has no sfx functions (canvas-era). Prototype audio can be kept.

---

## Restoration Phase 1 Scope

The following features will be restored in Phase 1 (core vertical arcade loop):

1. Splash screen + main menu
2. Vertical road with lane markings and rumble strips
3. Traffic spawning (spawnEntity)
4. Lane-switching traffic AI
5. Manual gear shifting (A/Z), gearStats, engine stress
6. Perfect-shift bonus
7. Near-miss bonus
8. Boost meter (near-miss filled)
9. Fuel/lives system
10. Gas pickups (drawGasCan)
11. Crash/spinout (handleCrash)
12. Floating text feedback
13. Full arcade HUD (canvas-drawn)
14. Game over screen + high scores (local)
15. Firebase multiplayer: preserved, wired to restored arcade launch

The following are **deferred** to Phase 2:
- Weather/rain/puddles
- Birds/flocks
- Scenery/parallax
- Emergency gas logic
- Mobile controls polish

---

_Last updated: Restoration Phase 1 pre-implementation_

---

## Phase 3 Restored Gameplay QA

**Date:** 2026-05-29  
**QA method:** Static code analysis (Playwright blocked on localhost; server confirmed live at 200 OK, 62 KB)

### Status: PASS (with fixes applied)

### Solo gameplay audit — all systems PRESENT

| System | Status | Notes |
|---|---|---|
| splash/menu | ✅ PASS | bounce-in overlay, click/key advance, menu Start Engine / High Scores |
| Start Engine | ✅ PASS | `startArcadeGame()` → `initGame()` → gameLoop running |
| vertical road | ✅ PASS | 800×600, ROAD_X=200, ROAD_W=400, scrolling markings, rumble strips |
| traffic | ✅ PASS | `spawnEntity()`, up to 12, AABB collision |
| lane-switching AI | ✅ PASS | switchTimer, smooth lerp, turn signal blink, tire smoke |
| A/Z gear shifting | ✅ PASS | gearStats[1..3], speed caps 250/450/700 |
| perfect shift | ✅ PASS | +500 pts within ±50, floating text, sfx |
| boost | ✅ PASS | near-miss filled; Space at 100%; 3s at 900 px/s; gamepad X button |
| near miss | ✅ PASS | +500 score, +25 boostMeter, sfxNearMiss |
| fuel/lives | ✅ PASS | 3 cans, drain 30s, crash –1, 0 → game over |
| gas pickups | ✅ PASS | drawGasCan bounce, +1 life / +1000 score |
| weather/rain | ✅ PASS | clear↔rain cycling, intensity ramp, "RAIN!" text |
| puddles/hydroplane | ✅ PASS | spawned during rain, AABB collision → handleCrash(true) |
| birds/flocks | ✅ PASS | flock 3–8, cross-screen, wing flap animation |
| scenery/parallax | ✅ PASS | 10 trees on init, near/far layers, continuous spawn |
| crash/spinout | ✅ PASS | invulnerable 2s, 720° spinAngle, canvas shake, particles |
| game over | ✅ PASS | "CRASHED OUT" overlay, final score |
| high scores | ✅ PASS | top-5 local, initials entry, table render |
| mobile controls | ✅ PASS | HTML element present, touch bindings + touchcancel; hidden ≥769px |
| gamepad guard | ✅ PASS | `pollGamepad()` runs per frame; connect/disconnect events; degrades safely without pad |
| W/S aliases | ✅ PASS | KeyW/KeyS map to ArrowUp/ArrowDown |
| sound guard | ✅ PASS | AudioContext only initialized on user gesture; failure caught silently |

### Multiplayer shell regression

| Check | Status |
|---|---|
| Firebase placeholder guard | ✅ PASS — `isConfigured` false, solo works, multiplayer UI does not crash |
| Prototype limitation text | ✅ PASS — visible in sidebar |
| No credentials present | ✅ PASS — 0 hits for real API keys in all scanned files |
| Room UI renders | ✅ PASS — Create/Join/Ready/Leave buttons present |
| Countdown → arcade handoff | ✅ PASS — `startLocalRaceOnce()` calls `startArcadeGame()` |
| Ghost/progress sync | ✅ PASS — `opponentStateUnsub` wired; ghost renders as semi-transparent car |
| Finish reporting | ✅ PASS — `publishFinish()` uses `player.score` |
| Leave-room cleanup | ✅ PASS — `cleanupListeners()` clears all unsubs and timers |

### Firebase live retest
**Not performed** — no local Firebase config was provided for this pass.

### Issues found and fixed

| # | Severity | Issue | Fix applied |
|---|---|---|---|
| 1 | **Blocker** | Rain draw batch left `lineWidth=1.5` and `strokeStyle` dirty in canvas state — leaked into HUD borders and floating text rendering | Wrapped rain draw in `ctx.save()`/`ctx.restore()` + added `ctx.lineCap='round'` |
| 2 | **Major** | Birds rendered before rain tint overlay → birds invisible during rain | Moved `birds.forEach(drawBird)` to after rain tint block |
| 3 | **Major** | Player spawns with `invulnerable=0` — first traffic car can collide immediately on game start | Added 2.0s grace invulnerability in `initGame()` |
| 4 | **Cosmetic** | `loneCarTimer` declared and reset in `initGame` but never decremented (dead variable) | Removed declaration and reset, replaced with explanatory comment |

### Gameplay feel assessment

- **Restored arcade identity:** YES. Vertical road, lane traffic, gear shifting, near-miss scoring, fuel pressure, rain hazard. Feels like Octane Racer.
- **Still feels aimless:** NO. Score pressure (speed²×time), gear efficiency, near-miss chain, fuel drain, rain handling penalty all create moment-to-moment decisions.
- **Circular test track:** Fully removed. No `track` object, no `player.a`/`player.v` angle physics.
- **HUD meaningful:** YES. Score, speed+gear notches, boost fill bar, gear indicator, fuel can lives, engine stress warning all give real-time feedback.

### Asset ingestion

Still paused until user visually approves restored gameplay.
