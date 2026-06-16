# Octane Racer — Progress Log

## Wave 1 — Game-over flow + high scores
Branch: `agent-claude/m4-gameover-flow` (off `main`, after #12–#15 merged)

### Done
1. **Run stats + one score function.** `freshPlayer` gains `topSpeed`/`bestCombo`, tracked each
   frame in `update`. `scoreRun()` = `f(distance, topSpeed, bestCombo, nearMisses)` with all
   weights in one tunable `SCORE` block; it's the single source of the final score (`lastRunScore`).
2. **Procedural game-over explosion (no sprite).** `applyImpact(…, 'gameover')` now emits a fully
   procedural burst — neon sparks (cyan/magenta/green) + hot debris + smoke + two expanding
   `spawnShockwave` rings — replacing the `fxExplosion` sprite path. New pooled `shockwaves`
   system (`spawn/update/draw`, additive, capped).
3. **Death sequence over a dimmed frozen frame.** New `gameState='dying'`: `endRun()` fires the
   explosion then holds for `DEATH_DUR` (0.9 s) while `updateDeath()` animates particles/FX/
   shockwaves/impact-decay (gameplay frozen); `render()` ramps a dim veil; then `triggerGameOver()`
   shows the overlay. Reduced-motion skips straight to the overlay.
4. **GAME OVER overlay** shows DISTANCE, TOP SPEED, BEST COMBO, NEAR MISSES + the final SCORE.
   Coexists with #15's `gameover.jpg` backdrop (the dim+explosion play on the canvas during
   `dying`, then the art overlay slides in).
