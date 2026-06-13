# Octane Street Racer — Master Flow Image-Gen Prompts (v2.0.0-m2)

Copy-paste each block into Google Flow's **image** engine (not Veo video). Generate on a
flat magenta background, then hand results to the integration agent — it keys out the
magenta, crops, rotates nose-up, resizes to spec, compresses, and wires into the manifest.

Build palette (match exactly): asphalt `#14141f` · guardrails `#39ff14` · player `#ff3300` ·
traffic `#ffff00` & `#8a2be2` · gas `#00ff66` · puddles `rgba(0,188,255,0.4)`.

## Already covered — DO NOT regenerate
- Player coupe, police-cruiser traffic, junkyard-muscle traffic (in game now).
- Splash + menu garage backgrounds (in repo).
- Drive has raw renders for Neon Lowrider / Armored Hauler / Luxury Sedan (¾-view; usable as
  extra traffic only after conversion — generate fresh top-downs in Flow for cleaner results).

## HOUSE-STYLE BLOCK (paste at the top of every CAR/OBJECT prompt)
```
Top-down orthographic sprite for a neon arcade racing game. TRUE bird's-eye view, camera
straight down (90° overhead), NOT 3/4 or perspective. Subject centered, nose toward the TOP,
filling ~85% of frame. Flat even lighting, crisp hard edges, subtle neon rim light, game-ready.
Background: solid flat pure magenta #FF00FF, perfectly uniform. NO shadow, NO ground, NO road,
NO reflection, NO motion blur, NO text, NO logos, NO badges, NO real brand styling. One subject
only, square framing.
```
Negative field (if available): `perspective, 3/4 view, side view, isometric, tilted camera, drop shadow, ground, asphalt, multiple subjects, people, motion blur, lens flare, watermark, text, logo, busy background, realistic photo background`

---
## STEP 1 — Player car  (`playerCar`, red #ff3300) → 64×128 PNG
```
…HOUSE BLOCK… A sleek low-slung sports coupe, glossy hot orange-red body (#ff3300), cyan neon
underglow, dark tinted windshield, aggressive aerodynamic hero-car silhouette, looks fast and premium.
```
## STEP 2 — Traffic sedan  (`trafficCar1`, yellow #ffff00) → 64×128 PNG
```
…HOUSE BLOCK… A boxy city sedan / taxi, electric yellow body (#ffff00), black window strip,
plain civilian look, silhouette clearly different from a sports car so it reads as traffic.
```
## STEP 3 — Traffic muscle/SUV  (`trafficCar2`, purple #8a2be2) → 64×128 PNG
```
…HOUSE BLOCK… A chunky muscle car / SUV, vivid purple body (#8a2be2), wide aggressive stance,
bulky silhouette, distinct from both the sedan and the coupe.
```
## STEP 4 — Traffic variants 3 & 4 (optional, `trafficCar3/4`) → 64×128 PNG
```
…HOUSE BLOCK… A compact hatchback, electric cyan body (#28e9ff), rounded friendly silhouette.
```
```
…HOUSE BLOCK… A boxy delivery van, matte white body with magenta accent stripe, tall slab silhouette.
```
(Keep colors away from player red so the player stays readable.)

## STEP 5 — Gas pickup  (`gasCan`, green #00ff66) → 48×48 PNG
```
…HOUSE BLOCK… A chunky retro jerry-can fuel pickup, glowing neon green (#00ff66), small spout,
simple iconic readable shape, soft green glow. Centered, fills ~70% of frame.
```

## STEP 6 — Explosion sprite sheet (optional; procedural is the no-cost default) → 6-frame strip
```
A horizontal sprite STRIP of 6 frames of a cartoon arcade explosion, left to right: spark →
fireball → expanding orange-yellow burst → smoke ring → dissipating embers → fade. Each frame
on flat pure magenta #FF00FF, evenly spaced, identical frame size, centered. Bold neon-arcade
style, hard edges, no text, no realistic smoke.
```

## STEP 7 — Start-line sign-holder ("grid" sprite) → 64×128 PNG
```
…HOUSE BLOCK… A stylized arcade pixel-art figure standing and holding a large blank rectangular
number board overhead, retro motorsport "grid" sign-holder, neon-synthwave styling, tasteful and
cartoonish (no realism), bold readable silhouette. The board face is plain white (numbers added
later in-engine). Centered, full figure.
```

## STEP 8 — Splash background (only if it beats the procedural one) → 4:3 (matches 800×600)
```
Neon synthwave city street at night, wet asphalt reflecting magenta and cyan signage, distant
skyline, retro-futuristic 1980s arcade vibe. Dark and uncluttered in the CENTER and LOWER THIRD so
large white pixel-font title text stays readable. No text in the image. 4:3.
```
## STEP 9 — Menu / garage background → 4:3
```
Underground neon parking garage, custom cars in shadow under magenta/cyan tube lighting, concrete
pillars, arcade racing mood. Darker overall, central area clear for menu buttons. No text. 4:3.
```

## POST-PROCESS (the integration agent does this — for your reference)
1. Key out #FF00FF → alpha. 2. Crop tight, rotate nose-up. 3. Resize to the target box
(cars 64×128, pickup 48×48, sign-holder 64×128), pad with transparency, don't stretch.
4. Export PNG-24+alpha, compress to ≤ ~18 KB (cars) / ≤ ~8 KB (pickup). 5. Sanity-check on a dark
background — corners transparent, no magenta fringe, body within the central ~32×64 (hitbox fairness).

## DELIVERY → how to get these to me
Pick one: (a) drop the PNGs into this chat, (b) commit them under `assets/cars|fx|ui/`, or
(c) attach a zip to a GitHub release (the route that worked before). Then I convert, integrate
(inline base64 or `assets/` file), update the manifest + license, run the smoke check, and PR.

## What I do NOT need Flow for (procedural, zero files, building now/next)
Explosions, nitro flames, skid marks, screen shake, neon guardrail bloom, parallax skyline,
and all sound effects — these are canvas/Web-Audio code, no assets required.
