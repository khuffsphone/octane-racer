# Codex Handoff — Octane Street Racer

## Assignment

Build out and polish the Octane Street Racer multiplayer prototype.

The user has a single-file HTML canvas racing game that was enhanced with Firebase multiplayer room support. The next step is to make it cleaner, more maintainable, and more visually polished while preserving multiplayer behavior.

## Non-negotiable constraints

1. Do not remove Firebase anonymous auth.
2. Do not remove Firestore room creation.
3. Do not remove join-by-code behavior.
4. Do not remove ready-state synchronization.
5. Do not remove synchronized countdown/start.
6. Do not remove opponent ghost sync.
7. Do not claim Firebase provides cheat-proof real-time racing.
8. Keep the project deployable as a static web app unless the user explicitly authorizes a server.
9. Do not introduce React, Next.js, Phaser, Vite, or another framework unless you first preserve the current single-file baseline.
10. Improve visuals after functionality is stable.

## Local Playability Checklist (Playability Pass — completed)

- [ ] Space boost works.
- [ ] Shift drift works.
- [ ] R reset works.
- [ ] Sound toggle works and does not crash.
- [ ] Gamepad status line appears.
- [ ] Gamepad input is optional and does not break keyboard input.
- [ ] Boost visual effect appears (cyan particle trail, glow on car, boost bar on canvas).
- [ ] Drift smoke/skid effect appears (white particles on canvas while drifting).
- [ ] Firebase placeholders still fail gracefully.
- [ ] Canvas still renders offline.

## Multiplayer Smoke-Test Checklist (requires real Firebase config)

- [ ] Solo mode loads without Firebase config.
- [ ] Firebase placeholders fail gracefully.
- [ ] Player A creates room.
- [ ] Player B joins room.
- [ ] Both players appear in lobby.
- [ ] Both players can toggle ready.
- [ ] Countdown starts only when both are ready.
- [ ] Race starts once for each client.
- [ ] Opponent ghost appears or degrades safely.
- [ ] Game over writes final score.
- [ ] Winner / loser / tie result displays correctly.

## Recommended implementation plan

### Phase 1 — Baseline import ✅

- Add the finalized HTML prototype as `index.html`.
- Confirm it opens locally in a browser.
- Confirm it still shows the splash screen, menu, and race loop without Firebase configured.
- Firebase should fail gracefully when config placeholders are still present.

### Phase 2 — Local playability pass ✅

- Implement Space boost with particle trail, boost bar, and glow.
- Implement Shift drift with skid mark particles and traction change.
- Implement R reset (edge-triggered, zeroes speed, returns to start position).
- Implement Web Audio sound toggle (click, ready, countdown, boost, drift, finish, win, lose).
- Implement Gamepad API (optional, LStick steer, RT/A accel, LT/B brake, X/□ boost, LB drift).
- Implement proper timer safety: clearCountdownTimer, clearRaceTimers, syncCountdownUI, cleanupListeners.
- Update controls help text.
- Preserve all Firebase multiplayer code unchanged.

### Phase 3 — Two-browser Firebase smoke test

After real Firebase config is added:

- Browser A creates room.
- Browser B joins by code.
- Both players appear in lobby.
- Both players can toggle ready.
- Countdown starts only when both are ready.
- Race starts once for each client.
- Opponent ghost appears or degrades safely.
- Game over writes final score.

### Phase 4 — Rematch / leave-room polish

- Ensure leave-room fully cleans up state.
- Implement rematch flow if desired.
- Improve result screen.

### Phase 5 — Asset ingestion scaffold

- Only after Phase 3 passes.
- Add placeholder asset manifest.
- Add first small asset pack.

## Timer safety rules

- `syncCountdownUI()` — updates countdown display only. Does NOT call `clearRaceTimers()`.
- `clearCountdownTimer()` — clears only `countdownIntervalId` (the display interval).
- `clearRaceTimers()` — clears both `countdownIntervalId` and `raceStartTimeout`.
- `cleanupListeners()` — clears roomUnsub, playersUnsub, opponentStateUnsub, and calls clearRaceTimers().
- `opponentStateUnsub` — cleared before replacement and on leave.
- `publishRaceState()` — throttled to 180ms gate, not every animation frame.

## Audio system

- Web Audio API only. No external sound files.
- Must initialize after a user gesture (soundBtn click).
- Sounds: sfxClick, sfxReady, sfxCountdown, sfxCountdownGo, sfxBoost, sfxDrift, sfxFinish, sfxWin, sfxLose.
- If AudioContext fails, game remains fully playable.

## Boost system

- boostCharge: 0.0 to 1.0. Drains at 0.022/frame while active. Regens at 0.004/frame.
- boostLocked: true when depleted. Re-enables when charge reaches BOOST_THRESH (0.25).
- BOOST_MAXSPD: 11.0 (normal max: 7.2).
- Visual: cyan particle trail, car glow, boost bar at canvas bottom.
- HUD: ⚡ percentage indicator with color (cyan → yellow → red as charge drops).

## Drift system

- Activated by Shift (or gamepad LB).
- Requires |player.v| > 0.5 to activate (must be moving).
- While drifting: friction reduced to 0.93 (normal: 0.98), turn rate multiplied by 1.75.
- Visual: white smoke particle skid marks emitted from car rear.
- Sound: throttled noise burst (sfxDrift every 20 frames).

## Gamepad mappings

- Axis 0 (left stick horizontal): steer
- Button 7 (RT) or Button 0 (A): accelerate
- Button 6 (LT) or Button 1 (B): brake
- Button 2 (X) or Button 3 (Y): boost
- Button 4 (LB): drift

## Firebase data model

```text
rooms/{roomCode}
  roomCode
  status: lobby | countdown | racing | finished
  player1Id
  player2Id
  player1Ready
  player2Ready
  createdAt
  countdownStartMs
  raceStartMs
  winnerId

rooms/{roomCode}/players/{playerId}
  id
  name
  ready
  x, y, a, progress
  finishedAtMs
  finalScore
  updatedAt
```

## Networking rule

Do not write every animation frame to Firestore. Race-state writes are throttled to approximately 5–6 times per second (180ms gate).

## Firebase Live Testing

- **Performed:** May 27, 2026.
- **Result:** PASS. Two-browser sync, lobby ready logic, countdown, race-state publication, and finish results work as intended with real Firestore backend using Anonymous Auth.
- **Notes:** Config injected locally for testing, placeholders restored afterward. No credentials committed. Live testing done with local config replacement without contaminating Git.

## Production warning

This is a prototype multiplayer model. For authoritative real-time racing, add a server-side movement validator or dedicated WebSocket/game server later.

## Asset Ingestion Gate

Status:
- Firebase live test: passed
- Local playability: passed
- Asset scaffold: created
- First tiny pack: created and integrated
- Assets generated locally via SVG
- Audio assets deferred (WAV generation skipped)
- All integrated assets have fallback behavior
- Bulk ingestion: not approved yet

Next approved step:
- Review first pack visually.
- Then approve a second tiny pack or begin replacing procedural placeholders asset-by-asset.

First pack limit:
- 3 car sprites
- 1 track background or tileset
- 1 start/finish banner
- 3 UI icons
- 5 SFX

Rules:
- No unknown licenses.
- No uncredited third-party assets.
- No bulk ingestion.
- No changes to multiplayer logic during asset scaffold phase.
- Keep asset manifest updated before integration.
