$base = "C:\Dev\archon-game\experiments\octane-street-racer\assets"
$pack = "$base\source-packs\first-tiny-pack-v1"
New-Item -ItemType Directory -Force -Path $pack | Out-Null

$readme = @"
# first-tiny-pack-v1
- purpose: first controlled Octane Racer asset integration test
- total asset limit: 3 cars, 1 track, 1 banner, 3 ui icons, 5 sfx
- source method: generated locally via SVG
- license status: project-owned/generated
- integration status: integrated
"@
Set-Content -Path "$pack\README.md" -Value $readme -Encoding UTF8

$carPink = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-15 -10 30 20"><rect x="-14" y="-8" width="28" height="16" fill="#ff3fb4" rx="2" ry="2" /><rect x="-7" y="-5" width="14" height="10" fill="#0b0f17" /></svg>'
Set-Content -Path "$base\cars\car-neon-pink-v1.svg" -Value $carPink -Encoding UTF8

$carCyan = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-15 -10 30 20"><rect x="-14" y="-8" width="28" height="16" fill="#36eaff" opacity="0.45" rx="2" ry="2" /><rect x="-7" y="-5" width="14" height="10" fill="#0b0f17" opacity="0.45" /></svg>'
Set-Content -Path "$base\cars\car-cyan-ghost-v1.svg" -Value $carCyan -Encoding UTF8

$carYellow = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-15 -10 30 20"><rect x="-14" y="-8" width="28" height="16" fill="#ffd166" rx="2" ry="2" /><rect x="-7" y="-5" width="14" height="10" fill="#0b0f17" /></svg>'
Set-Content -Path "$base\cars\car-yellow-rival-v1.svg" -Value $carYellow -Encoding UTF8

$trackLoop = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 720"><rect width="960" height="720" fill="#0e1322" /><rect x="120" y="80" width="720" height="560" fill="none" stroke="#2a3f70" stroke-width="88" /><rect x="120" y="80" width="720" height="560" fill="none" stroke="#1a243b" stroke-width="66" /></svg>'
Set-Content -Path "$base\tracks\track-neon-loop-v1.svg" -Value $trackLoop -Encoding UTF8

$banner = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 150"><rect width="30" height="150" fill="white"/><rect width="15" height="15" fill="black"/><rect x="15" y="15" width="15" height="15" fill="black"/><rect y="30" width="15" height="15" fill="black"/><rect x="15" y="45" width="15" height="15" fill="black"/><rect y="60" width="15" height="15" fill="black"/><rect x="15" y="75" width="15" height="15" fill="black"/><rect y="90" width="15" height="15" fill="black"/><rect x="15" y="105" width="15" height="15" fill="black"/><rect y="120" width="15" height="15" fill="black"/><rect x="15" y="135" width="15" height="15" fill="black"/></svg>'
Set-Content -Path "$base\ui\start-finish-banner-v1.svg" -Value $banner -Encoding UTF8

$iconBoost = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" fill="#36eaff"/></svg>'
Set-Content -Path "$base\ui\icon-boost-v1.svg" -Value $iconBoost -Encoding UTF8

$iconDrift = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5l6.74-6.76z" fill="#ff3fb4"/></svg>'
Set-Content -Path "$base\ui\icon-drift-v1.svg" -Value $iconDrift -Encoding UTF8

$iconGamepad = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M21.58 16.09l-1.09-7.66A3 3 0 0 0 17.5 6h-11a3 3 0 0 0-2.99 2.43l-1.09 7.66a2 2 0 0 0 1.96 2.27h1.4l1.6-1.6h9.24l1.6 1.6h1.4a2 2 0 0 0 1.96-2.27z" fill="#9cb1d8"/></svg>'
Set-Content -Path "$base\ui\icon-gamepad-v1.svg" -Value $iconGamepad -Encoding UTF8

Write-Host "Assets generated."
