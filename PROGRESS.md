# Octane Racer — Progress Log

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
