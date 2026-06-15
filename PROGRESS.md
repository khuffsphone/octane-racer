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