5. **HighScoreStore** (IIFE, built to spec — `highscore.js` wasn't supplied): cap-5, sort desc,
   `qualifies(score)`, `add(name,score)` → new-row index, localStorage in try/catch, corruption-
   safe load (validates + sanitizes parsed JSON, falls back to defaults). Wired into the qualify
   check, save, and board. Initials entry now 3–8 chars (touch input + keyboard; **Enter** saves);
   the new row is **highlighted** on the top-5 board. Added a blinking **TAP TO RESTART** (tap the
   game-over screen, except buttons/while entering initials).
6. **Clean restart.** `initGame` clears `shockwaves`/`deathTimer` on top of the existing
   `resetImpactState()` + fresh player — asserted no leftover shake/hitstop/rage/combo/topSpeed.

### Verification (headless — no browser here)
- `node --check` clean; boots. In-scope logic sim: HighScoreStore cap=5 + sorted, qualifies
  (low=false / high=true / zero=false), `add` returns the new row index & stays capped & persists,
  names sanitized, corruption survives; `scoreRun()` computes from stats; restart zeroes every
  transient (shake/hitstop/rage/shockwaves/deathTimer/combo/topSpeed, bestCombo→1).
- **Pending manual/browser QA:** the death-explosion feel + dim veil, the gameover backdrop
  coexistence, initials entry on a device, and tap-to-restart.

### Assumptions logged
- `highscore.js` wasn't attached → implemented `HighScoreStore` to the described API and
  sandbox-tested it headlessly.
- Final score is `scoreRun()` (a pure function of run stats); the live HUD score stays the
  in-play running tally. Weights live in `SCORE` (tunable).
- No new assets (procedural explosion) → `asset-manifest.json` unchanged.

### Build size
`index.html` **+5.3 KB** (code only) → 1.24 MB. No asset-budget impact.

---

## Phase 3 — Obstacles (cones / barriers / oil slicks) + road decals
Branch: `agent-claude/phase3-obstacles` (off `main`)

### Done
1. **Obstacle subtypes + weighted spawn.** `spawnObstacle()` reuses the traffic spawner pattern
   (`pickSpawnLane` fairness) and pushes one of three `otype`s into the existing `entities` array:
   cones ~55%, barriers ~27%, oil slicks ~18% (measured 442/220/138 over 800 spawns, 0 misses).
   All procedural in `drawObstacle(x,y,w,h,otype,yaw)` — no sprites. They scroll + despawn off-screen
   via the existing entity cull (verified: an off-screen obstacle is removed within one update, no leak).
2. **Per-type reactions, all via applyImpact / the existing hazard path** (no bespoke FX):
   - **cone** → light clip: `applyImpact(…,0.3,'sideswipe')` + speed scrub + a tyre scuff
     (`grindScrape`), and the cone is knocked tumbling away (`vx/vy/spin`, brief 0.18 s debounce).
   - **barrier** → `handleCrash(false)` → hard `applyImpact(…,'crash')`.
   - **oil slick** → `handleHydroplane()` (the existing grip-loss/spin path) — NOT a crash; you
     drive through it, with a 1.2 s re-trigger cooldown.
3. **Persistent decals reuse the impact-juice pool (no second system).** Heavy-braking tyre marks
   (existing `spawnDecal('skid')`, whose primitive already renders dual tyre tracks), drift marks,
   and grind scrape streaks (`grindScrape`) all write into `decals[]` — capped (80 total / 14
   scrape) and fading via `updateDecals`. Cone clips also feed a scrape streak.

### Verification (headless — no browser here)
- `node --check` clean; boots. In-scope sim driving the real `update()` with the reaction
  functions stubbed to count calls: cone → `['sideswipe']` impact, no crash, knocked=true;
  barrier → crash=1; oil slick → hydro=1; spawn distribution 442/220/138/0; off-screen despawn=true.
- **Pending manual/browser QA:** the feel of cone clips vs barrier crashes vs oil-slick spins,
  and that fairness (≥1 open lane) holds with hazards + traffic mixed.

### Assumptions logged
- Built off `main` (has #13's applyImpact + decal pool + hydroplane). #16 (game-over flow) is an
  open PR, not merged — Phase 3's real dependencies are all on `main`, so this branches off `main`
  as instructed; the collision region lightly overlaps #16, so expect a tiny reconcile at merge.
- Oil slicks are surface hazards (drive-through, like rain puddles), not solid colliders.
- No new assets (all procedural) → `asset-manifest.json` unchanged.

### Build size
`index.html` **+2.8 KB** (code only). No asset-budget impact.

---

## Screen art — synthwave backdrops behind title/menu, game-over, leaderboard, new-high-score
Branch: `agent-claude/screen-art` (off `main`)

### Done
1. **4 backdrops inlined** in `assetManifest` (`screenTitle/Gameover/Leaderboard/Victory`) as
   base64 JPEGs — chosen from the 20 supplied renders by measuring luminance in each screen's
   exact text region (darkest-where-text-goes wins): title = retro-sun synthwave grid; gameover
   = stormy neon skyline; leaderboard = car-left with a dark right column; victory = neon-arch
   spark burst. Cover-fit 800×600, JPEG q74, loaded by the existing asset loop.
2. **Per-screen backdrop + scrim** applied by `applyScreenBackdrops()` (called after assets load
   and from `showScreen`): each overlay's background = a directional scrim gradient layered over
   the image (top-heavy for title/gameover/victory so upper text reads; right-heavy for the
   leaderboard so the list column reads). If an image didn't load, the overlay keeps its
   gradient/`#0a0a14` base — the **procedural fallback**.
3. **Title/menu**: `screenTitle` on the splash (now `has-art`, logo + prompt in the dark upper
   band) and the menu (replaces the garage bg).
4. **Game over**: `screenGameover` with GAME OVER + run-stats in the dark upper area.
5. **New high score**: `updateGameOverArt(true)` swaps the gameover backdrop to `screenVictory`
   and adds `victory-mode` (banner + initials float top-centre) when a record is set; reverts
   to `screenGameover` otherwise.
6. **Leaderboard**: `screenLeaderboard` with the top-5 table pinned to the dark right column.

### Verification (headless — no browser here)
- `node --check` clean; headless boot OK. With the mock `Image` forcing failures, the fallback
  path runs cleanly (no crash, overlays keep their gradient) — confirms graceful degradation.
- Image picks validated by per-region luminance + a rendered scrim preview (text legible in
  each screen's dark zone).
- **Pending manual/browser QA:** actual on-screen look of each backdrop + scrim and text
  contrast (CSS background rendering is browser-only here).

### Budget
4 backdrops ≈ 205 KB JPEG / **+275.9 KB** base64 inlined. Shipped footprint (referenced asset
files + inlined base64) **2.24 MB / 3 MB** — under budget but tightening (~0.76 MB headroom);
flagging per the brief. `index.html` 1.01 MB → 1.30 MB.

---

## Milestone 3G — Sim-Physics v2: aero drag + KERS + thermal
Branch: `agent-claude/m3g-sim-physics` (off fresh `main`, after #8/#10/#9/#11 merged)

### Done
1. **Three verified classes, dropped in verbatim** — `AeroDragModel`, `KersSystem`,
   `ThermalModel` from the reviewed `octane_3g.js` (not rewritten), each instantiated once
   with a tunable config tuned to the game's MPH scale (`drag`, `kers`, `thermal`).
2. **Cooperative drive (not a second drive)** — in fixed `update(dt)` the 5-gear/RPM curve
   stays the single drive source: each gear's MPH cap is converted into the drag model's
   **throttle term** (`throttle = (dragCoeff·cap² + rollingResist·cap)/driveForceMax`), so
   full throttle in a gear asymptotes toward *that gear's* ceiling via v² drag — the old
   hard `speed-=60*dt` soft cap is gone. `accel = drag.getAcceleration(throttle·powerMult,
   brake01, speed) + kers.getBoostForce()/mass`; speed integrates and clamps ≥0. Engine bog
   (−42%) now scales the throttle term.
3. **Thermal tyre grip MULTIPLIES into 3A grip** — `player.gripFactor =
   (0.65 + tireWear/100·0.35) · thermal.getTyreGripMultiplier()` (cold/hot tyres lose grip;
   the wear-based grip is not overridden). Tyre heat is fed a blended work input
   (speed + slip + braking), so tyres warm into the optimal window at racing speed.
4. **KERS** — harvests under braking, deploys on **K** / gamepad bumper as its own boost
   force (decoupled from nitro). HUD surfaces `charge01` (gauge under the nitro bar) plus
   engine + tyre temperature pips beside the RPM bar. State resets each run.
5. **Engine overheat REPLACED, not doubled** — the old §5.1 forced-50-MPH/−15%-fuel rule is
   removed; `thermal.getEnginePowerMultiplier()` is now the sole engine-heat consequence
   (continuous drive derate) with a visual fire cue + one-shot warning when it bites.
6. **Tuned for fun** — constants chosen so normal fast driving stays cool, while lugging at
   low-gear redline overheats and hard cornering overheats tyres.

### Verification (headless — no browser in this environment)
- `node --check` clean; headless boot OK (asset-loader fallback path exercised).
- Physics sim driving the **shipped** class configs through the real integration math:
  - Per-gear top speed asymptotes to cap (110/145/185 exact; gear1/2 a touch under from
    low-airflow derate); nitro top gear → 231 MPH. **No hard cap.**
  - Braking 180→0 in 1.17 s vs the old flat-rate 2.0 s. **Harder.**
  - KERS harvests ~65 over a stop; full-charge deploy adds ~27 MPH over 1.5 s.
  - Hold gear-1 redline → engine 126°, power ×0.84. Top-gear cruise stays cool (airflow).
  - Tyre grip: cold 0.86 → optimal 1.0 at speed → 0.82 when cornering-overheated.
- **Pending manual/browser QA:** in-race feel of the asymptotic top end, brake bite, KERS
  deploy, and the HUD gauges/pips.

### Build size
`index.html` +10.24 KB (code only — no new assets; the three classes + integration + HUD).

---

## Impact / Juice — consolidated severity-scaled collision feedback
Branch: `agent-claude/impact-juice` (off `main`)

### Done
1. **One orchestrator.** `applyImpact(x,y,severity,type)` (+ `impactState`) is the single
   entry point; `type ∈ scrape|sideswipe|crash|gameover`, `severity ∈ [0,1]`. All collision
   handlers route through it — `handleCrash`, `handleHydroplane`, the traffic/obstacle
   collision site, and `triggerGameOver`. The old inline crash FX (particles/explosion) and
   the `canvas.style.transform` setTimeout DOM-shake are removed (no scattered FX left).
2. **Screen shake** is applied to the world transform in `render()` (decaying random offset,
   amplitude `cap*severity` — 3px scrape → 10px crash, linear ease-out ~200ms, strongest
   concurrent wins). A dark pre-fill hides the revealed edge. **Hit-stop**: solid hits
   (`heavy && severity≥0.6`) freeze the sim 1–3 frames in the fixed loop; render still runs.
3. **Flash + vignette**: radial flash at the impact point + edge vignette, `alpha
   ~0.16*severity`, ~150ms fade; white for scrape/sideswipe, orange-red for crash/gameover.
4. **Particle burst** via `emitImpactBurst` — routes to `particlePool.emitBurst` if the 3F
   pool ever lands (`typeof` guard), else the existing emitter: sparks for scrape/sideswipe,
   debris + smoke for crash, the one big `fxExplosion` reserved for `gameover`.
5. **Scrape decals**: sustained grind drops fading dark streaks (`grindScrape`, pooled in
   `decals[]`, separately capped at 14, ~3s fade).
6. **Traffic reaction**: a glancing traffic hit (shallow horizontal penetration) is a
   *sideswipe* — shove (`vx`) + yaw spin (`spin`/`spinTimer`, drawn via `drawCar`'s rotation),
   sparks, player speed scrub (no dead stop); a hard hit (≥110 MPH) spins it off-lane and it
   re-acquires the nearest lane on settle. Deep/head-on overlap and obstacles still full-crash.
7. **Audio crunch** via the 3C synth (`playNoise`/`playTone`, level/pitch by severity;
   self-guards when audio is off/absent).
8. **Rage build**: reads the near-miss combo (`player.multiplier`); past tier 2 it ramps a
   smoothed `rage` 0→1 driving a faint warm edge tint + side speed-lines, and **resets on a
   crash**. Routine crashes stay procedural; only `gameover` gets the bigger explosion.
9. All amplitudes/decays/thresholds live in the `IMPACT` constants block.

### Verification (headless — no browser here)
- `node --check` clean; headless boot OK (asset-loader fallback path exercised, no errors).
- In-scope logic sim: scrape shake cap 3 / crash 10; hit-stop 0 for scrape, 3 for crash sev1,
  threshold 0.6→1 frame; severity(30/150/220)=0.2/1/1; shake fully decays in ~0.217s; rage
  builds to 0.94 at combo 5, resets to 0 on crash, decays to 0 at combo 1; scrape-decal cap
  holds at 14; glancing geometry classified correctly (side overlap = sideswipe, deep = crash);
  `sideswipeTraffic` spins+shoves the car, flags off-lane on a hard hit, scrubs player speed.
- **Pending manual/device QA:** felt weight/subtlety of shake, hit-stop, flash, and rage tint.

### Assumptions logged
- Hit-stop reserved for `heavy` (crash/gameover) so grinds/sideswipes stay smooth (brief says
  "severity ≥ ~0.6"; gated by type too, to keep it subtle per the dial-down directive).
- Added a light sideswipe/grind gameplay path (speed scrub + lateral nudge, 4 fuel, combo
  reset) so "sustained grinds" and traffic spin are possible — the old model made every
  overlap a full stop. Tunable in `IMPACT`.
- `gameover` explosion is emitted at death; the canvas freezes on game-over so it renders as a
  burst frame (most deaths follow a crash that already animated).
- No 3F ParticlePool / `particlePool` on main yet → uses the existing emitter; upgrades free.

### Build size
`index.html` **+10.29 KB** (code only — no new assets).

---

## M3d — Touch controls: drag wheel (left) + brake/gas/shift (right)
Branch: `agent-claude/m3d-touch-controls` (off `main`)

### Done
1. **Overlay** replaces the old D-pad. Bottom-left: the attached `wheel.png` (256×256,
   quantized, inlined as a base64 data URI in `#wheelImg`) with a procedural KERS/nitro
   **ring** + **T** hub drawn on top (`#wheelHud` canvas + `#btnT`). Right: `▲`/`▼` shift
   paddles + `BRAKE` + `GAS`, all CSS-vector. Shown only when touch is detected
   (`matchMedia('(pointer:coarse)')` / `ontouchstart` / `maxTouchPoints`) **and** racing
   (`body.touch.racing`), so it never covers menus.
2. **Steering wheel** — one captured `pointerId`; relative horizontal drag → `touchSteer`
   ∈ [-1,1] (`±70px` = full lock), self-centers toward 0 on release (~0.35s). The wheel
   **image rotates by `steerNormalized * 120°`** each frame (hub at image center). A new
   analog channel folds into the existing steer block (`max-magnitude` of touch vs gamepad);
   keyboard arrows + gamepad stick are unchanged.
3. **Pedals / paddles / turbo** — `GAS`→`ArrowUp`, `BRAKE`→`ArrowDown` (held, pointer
   capture so a slide-off still releases). `▲`/`▼`→`doUpshift()/doDownshift()` (one per tap).
   `T`→nitro (`keys.Space`) always, **plus KERS deploy (`keys.KeyK`) only if `KersSystem`
   exists** — branch is off current main (no #12), so T is nitro-only, the expected fallback;
   the KERS ring/deploy light up for free once #12 lands.
4. **Multitouch** — each control owns its own `pointerId` + `setPointerCapture`, so a left
   thumb steers while a right thumb holds gas. `touch-action:none` + `preventDefault` on the
   overlay kill scroll/zoom/double-tap.
5. **Desktop/keyboard/gamepad untouched**; overlay is additive and touch-only.

### Verification (headless — no browser here)
- `node --check` clean; headless boot OK on both desktop and touch device profiles (no errors).
- No residual old-control references (`btn-up/down/left/right/nitro`, `ctrl-btn`, `bindTouch`).
- Steer-math checks: drag +35px→0.50, +90px→clamp 1.0, −50px→−0.71; self-center 1→0 in 21
  frames (0.35s); channel combine prefers the larger magnitude; deadzone gating + rotation
  (steerNorm 0.8 → 96°); wheel data URI confirmed inlined.
- **Pending manual/device QA:** on-device multitouch feel, wheel rotation/self-center, and
  whether `±70px` drag range feels right per screen size.

### Assumptions logged
- `control_overlay_mockup.svg` was never provided; per the follow-up I used `wheel.png` as the
  wheel image (rotated by `steerNormalized`, hub at center, KERS ring + T procedurally on top)
  and kept the pedals/shifter as CSS-vector.
- Wheel resized 360→256 and palette-quantized (64 colors, alpha preserved) to cut the inline
  payload from 118 KB → ~46 KB.
- Steer mapping = relative horizontal drag (most robust without on-device playtest), not polar
  angle; tunable via `RANGE`/`WHEEL_MAX_DEG`.
- Did **not** merge #12 (per instruction — that's your browser QA + merge).

### Build size
`index.html` **+64.94 KB** (≈46 KB inlined wheel image + ≈4 KB code/CSS; net of removing the
old D-pad markup/CSS).

---

## Milestone 3E — deterministic fixed-timestep loop + player steer sprites
Branch: `agent-claude/m3e-fixed-loop` (off `main`)

### Done
1. **Steer assets** — 7 PNGs (`assets/car/player_*.png`) base64-inlined into
   `assetManifest.playerSteerFrames{straight,slightL,modL,hardL,slightR,modR,hardR}`.
   Loader special-cases the object → `playerSteer{}` Image dict; a missing frame just
   leaves the slot empty. Frame→file mapping was verified by a nose-lean silhouette
   metric (not guessed): −0.217=hardL … 0=straight … +0.217=hardR.
2. **`FixedTimestepLoop`** — accumulator loop, fixed 1/60 step, max-frame clamp (0.25s),
   ≤8 steps/frame spiral-of-death guard, `lerp()`. **Fix (a):** `visibilitychange` on
   `document`. **Fix (b):** `manualPaused` flag — never auto-resumes a manual/menu pause
   on tab-return.
3. **Loop refactor** — `update(dt)` kept; drawing wrapped as `render(alpha)`; the old
   `requestAnimationFrame(gameLoop)` driver replaced with `new FixedTimestepLoop(update,
   render, 1/60).start()`. The one wall-clock read in `update()` (a `Date.now` MP-publish
   throttle, dead in solo) is now a `dt` accumulator — `update()` is fully time-source-clean.
4. **Position buffering** — top of `update()` caches `prevX/prevY` on player + each traffic
   entity and `prevBgOffsetY`. `render(alpha)` interpolates those via `lerp(prev,cur,alpha)`
   using a save→overwrite→`draw()`→restore wrapper, so `draw()`'s body is untouched.
   Peds/props/decals snap (non-critical).
5. **Steer frame** — single smoothed `steerNormalized ∈ [-1,1]` set from the steer input
   (so the §5 wheel can feed it later). `drawPlayerCar()` picks by `|steer|` (<.15 straight,
   <.5 slight, <.8 mod, else hard; sign→L/R) and falls back to procedural `drawCar()` if a
   frame is absent.

### Verification
- `node --check` clean after every task.
- Headless loop test: ~59 `update(1/60)` steps over 1.0 s at 60/120/144 Hz (constant →
  refresh-independent); 5 s hitch clamps to 8 steps (no spiral of death).
- **Pending manual/browser QA:** actual boot-to-title/into-race + visual steer-frame and
  interpolation smoothness (no browser in this environment).

### Assumptions logged (per autonomy directive)
- Branched off `main` (M3a only). The 3B HUD (#8), 3C audio (#10), splash (#9) PRs are still
  open and also edit `index.html` — small reconcile expected at merge.
- Steer frames drawn 72×72 centered on the player (sprites are square 164×164, nose-up); a
  touch larger than the old 32×64 procedural car but reads better. Hitbox unchanged.
- `manualPaused` flag wired though no pause UI exists yet (future-proofing the fix).
- MP `Date.now` throttle → `dt` accumulator (dead code in solo; done for determinism).

### Build size
`index.html` 245 KB (~+159 KB inlined steer frames, ~+3 KB code). No other asset impact.
