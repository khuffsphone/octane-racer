# octane-smoke-check.ps1
# Octane Street Racer — automated pre-tag smoke check
# Usage: powershell -ExecutionPolicy Bypass -File scripts\octane-smoke-check.ps1
# Run from repo root, or pass -RepoRoot <path>

param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

Set-Location $RepoRoot

$pass = 0
$fail = 0
$warn = 0

function Chk-Pass([string]$label, [string]$detail = '') {
    Write-Host "  [PASS] $label" -ForegroundColor Green
    if ($detail) { Write-Host "         $detail" -ForegroundColor DarkGray }
    $script:pass++
}

function Chk-Fail([string]$label, [string]$detail = '') {
    Write-Host "  [FAIL] $label" -ForegroundColor Red
    if ($detail) { Write-Host "         $detail" -ForegroundColor Yellow }
    $script:fail++
}

function Chk-Warn([string]$label, [string]$detail = '') {
    Write-Host "  [WARN] $label" -ForegroundColor Yellow
    if ($detail) { Write-Host "         $detail" -ForegroundColor DarkGray }
    $script:warn++
}

Write-Host ''
Write-Host '============================================' -ForegroundColor Cyan
Write-Host '  OCTANE STREET RACER  —  Smoke Check' -ForegroundColor Cyan
Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''

# ─── 1. index.html exists ────────────────────────────────────────────────────
Write-Host '[ 1 ] Core file' -ForegroundColor White
if (Test-Path 'index.html') {
    $sz = (Get-Item 'index.html').Length
    Chk-Pass 'index.html exists' "$([math]::Round($sz/1KB,1)) KB"
} else {
    Chk-Fail 'index.html MISSING' 'Game will not load'
}

# ─── 2. Restored arcade markers ──────────────────────────────────────────────
Write-Host ''
Write-Host '[ 2 ] Restored arcade systems (index.html)' -ForegroundColor White
$markers = @(
    'gearStats','spawnEntity','handleCrash',
    'PERFECT SHIFT','NEAR MISS','boostMeter',
    'puddles','pickups','weather','birds','highScores'
)
$missing = @()
foreach ($m in $markers) {
    if (Select-String -Path 'index.html' -Pattern $m -Quiet) {
        Chk-Pass "Marker present: $m"
    } else {
        Chk-Fail "Marker MISSING: $m" 'Restored system may have regressed'
        $missing += $m
    }
}
if ($missing.Count -eq 0) {
    Write-Host '  All 11 restored systems present.' -ForegroundColor Green
} else {
    Write-Host "  MISSING: $($missing -join ', ')" -ForegroundColor Red
}

# ─── 3. No active Firebase credentials ───────────────────────────────────────
Write-Host ''
Write-Host '[ 3 ] Credential / security scan' -ForegroundColor White
$credPatterns = @('AIza','octane-racer-prototype','473393792194','1:473393792194')
$scanFiles = @('index.html','README.md','asset-manifest.json')
if (Test-Path 'CODEX_HANDOFF.md') { $scanFiles += 'CODEX_HANDOFF.md' }
$credFound = $false
foreach ($file in $scanFiles) {
    if (-not (Test-Path $file)) { continue }
    foreach ($pat in $credPatterns) {
        if (Select-String -Path $file -Pattern $pat -Quiet) {
            Chk-Fail "Active credential in $file" "Pattern: $pat"
            $credFound = $true
        }
    }
}
# Scan docs/ (skip qa-demo-candidate.md which documents the patterns as text)
if (Test-Path 'docs') {
    Get-ChildItem -Path 'docs' -Filter '*.md' |
        Where-Object { $_.Name -ne 'qa-demo-candidate.md' } |
        ForEach-Object {
            foreach ($pat in $credPatterns) {
                if (Select-String -Path $_.FullName -Pattern $pat -Quiet) {
                    Chk-Fail "Active credential in docs/$($_.Name)" "Pattern: $pat"
                    $credFound = $true
                }
            }
        }
}
if (-not $credFound) {
    Chk-Pass 'No active Firebase credentials found' 'firebaseConfig uses placeholder YOUR_API_KEY'
}

