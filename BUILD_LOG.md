# Build Log — Octane Street Racer

## Milestone 2 — Gameplay Balancing & Playability Tuning
**Agent:** Claude Code (gameplay-systems)
**Branch:** `agent-claude/gameplay-tuning` (from `main` @ b199b8a)
**Version:** 2.0.0-m2

### Action taken
Landed the spec-complete v2 gameplay layer into `index.html` to the handoff §5
constants. This is a gameplay-model replacement: the 3-gear table and the
discrete `lives` model are retired in favour of a 5-gear RPM transmission and a
continuous fuel timer.

### Key decisions (delegated by human lead — "dealer's choice")
- **Branch base = `main`, PR target = `main`.** The prompt's literal §2 base
  (`restore/vertical-arcade-baseline`) is a 17-commit-stale pure ancestor of
  `main`; using it would have discarded the shipped sprites, mobile layout,
  underglow cleanup, QA package, and the `demo-candidate-v1` release. Built on
  `main` instead to preserve all of it. **Flagged** as a deviation from §2.
- **Car art = AG PNG sprites kept as primary, procedural vector as fallback.**
  Satisfies the "procedural-first graceful degradation" invariant (PNG =
  enhancement, vector fallback retained). **Flagged** as a deviation from §6's
  literal "procedural vector cars," chosen for aesthetics per the lead.
- **Implemented from §5 constants** (reference build + spec docs were absent).

### Subsystems implemented (file: `index.html`, all in the inline module)
- **§5.1 Transmission** — 5 gears, MPH caps 40/75/110/145/185; RPM 1000→10000
  linear per band; per-gear acceleration derived as (band ÷ idle→redline), which
  reproduces the spec's RPM/sec column. Perfect shift 9000–9500 RPM → +200 +
  speed kick; early upshift <8000 → engine bog (−42% accel, 1.5s); overheat at
  redline >1.2s → forced 50 MPH, −15% fuel.
- **§5.2 Nitro** — +25% top speed, 2.5s active, 8.0s cooldown, 2× fuel drain.
- **§5.3 Fuel timer** — tank 100; drain 1.2/s +0.2/s per gear>3; crash −20;
  gas pickup +35 (cap 100); game over at fuel ≤ 0.
- **§5.4/§5.7 Traffic & difficulty** — interval-based spawn (default 2.2s),
  every 2000 pts traffic +6% / spawn −8%, cap at 12000 pts.
- **§5.5 Weather** — state machine sunny45→warning5→rain30→clearing10 (90s);
  rain steering −35%; puddles 45×20, max 2; hydroplane = 360° spin 1.2s.
- **§5.6 Scoring** — passive +10/100px; near-miss edge gap 12–35px → +100×mult;
  multiplier ×1→×5, resets on any hit.
- **§5.8 Fairness** — gas/puddles never under traffic; ≥1 lane always open;
  post-crash invuln 2.5s.
- **§H** — localStorage high scores (try/catch → in-memory fallback); touch
  overlay gains shift + nitro buttons; `M` mutes; prefers-reduced-motion halts
  grid scroll + scenery + crash shake.

### Verification
- **`node --check`** on the extracted module: PASS.
- **HTML tag balance:** all balanced (div 53/53, section 5/5, script 1/1, …).
- **Release scan:** no live Firebase keys (placeholders only); no debug in the
  game loop; index.html 72 KB; assets 2.0 MB (≤3.0 MB); largest file 0.96 MB
  (≤25 MB); 800×600 canvas preserved; no Tailwind; single HTML file.
- **Headless numeric simulation** (the heart of Milestone 2) — ALL PASS:
  gear caps + accelRpm consistency; idle→redline times 1.2/1.8/2.4/3.2/4.8s;
  perfect-shift bands; fuel time-to-empty by gear; nitro double-drain; multiplier
  chain ×1→×5; weather cycle = 90s; difficulty tiers/cap.

### Sandbox/tooling blockers — NOT fabricated (§11)
This environment has **no browser**, so the interactive QA matrix **TC-01…TC-22**
(boot/white-screen, steering clamp, touch multi-touch, gamepad no-double-steer,
reduced-motion runtime, 60 FPS ≥90s, reload persistence) could **not** be
executed here. The systems are implemented to spec and verified statically +
by simulation; the TC matrix is **pending manual/browser QA** before release.

### Known deviations to review in PR
1. Branch base / PR target = `main`, not `restore/vertical-arcade-baseline` (§2).
2. PNG sprites kept as primary art over §6's procedural-vector cars (fallback
   retained).
3. Road is **4 lanes** (inherited from the shipped build); §5.8/§6 reference
   "3 lanes." Kept 4 to avoid destabilising collision/spawn geometry — flagged
   for a decision rather than silently changed.

### Status
Gameplay layer implemented and statically verified. Pending: manual runtime QA
(TC matrix) on a real browser/device.
