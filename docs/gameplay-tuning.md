# Octane Racer — Gameplay Tuning Notes

Branch: `agent/claude-gameplay-tuning` (from `restore/vertical-arcade-baseline` @ 46815d5)

All values live in the inline script of `index.html`. Units: speed/accel are
px-per-second equivalents at the 800×600 canvas scale; rates marked "per frame"
are evaluated per animation frame (~60/s).

## Current values (after this tuning pass)

| System | Parameter | Baseline | Tuned | Notes |
|---|---|---|---|---|
| Gears | G1 max / accel | 250 / 450 | unchanged | |
| Gears | G2 max / accel | 450 / 300 | unchanged | |
| Gears | G3 max / accel | 700 / 200 | unchanged | |
| Gears | G2 lug threshold | ≤400 | **≤180** | See "spinout trap" below |
| Gears | G3 lug threshold | none | **≤380** | Closes the skip-to-G3 exploit |
| Gears | lug accel penalty | 50 | unchanged | |
| Gears | stress limit → spinout | 2.0 s | unchanged | decays at 2×dt when clear |
| Shifting | perfect-shift window | ±50 around threshold | unchanged | +500 pts |
| Braking | brake / coast / over-rev decel | 1200 / 100 / 500 per s | unchanged | |
| Steering | turn speed | 440·dt·speedFactor | unchanged | speedFactor 0.5–1.3 |
| Steering | rain handling penalty | up to −45% | unchanged | |
| Steering | active during invuln grace | no | **yes** | See "control freeze" below |
| Boost | trigger / speed / duration | meter 100 / 900 / 3.0 s | unchanged | |
| Boost | near-miss fill | +25 (4 misses = full) | unchanged | |
| Boost | score multiplier while boosting | 2× | unchanged | |
| Scoring | distance score | speed²·dt/1500 | unchanged | |
| Scoring | near miss / perfect shift / pickup / boost-smash | 500/500/1000/1000 | unchanged | |
| Near miss | lateral window | <50 px on pass | unchanged | |
| Traffic | spawn prob per frame | 0.03 + distance/250000, cap 0.12 | unchanged | max 12 entities |
| Traffic | car speed range | 80–300 | unchanged | |
| Traffic | lane-switch zone | y<250 | **y<200** | More reaction time |
| Traffic | lane-switch prob per frame | difficulty×0.05 | **difficulty×0.03** | difficulty = distance/20000 cap 1 |
| Traffic | switch cooldown | 2–4 s | unchanged | |
| Fuel | drain interval | 30 s | unchanged | lives are fuel |
| Fuel | airdrop interval | 60 s | **45 s** | See "fuel attrition" below |
| Fuel | emergency drop (at 1 life) | every 15 s | unchanged | never in player's lane |
| Fuel | pickup restores | +1 life (max 3), +1000 pts | unchanged | |
| Crash | invulnerability after crash/spawn | 2.0 s | unchanged | drive allowed now |
| Weather | rain duration / clear duration | 5–10 s / 12–22 s | unchanged | |
| Weather | puddle spawn per frame | intensity×0.015 | **intensity×0.008** | each puddle costs a life |

## Why each change

### 1. Gear-2 spinout trap (mechanics bug — the big one)
Baseline marks gear 2 as "lugging" at any speed ≤400, but the game's own
SHIFT UP prompt fires at 230 and the perfect-shift window for G1→G2 is
200–300. Lugging caps accel at 50, so after an obedient shift at ~233 the
player needs 3+ s to climb past 400 while the stress meter spins you out at
2.0 s. **Headless simulation of the baseline update() math confirms a
guaranteed spinout at t≈2.5 s for a player who follows the prompt.** The only
baseline-safe strategy was double-shifting straight into gear 3, which had no
lug check at all. Fix: G2 lug threshold 180 (just below the shift window
floor), and a matching G3 lug threshold of 380 (below the G2→G3 window floor
of 400) so skipping gears is risky instead of optimal. Same simulation after
the fix: perfect shifts at 233/433, reaches 696, no spinout.

### 2. Control freeze during grace (feel)
Baseline gated throttle, boost, AND steering behind `invulnerable<=0`. Every
run started with 2 s of dead controls, and every crash added another 2 s
freeze on top of losing all speed. Now driving stays live during grace;
invulnerability still shields traffic collisions and puddles (those checks
were already gated separately). Crash penalty = lost speed + a fuel can,
which is punishment enough.

