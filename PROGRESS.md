# Octane Racer — Progress Log

## Milestone 3E — deterministic fixed-timestep loop + player steer sprites
Branch: `agent-claude/m3e-fixed-loop` (off `main`)

### Done
1. **Steer assets** — 7 PNGs (`assets/car/player_*.png`) base64-inlined into
   `assetManifest.playerSteerFrames{straight,slightL,modL,hardL,slightR,modR,hardR}`.
   Loader special-cases the object → `playerSteer{}` Image dict; a missing frame just
   leaves the slot empty. Frame→file mapping was verified by a nose-lean silhouette
   metric (not guessed): −0.217=hardL … 0=straight … +0.217=hardR.
2. **`FixedTimestepLoop`** — accumulator loop, fixed 1/60 step, max-frame clamp (0.25s),
   ≤8 steps/frame spiral-of-death guard, `lerp()`. **Object-form constructor**
   `new FixedTimestepLoop({ update, render, onPanic })`; `SIM_DT` is an internal module
   const (never passed positionally). **`onPanic`** is wired to the spiral-of-death guard —
   when the loop falls ≥8 steps behind it resets the accumulator and calls `onPanic(frame,
   steps)` (logs a warning) instead of silently dropping time. **Fix (a):** `visibilitychange`
   on `document`. **Fix (b):** `manualPaused` flag — never auto-resumes a manual/menu pause
   on tab-return.
3. **Loop refactor** — `update(dt)` kept; drawing wrapped as `render(alpha)`; the old
   `requestAnimationFrame(gameLoop)` driver replaced with `new FixedTimestepLoop({ update,
   render, onPanic }).start()`. The one wall-clock read in `update()` (a `Date.now` MP-publish
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
- `node --check` clean (inline module extracted and checked) after every edit.
- Headless determinism harness (loop class run verbatim with a mocked clock/rAF):
  1.0 s wall-clock → **60 Hz = 59, 120 Hz = 60, 144 Hz = 60** fixed `update(1/60)` steps
  (refresh-independent); every `update` receives exactly `SIM_DT`; `alpha ∈ [0,1)`.
  5000 ms single-frame hitch → clamps to **8** steps and fires **exactly one** `onPanic`
  (no spiral of death).
- **Browser QA (static server + headless preview):** boots splash → menu → race; canvas HUD
  (score/speed/nitro/gear/fuel), parallax scenery, pedestrians, obstacles, audio ("SOUND ON")
  all render; console shows `Assets loaded: 17 + 7 steer` (all frames load, no errors);
  `onPanic` warning observed under the preview's background-tab rAF throttle (clamps correctly).
- **Steer mapping confirmed visually (not from filenames):** inspected the PNGs directly —
  `player_hardR.png` leans nose-up-right, `player_hardL.png` leans nose-up-left; in-game,
  holding → moved the car right and selected the `*R` frame. **Steering right leans right.** ✓
- *Caveat:* true high-refresh "no-stutter" smoothness can't be measured on a throttled headless
  preview; interpolation is logically verified (alpha lerp of cached prev→cur) and visually smooth.

### Assumptions logged (per autonomy directive)
- Branched off `main` (M3a only). The 3B HUD (#8), 3C audio (#10), splash (#9) PRs are still
  open and also edit `index.html` — small reconcile expected at merge.
- Steer frames drawn 72×72 centered on the player (sprites are square 164×164, nose-up); a
  touch larger than the old 32×64 procedural car but reads better. Hitbox unchanged.
- `manualPaused` flag wired though no pause UI exists yet (future-proofing the fix).
- MP `Date.now` throttle → `dt` accumulator (dead code in solo; done for determinism).

### Build size
`index.html` ~249 KB on the branch vs ~85 KB on `main` → **+164 KB**, almost entirely the
7 inlined steer-frame data-URIs (~+159 KB); loop/render/steer code is ~+3 KB. No other asset
impact (single file, zero new deps).

---

## 3E follow-up (2026-06-15) — object-form loop + onPanic, full QA
This branch already carried the M3E work; this pass corrected the one spec deviation and
completed verification:
- **`FixedTimestepLoop` is now object-form** `new FixedTimestepLoop({ update, render, onPanic })`
  with `SIM_DT` as an internal const (previously the constructor took `(update, render, step)`
  positionally). **`onPanic` is wired** to the spiral-of-death guard (was a silent `acc=0`).
- Re-ran `node --check` (clean) and the headless 60/120/144 Hz + hitch determinism harness
  (all pass — see Verification above).
- Completed browser QA on a static preview: boot → race, HUD/splash/audio intact, 7 frames
  load, and **steering right visibly leans the car right** (verified against the PNG art, not
  the filenames).
- Untouched: assets, the splash/HUD/audio merged from `main`, and the procedural `drawCar()`
  fallback (still used when a steer frame is absent).
