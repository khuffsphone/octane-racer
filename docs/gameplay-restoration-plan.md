# Octane Racer Gameplay Restoration Plan

Version: Phase 1  
Date: 2026-05-29

---

## Goal

Restore the original vertical arcade racer as the main game loop, while preserving Firebase multiplayer as the room/sync shell.

The current prototype's physics (angle-steered oval-track car) and the original arcade physics (vertical-scroll lane-snap racer) are architecturally incompatible. Phase 1 replaces the prototype game loop with the restored arcade loop, while keeping all Firebase plumbing intact.

---

## Non-negotiable gameplay systems to restore first

1. Vertical road gameplay (800×600 canvas, roadX=200, roadW=400)
2. Traffic spawning (spawnEntity, up to 12 entities)
3. Gear shifting A/Z (gearStats[1..3], speed caps, accel per gear)
4. Speed/gear caps and engine stress (wrongGearTimer → crash)
5. Perfect-shift scoring (+500 pts, floating text)
6. Boost meter filled by near misses (not regen-only)
7. Near-miss bonus (+500 score, +25 boostMeter)
8. Fuel/lives system (3 lives, drain every 30s)
9. Gas pickups (drawGasCan, spawn every 60s)
10. Crash/spinout (handleCrash, invulnerable, canvas shake)
11. Arcade HUD (canvas-drawn: score, timer, speed bar, gear, boost, lives, stress)
12. Game over / high score flow (triggerGameOver, saveHighScore, populateHighScores)

---

## Secondary systems to restore next (Phase 2)

1. Weather/rain cycling
2. Puddles/hydroplane
3. Birds/flocks
4. Scenery/parallax
5. Emergency gas logic (lives===1 spawn)
6. Mobile controls polish (touch buttons)

---

## Multiplayer preservation

- Keep Firebase config guard (isConfigured check).
- Keep Anonymous Auth sign-in.
- Keep room create/join flow.
- Keep ready state (toggleReady).
- Keep countdown/start sync (scheduleCountdown, syncCountdownUI).
- **Wire**: after countdown completes → call restored arcade `startGame()` instead of prototype `startLocalRaceOnce()`.
- Publish at throttled 180ms rate (publishRaceState):
  - x, y (player canvas position)
  - speed (pixels/second)
  - distance (cumulative)
  - score (arcade score)
  - lives
  - gear
  - boostMeter
  - isBoosting
  - finished
  - updatedAt
- Opponent display: render as ghost/progress indicator (semi-transparent car at opponent x position on road).
- **Winner logic Phase 1**: when both players have finished or crashed (lives===0), higher final score wins. Equal = tie.
- Keep prototype-limitation disclaimer text visible.
- Keep leaveRoom / opponentStateUnsub cleanup.

---

## Architecture plan

### Layout strategy

Keep the two-column sidebar layout for multiplayer lobby. The sidebar handles auth, room, ready, controls info.

The main stage area contains the 800×600 game canvas (or scaled equivalent).

**Solo mode** (no room joined):
```
Splash overlay → Main menu overlay → startGame() → arcade loop → game over overlay
```

**Multiplayer mode** (room joined, both ready):
```
Lobby sidebar → Ready Up → countdown overlay → startArcadeRace() → arcade loop → publishRaceState throttled → finish → winner overlay
```

### Key function renames / changes

| Prototype | Restored |
|---|---|
| `startLocalRaceOnce()` | Replaced by `startArcadeRace()` which calls `initGame()` + sets `gameState='playing'` |
| `player` (angle/v/progress object) | Replaced by original arcade player object (x, y, speed, gear, lives, score, etc.) |
| `updateGame()` (angle physics) | Replaced by `update(dt)` from original |
| `render()` (oval track) | Replaced by `draw()` from original |
| `publishRaceState()` | Updated to publish arcade fields |
| `publishFinish()` | Updated to use `player.score` not `player.progress*1000` |
| `ghost` object | Updated to include x, y on vertical road |
| `showResultFromRoom()` | Updated for score-based winner |

### Variables to remove from prototype

- `track` (oval rectangle)
- `boostCharge`, `boostActive`, `boostLocked`, `BOOST_DRAIN`, `BOOST_REGEN`, `BOOST_THRESH`, `BOOST_MAXSPD`
- `boostParticles`, `skidMarks`, `drifting`, `driftSfxTimer`
- `emitBoostParticle`, `emitSkid`, `drawSkids`, `drawBoostParticles`, `drawBoostBar`
- `drawTrack()` (oval renderer)
- `getActiveGamepad`, gamepad polling logic (can add back later)

### Variables to add from original

- `gearStats[]`
- `entities[]`, `birds[]`, `pickups[]`, `puddles[]`, `particles[]`, `floatingTexts[]`, `scenery[]`
- `weather` object (deferred — add stub)
- `bgOffsetY`, `cameraSpeed`
- `timeSinceLastSpawn`, `loneCarTimer`
- `highScores[]`
- `basePlayerConfig`
- All draw helpers: `drawCar`, `drawGasCan`, `drawBird`, `drawPuddle`, `drawDeer`
- `spawnEntity`, `spawnScenery`, `createParticles`, `handleCrash`
- `initGame`, `update`, `draw`, `gameLoop`
- `gameState` ('splash' | 'menu' | 'playing' | 'gameover')
- Screen management: `showScreen`, `startFromSplash`, `startGame`, `triggerGameOver`, `saveHighScore`, `populateHighScores`

