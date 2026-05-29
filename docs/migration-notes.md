# Octane Racer Migration Notes

## Source

Old local container:
C:\Dev\archon-game

Old GitHub container:
khuffsphone/archon-game

## Destination

New local project:
C:\Dev\octane-racer

New GitHub target:
khuffsphone/octane-racer

## Reason

Octane Racer is now its own project and must be separated from the old repository container.

Future development should happen in C:\Dev\octane-racer.

## Important Direction

The original arcade gameplay is the gameplay baseline.

The simplified circular-track multiplayer prototype is not the final gameplay target.

Firebase multiplayer should wrap around the restored arcade gameplay. It should not replace the original arcade game loop.

## Preserved Sources

- Current multiplayer prototype: index.html
- Firebase rules: firebase.rules
- Asset scaffold: assets/
- Asset manifest: asset-manifest.json
- Handoff docs: CODEX_HANDOFF.md
- Original arcade baseline: legacy/original/Octane_Street_Racer.html, if present
