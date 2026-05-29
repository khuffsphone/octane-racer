# Octane Street Racer Assets

## 1. Purpose
This folder contains reviewed Octane Street Racer assets only.

## 2. Folder meanings
- **cars**: Car sprites and related textures
- **tracks**: Track backgrounds, tilesets, and environmental props
- **ui**: HUD elements, menu icons, and fonts
- **fx**: Particle effects, boost glows, and smoke textures
- **audio**: Sound effects and music tracks
- **source-packs**: Raw un-curated source packs (must be filtered before integration)

## 3. Allowed formats
- images: png, webp, svg
- audio: wav, mp3, ogg
- metadata: json

## 4. Licensing rule
Every asset must have a known license, source, and attribution entry in `asset-manifest.json` before it can be integrated.

## 5. First pack limit
- 3 car sprites
- 1 track background or tileset
- 1 start/finish banner
- 3 UI icons
- 5 SFX

## 6. Rejection rules
Reject assets if:
- license is unknown;
- attribution is missing;
- source is unclear;
- file is too large for the prototype;
- asset does not match the arcade/neon racing style;
- asset is unrelated to Octane Street Racer.

## 7. Integration rule
Do not wire assets into `index.html` until the first asset pack is reviewed and approved.