### 3. Lane-switch ambush (fairness)
At full difficulty, traffic switched lanes at 5%/frame (~3 attempts/s) as low
as y=250 — at gear-3 closing speeds (~620 px/s relative) that's ~0.3 s to
react to a swerve directly ahead. Tuned to y<200 and 3%/frame: switches still
pressure the player but happen far enough up the road to dodge. Turn-signal
blink (last 0.5 s of cooldown) is unchanged.

### 4. Puddle spam (fairness)
Full-intensity rain spawned ~0.9 puddles/s, each a hydroplane that costs a
life — a single 8 s storm could end a run on its own. Halved to ~0.5/s.
Rain frequency, handling penalty, and the boost-immunity to puddles are
unchanged, so storms still matter.

### 5. Fuel attrition (difficulty curve)
Drain is 1 can/30 s but airdrops came 1/60 s, so net fuel income was always
negative and long runs hovered permanently at 1 life inside the CRITICAL-FUEL
emergency loop. Airdrops every 45 s keep net pressure negative (you still
can't idle) but let a player who catches drops ride at 2 lives instead of
living at the edge the whole run.

## Expected curve after tuning
- 0–30 s: learn shifts, low traffic (spawn 0.03/frame), no lane switching
  yet (difficulty ≈ 0 until distance builds), first fuel drain at 30 s.
- 30–60 s: gear 3 cruising, lane-switching fades in, first airdrop at 45 s.
- 120 s+: spawn rate climbing toward cap, lane switching at full strength,
  score rate ~326/s at G3 (1080/s boosted) vs. high-score floor of 2000.

## Verification done
- Headless Node simulation of gear/stress math (before vs. after) — see §1.
- `node --check` on the extracted module script — passes.
- Core-system scan (`gearStats`, `spawnEntity`, `handleCrash`, `PERFECT
  SHIFT`, `NEAR MISS`, `boostMeter`, `puddles`, `pickups`) — all present.
- Credential scan and >25 MB file scan — clean.

## Rebase After Asset Integration

- AG branch inspected: `agent/ag-assets-integration-local` @ e3aba18 (2 commits:
  sprite/UI integration + audit reconcile). Changes: asset loader with
  procedural fallback, JPEG sprites for player/traffic cars, splash/menu
  background images, solo-first sidebar with multiplayer demoted behind a
  toggle, game-over stats panel (distance/time/top gear/near misses).
- Rebase: clean, no conflicts. All six tuning changes verified present
  post-rebase; AG's loader, stat counters (reset/increment/display), and UI
  changes intact alongside them.
- Visual changes that affect tuning: none mechanically. Road geometry
  (ROAD_X 200 / ROAD_W 400), car hitboxes (32×64), near-miss window (<50 px),
  gear table, and the whole update() loop are untouched by AG — sprites are
  drawn into the same boxes the fallback rectangles used.
- Tuning values: still valid; no constant changes needed in this pass.
- Recommended manual playtest focus:
  1. **Perceived hitbox fairness** — the JPEG sprites have no alpha channel,
     so each car renders as a full 32×64 rectangle including baked-in
     background pixels. If the painted car body looks narrower than the
     rectangle, collisions and near-misses will feel wrong even though the
     numbers are unchanged. If playtest confirms this, the fix is tighter
     crops / alpha PNGs (pipeline in asset-ingestion-audit.md), not constant
     changes.
  2. Near-miss readability with sprite traffic at gear-3 closing speeds.
  3. Menu/splash text contrast over the new background images.
- Housekeeping noted for AG: `assets/ui/hud-frame.jpeg` (630 KB) is committed
  but referenced nowhere in index.html — dead weight; drop it or wire it up.

## Still needs a human play test
- Whether 45 s airdrops feel too generous on mobile (smaller dodging space).
- Whether G3 lug at 380 ever surprises players who downshift hard while braking
  (brake decel 1200/s can drop through 380 quickly; stress needs 2 s, so it
  should be fine, but verify by feel).
- Multiplayer smoke (publish loop untouched, but per protocol any index.html
  change wants the two-browser test rerun before merge to main).