### HTML changes

Add back from original:
- `#splash-screen` overlay
- `#menu-screen` overlay  
- `#gameover-screen` overlay (with `#new-highscore-box`, `#initials-input`, `#final-score`, `#gameover-buttons`)
- `#highscores-screen` overlay (with `#highscore-list`)
- `#mobile-controls` (deferred polish, but keep element)
- Canvas size: 800×600 (restore original dimensions)

Remove from prototype:
- Inline HUD divs `#hudSpeed`, `#hudBoost`, `#hudProgress`, `#hudState` (HUD is canvas-drawn in original)
- `#countdown` strong text overlay (replace with canvas-drawn or keep div for multiplayer countdown display)
- Prototype game over card (replaced by original gameover-screen overlay)

Keep from prototype:
- Firebase sidebar (auth, lobby, room, ready, drivers, controls, audio, gamepad status)
- `#errorMsg`
- `#soundBtn`
- `#gamepadStatus`

### CSS changes

Merge:
- Prototype CSS variables (`:root` with `--bg`, `--cyan`, etc.) — keep for sidebar
- Original overlay/btn/input styles — add back
- Original `@keyframes bounceIn` for splash
- Original mobile-controls CSS
- Original canvas `image-rendering: pixelated`

### Input changes

Original keys: `{ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Space}` + A/Z for gear shift.

Prototype keys: `key[e.key.toLowerCase()]` (W/S/A/D and arrows).

**Resolution**: Use original keydown/keyup listeners for gameplay keys. Keep prototype key map for lobby UI interactions. A and Z for gear shift must take priority over steer (original uses ArrowLeft/Right for steer, not A/D).

### Canvas sizing

Original: 800×600 fixed internal, CSS-scaled to fit window.
Prototype: 960×720.

**Restore**: Canvas internal size = 800×600. Add `resizeCanvas()` from original. Remove aspect-ratio CSS on canvas.

---

## Multiplayer sync schema (Phase 1)

```js
// publishRaceState — throttled 180ms
{
  x: player.x,
  y: player.y,
  speed: player.speed,
  distance: player.distance,
  score: player.score,
  lives: player.lives,
  gear: player.gear,
  boostMeter: player.boostMeter,
  isBoosting: player.isBoosting,
  finished: player.finished ?? false,
  updatedAt: serverTimestamp()
}
```

```js
// publishFinish
{
  finishedAtMs: Date.now(),
  finalScore: Math.round(player.score),
  distance: player.distance,
  finished: true,
  updatedAt: serverTimestamp()
}
```

### Winner resolution (Phase 1)

```js
// When both players have finished or 0 lives:
// higher finalScore wins; equal = 'tie'
const winnerId = sorted[0].finalScore === sorted[1].finalScore
  ? 'tie'
  : sorted[0].finalScore > sorted[1].finalScore
    ? sorted[0].id : sorted[1].id;
```

### Opponent ghost rendering

Draw opponent as a semi-transparent car at `ghost.x, ghost.y` on the vertical road canvas. Update ghost fields from Firestore onSnapshot. Ghost fields: x, y, speed, gear (for visual). No shared traffic/hazards in Phase 1.

---

## Asset policy

Asset ingestion remains **paused** until restored gameplay is visually approved by the user after Phase 1.

Canvas fallback primitives are used for all visuals (as in original baseline).

---

## Verification plan

### Automated grep check
```powershell
Select-String -Path "index.html" -Pattern "gearStats","highScores","spawnEntity","handleCrash","PERFECT SHIFT","NEAR MISS","drawGasCan","boostMeter","wrongGearTimer","saveHighScore","populateHighScores","splash-screen","gameover-screen","highscores-screen"
```

### Local server test
```
python -m http.server 8081
# Open http://localhost:8081/index.html
```

### Smoke test — Solo mode
- [ ] Splash screen loads and animates
- [ ] Click/keypress advances to main menu
- [ ] "Start Engine" launches vertical road
- [ ] Traffic appears and scrolls
- [ ] Arrow keys steer left/right
- [ ] Up/Down accelerate/brake
- [ ] A shifts gear up, Z shifts gear down
- [ ] Gear indicator updates in HUD
- [ ] Perfect shift floating text appears
- [ ] Near miss triggers score + boost fill
- [ ] Space bar triggers boost when meter full
- [ ] Lives (fuel cans) display in HUD
- [ ] Crash reduces lives, spinout visual
- [ ] Game over screen appears at 0 lives
- [ ] Score displayed on game over
- [ ] High score entry if qualifying score
- [ ] High scores table renders

### Smoke test — Multiplayer placeholder
- [ ] Firebase placeholders detected gracefully
- [ ] Solo mode works without Firebase
- [ ] Lobby sidebar does not crash
- [ ] No credentials committed

---

_Last updated: Phase 1 pre-implementation_
