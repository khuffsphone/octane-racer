# Octane asset pipeline (`octane_assets.py`)

Turns raw Google Flow / Nano Banana renders into spec-compliant **64×128 transparent
sprites** and wires them into the game's `assetManifest` — chroma-key → autocrop → resize →
compress → base64 → patch. Verified against this build (see "Tested" below).

## Install
```
pip install pillow numpy scipy        # scipy optional (flood-fill falls back if absent)
# optional, smaller PNGs: apt-get install pngquant
```

## Typical run (Flow renders already in ./raw)
```
# 1. raw renders → 64×128 transparent sprites
python scripts/octane_assets.py process   --in raw --out sprites

# 2. patch the manifest (inline base64 — keeps the game one self-contained file)
python scripts/octane_assets.py integrate --in sprites --html index.html --mode inline

# …or both at once:
python scripts/octane_assets.py pipeline  --in raw --html index.html --mode inline
```
Use `--mode files` to write `assets/cars/<name>.png` and set paths instead of inlining.

## Filename → manifest key map
`player-coupe→playerCar`, `traffic-sedan→trafficCar1`, `traffic-muscle→trafficCar2`,
`traffic-van→trafficCar3`, `traffic-hatch→trafficCar4`, `traffic-rival→trafficCar5`,
`pickup-gas→pickupGas`. Override per file with `--map myfile.png:someKey`. New `trafficCarN`
keys are auto-added to `trafficAssetKeys` so spawned traffic actually uses them.

## Key behaviour
- Background key color is **auto-detected** from the corners — magenta `#FF00FF` and green
  `#00FF00` renders both work with no flag. Override with `--key magenta|green|#RRGGBB`.
- Only border-connected background is removed, so interior detail near the key hue survives.
- Already-transparent inputs (re-runs, alpha PNGs from Drive) skip keying.
- `index.html` is backed up to `index.html.bak` before any patch; the procedural `drawCar()`
  fallback is never touched.

## ⚠️ Honest caveats
- **`generate` (Gemini image API) does NOT work in the Claude Code cloud sandbox** — outbound
  egress is locked to GitHub, so `generativelanguage.googleapis.com` is unreachable, and it
  needs a `GEMINI_API_KEY` anyway. Generate art in **Flow** (or on an unrestricted machine) and
  use `process`/`integrate`, which are network-free and the rock-solid path.
- `process` resizes everything to 64×128. That's correct for cars; a gas-can/pickup ideally
  wants a smaller box — pass a custom size or accept the padded 64×128.
- Adding a `pickupGas` key loads an image the game doesn't draw yet (gas cans are procedural in
  `drawGasCan()`); it's a harmless no-op until that's wired. `trafficCarN` keys are used immediately.
- After integrating: open the game, confirm sprites render, delete/rename one asset to confirm
  the procedural fallback still draws, then run `scripts/octane-smoke-check.ps1`.

## Tested (in-sandbox, real runs — not claims)
- Red-on-magenta and purple-on-green keyed correctly → 64×128 RGBA, fully transparent corners,
  zero key-color fringe in the body.
- `integrate --mode inline` on a copy of the real `index.html`: replaced existing keys with data
  URIs, left untouched keys alone, added a new `trafficCar3` and registered it in
  `trafficAssetKeys`, wrote `index.html.bak`, and the patched module still passed `node --check`.