# ─── 4. asset-manifest.json valid JSON ───────────────────────────────────────
Write-Host ''
Write-Host '[ 4 ] Asset manifest' -ForegroundColor White
if (Test-Path 'asset-manifest.json') {
    try {
        $manifest = Get-Content 'asset-manifest.json' | ConvertFrom-Json
        Chk-Pass 'asset-manifest.json is valid JSON'
        $carPngs = $manifest.assets | Where-Object { $_.path -like 'assets/cars/*.png' }
        $count = @($carPngs).Count
        if ($count -ge 3) {
            Chk-Pass "Manifest contains $count car PNG entries"
        } else {
            Chk-Warn "Manifest contains only $count car PNG entries (expected >= 3)"
        }
    } catch {
        Chk-Fail 'asset-manifest.json parse error' $_.Exception.Message
    }
} else {
    Chk-Fail 'asset-manifest.json MISSING'
}

# ─── 5. Active car sprite PNGs exist ─────────────────────────────────────────
Write-Host ''
Write-Host '[ 5 ] Active car sprites' -ForegroundColor White
$sprites = @(
    'assets\cars\player-slickback-coupe.png',
    'assets\cars\traffic-police-cruiser.png',
    'assets\cars\traffic-junkyard-muscle.png'
)
foreach ($s in $sprites) {
    if (Test-Path $s) {
        $sz = (Get-Item $s).Length
        $szKB = [math]::Round($sz/1KB, 1)
        if ($sz -gt 51200) {
            Chk-Warn "$s is large ($szKB KB)" 'Consider optimizing (target <= 50 KB)'
        } else {
            Chk-Pass "$s" "$szKB KB"
        }
    } else {
        Chk-Fail "$s MISSING" 'Game will use procedural fallback car'
    }
}
# Old JPEG car files must NOT be tracked
$oldJpegs = git ls-files 'assets/cars/*.jpeg' 2>$null
if ($oldJpegs) {
    Chk-Fail 'Old JPEG car files tracked by git' ($oldJpegs -join ', ')
} else {
    Chk-Pass 'No old JPEG car files tracked by git'
}

# ─── 6. No raw ZIPs tracked ──────────────────────────────────────────────────
Write-Host ''
Write-Host '[ 6 ] Raw ZIP scan' -ForegroundColor White
$zips = git ls-files 2>$null | Where-Object { $_ -like '*.zip' }
if ($zips) {
    Chk-Fail 'Raw ZIPs tracked in git' ($zips -join ', ')
} else {
    Chk-Pass 'No raw ZIP archives tracked in git'
}

# ─── 7. No files over 100 MB ─────────────────────────────────────────────────
Write-Host ''
Write-Host '[ 7 ] Oversized file scan (> 100 MB)' -ForegroundColor White
$bigFiles = Get-ChildItem -Recurse -File |
    Where-Object { $_.FullName -notmatch 'venv_rembg' -and $_.Length -gt 100MB }
if ($bigFiles) {
    foreach ($f in $bigFiles) {
        Chk-Fail "Oversized: $($f.Name)" "$([math]::Round($f.Length/1MB,1)) MB"
    }
} else {
    Chk-Pass 'No files over 100 MB (venv_rembg excluded)'
}

# ─── Summary ─────────────────────────────────────────────────────────────────
Write-Host ''
Write-Host '============================================' -ForegroundColor Cyan
Write-Host '  RESULT SUMMARY' -ForegroundColor Cyan
Write-Host '============================================' -ForegroundColor Cyan
$failColor = if ($fail -gt 0) { 'Red' } else { 'Green' }
$warnColor = if ($warn  -gt 0) { 'Yellow' } else { 'Green' }
Write-Host "  PASS : $pass" -ForegroundColor Green
Write-Host "  FAIL : $fail" -ForegroundColor $failColor
Write-Host "  WARN : $warn" -ForegroundColor $warnColor
Write-Host ''
if ($fail -eq 0) {
    Write-Host '  OK  All checks passed. Safe to tag demo-candidate-v1.' -ForegroundColor Green
    exit 0
} else {
    Write-Host "  ERR  $fail check(s) FAILED. Fix before tagging." -ForegroundColor Red
    exit 1
}
