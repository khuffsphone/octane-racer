# Octane Racer — Progress Log

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
