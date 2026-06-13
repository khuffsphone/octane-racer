#!/usr/bin/env python3
"""
octane_assets.py — Octane Street Racer asset pipeline.

Turns raw art (Google Flow / Nano Banana renders, or images you generate via the
Gemini API) into spec-compliant 64x128 transparent sprites and wires them into the
game's `assetManifest` — chroma-key -> autocrop -> 64x128 -> compress -> base64 -> patch.

Subcommands
-----------
  generate   prompts.json -> Gemini image API -> raw PNGs        (needs GEMINI_API_KEY; optional)
  process    raw PNGs -> keyed/cropped/resized/compressed sprites (no network; the core)
  integrate  sprites -> patch index.html assetManifest            (inline data-URI) or assets/cars/ (files)
  pipeline   process + integrate in one go

Quick start (you already have Flow renders in ./raw)
  python octane_assets.py process   --in raw --out sprites
  python octane_assets.py integrate --in sprites --html index.html --mode inline

Install deps:  pip install pillow numpy scipy   (scipy optional; falls back if absent)

Design notes
------------
* Background key color is auto-detected from the image corners, so magenta (#FF00FF)
  and green (#00FF00) renders both work with no flag. Override with --key.
* Only background CONNECTED TO THE BORDER is removed (flood from edges), so interior
  car pixels that happen to be near the key hue are preserved. This is why the purple
  car can be shot on green and the green gas-can on magenta without punching holes.
* Despill runs only on feathered EDGE pixels, so solid body colors (e.g. the red player)
  are never desaturated.
* The procedural fallback in drawCar() is untouched — this only swaps manifest values.
* index.html is backed up to index.html.bak before any patch.
"""

import argparse, base64, io, json, os, re, shutil, subprocess, sys
from pathlib import Path

try:
    from PIL import Image, ImageFilter
    import numpy as np
except ImportError:
    sys.exit("Missing deps. Run:  pip install pillow numpy scipy")

try:
    from scipy import ndimage
    HAVE_SCIPY = True
except ImportError:
    HAVE_SCIPY = False

TARGET_W, TARGET_H = 64, 128
TARGET_KB = 20  # soft cap per sprite; warn if exceeded

# Filename -> manifest key (matches OCTANE_FLOW_MASTER_PROMPTS.md §H)
DEFAULT_MAP = {
    "player-coupe": "playerCar",
    "traffic-sedan": "trafficCar1",
    "traffic-muscle": "trafficCar2",
    "traffic-van": "trafficCar3",
    "traffic-hatch": "trafficCar4",
    "traffic-rival": "trafficCar5",
    "pickup-gas": "pickupGas",
}

NAMED_KEYS = {"magenta": (255, 0, 255), "green": (0, 255, 0),
              "blue": (0, 0, 255), "grey": (128, 128, 128), "gray": (128, 128, 128)}


# ─────────────────────────────────────────────────────────────────────────────
# Chroma key
# ─────────────────────────────────────────────────────────────────────────────
def _sample_corner_color(rgb):
    """Median color of the four 8x8 corners — robust to JPEG-ish noise."""
    h, w, _ = rgb.shape
    s = 8
    patches = np.concatenate([
        rgb[:s, :s].reshape(-1, 3), rgb[:s, -s:].reshape(-1, 3),
        rgb[-s:, :s].reshape(-1, 3), rgb[-s:, -s:].reshape(-1, 3),
    ], axis=0)
    return np.median(patches, axis=0)


def _border_connected(mask):
    """True where `mask` (background-like) is connected to the image border."""
    if HAVE_SCIPY:
        seed = np.zeros_like(mask)
        seed[0, :] = seed[-1, :] = seed[:, 0] = seed[:, -1] = True
        seed &= mask
        return ndimage.binary_propagation(seed, mask=mask)
    # Dependency-light fallback: iterative dilation from the border (bounded).
    out = np.zeros_like(mask)
    out[0, :] = out[-1, :] = out[:, 0] = out[:, -1] = True
    out &= mask
    for _ in range(max(mask.shape)):
        grown = out.copy()
        grown[1:, :] |= out[:-1, :]; grown[:-1, :] |= out[1:, :]
        grown[:, 1:] |= out[:, :-1]; grown[:, :-1] |= out[:, 1:]
        grown &= mask
        if np.array_equal(grown, out):
            break
        out = grown
    return out


def chroma_key(img, key_rgb=None, tol=0.18, feather=1.5, despill=True):
    """Remove the flat background to alpha. Returns RGBA PIL image + the key color used."""
    img = img.convert("RGBA")
    arr = np.asarray(img).astype(np.float32)
    rgb = arr[..., :3]

    key = np.array(key_rgb, np.float32) if key_rgb is not None else _sample_corner_color(rgb)
    dist = np.sqrt(((rgb - key) ** 2).sum(-1)) / (255.0 * np.sqrt(3))  # 0..1
    bg_like = dist < tol
    bg = _border_connected(bg_like)                                    # border-connected only

    alpha = np.where(bg, 0.0, 255.0).astype(np.float32)
    if feather > 0:                                                    # soft, anti-aliased edge
        alpha = np.asarray(
            Image.fromarray(alpha.astype(np.uint8)).filter(ImageFilter.GaussianBlur(feather)),
            np.float32)

    if despill:
        edge = (alpha > 0) & (alpha < 255)
        f = (1.0 - alpha / 255.0)[..., None]      # strongest where most transparent
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        kr, kg, kb = key
        if kr > 150 and kb > 150 and kg < 120:    # magenta key
            spill = np.maximum(0.0, (r + b) / 2.0 - g)
            corr = np.zeros_like(rgb); corr[..., 0] = spill; corr[..., 2] = spill
        elif kg > 150 and kr < 120 and kb < 120:  # green key
            spill = np.maximum(0.0, g - (r + b) / 2.0)
            corr = np.zeros_like(rgb); corr[..., 1] = spill
        else:
            corr = np.zeros_like(rgb)
        rgb = np.clip(rgb - corr * f * edge[..., None] * 0.9, 0, 255)

    out = np.dstack([rgb, alpha]).astype(np.uint8)
    return Image.fromarray(out, "RGBA"), tuple(int(x) for x in key)


# ─────────────────────────────────────────────────────────────────────────────
# Crop / resize / compress
# ─────────────────────────────────────────────────────────────────────────────
def autocrop(img, pad=2):
    bbox = img.split()[-1].getbbox()  # alpha bounding box
    if not bbox:
        return img
    l, t, r, b = bbox
    l, t = max(0, l - pad), max(0, t - pad)
    r, b = min(img.width, r + pad), min(img.height, b + pad)
    return img.crop((l, t, r, b))


def fit_canvas(img, w=TARGET_W, h=TARGET_H, fill=0.92):
    """Scale to fill ~`fill` of an w×h transparent canvas, preserving aspect, centered."""
    scale = min((w * fill) / img.width, (h * fill) / img.height)
    nw, nh = max(1, round(img.width * scale)), max(1, round(img.height * scale))
    img = img.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(img, ((w - nw) // 2, (h - nh) // 2), img)
    return canvas


def compress_png(img, target_kb=TARGET_KB):
    """Return PNG bytes, smallest of pngquant (if present) and Pillow optimize."""
    base = io.BytesIO(); img.save(base, "PNG", optimize=True); best = base.getvalue()
    if shutil.which("pngquant"):
        try:
            p = subprocess.run(["pngquant", "--quality=60-90", "--strip", "--force",
                                "--output", "-", "-"],
                               input=best, capture_output=True)
            if p.returncode == 0 and 0 < len(p.stdout) < len(best):
                best = p.stdout
        except Exception:
            pass
    if len(best) > target_kb * 1024:
        print(f"    ⚠ {len(best)//1024} KB (> {target_kb} KB target) — consider a simpler sprite")
    return best


# ─────────────────────────────────────────────────────────────────────────────
# Gemini image generation (optional; needs GEMINI_API_KEY)
# ─────────────────────────────────────────────────────────────────────────────
def gemini_generate(prompt, out_path, model="gemini-2.5-flash-image", api_key=None):
    """Best-effort call to the Gemini image API. Model names change — see
    https://ai.google.dev/gemini-api/docs/image-generation if this 404s."""
    import urllib.request
    api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("Set GEMINI_API_KEY to use `generate` (or just use Flow + `process`).")
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
           f"?key={api_key}")
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                       "generationConfig": {"responseModalities": ["IMAGE"]}}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            Path(out_path).write_bytes(base64.b64decode(inline["data"]))
            return out_path
    raise RuntimeError(f"No image in response: {json.dumps(data)[:300]}")


# ─────────────────────────────────────────────────────────────────────────────
# Manifest patching
# ─────────────────────────────────────────────────────────────────────────────
MANIFEST_RE = re.compile(r"(const\s+assetManifest\s*=\s*\{)(.*?)(\};)", re.S)
TRAFFIC_RE = re.compile(r"(const\s+trafficAssetKeys\s*=\s*\[)([^\]]*)(\])")


def patch_manifest(html, key, value):
    """Replace manifest[key] = value, or insert the key if new. value is a data: URI or path.
    If key matches trafficCarN, also register it in trafficAssetKeys. Returns new html."""
    m = MANIFEST_RE.search(html)
    if not m:
        raise SystemExit("Could not find `const assetManifest = { … };` in the HTML.")
    head, block, tail = m.group(1), m.group(2), m.group(3)

    kv_re = re.compile(rf"(\b{re.escape(key)}\s*:\s*)'[^']*'")
    if kv_re.search(block):
        block = kv_re.sub(lambda mm: mm.group(1) + f"'{value}'", block, count=1)
    else:
        sep = "" if block.strip().endswith(",") or not block.strip() else ","
        block = block.rstrip() + f"{sep}\n  {key}: '{value}'\n"
        print(f"    + new manifest key: {key}")

    html = html[:m.start()] + head + block + tail + html[m.end():]

    if re.fullmatch(r"trafficCar\d+", key):
        tm = TRAFFIC_RE.search(html)
        if tm and f"'{key}'" not in tm.group(2):
            items = [s.strip() for s in tm.group(2).split(",") if s.strip()]
            items.append(f"'{key}'")
            html = html[:tm.start()] + tm.group(1) + ",".join(items) + tm.group(3) + html[tm.end():]
            print(f"    + registered {key} in trafficAssetKeys")
    return html


# ─────────────────────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────────────────────
def _key_rgb(name):
    if not name:
        return None
    if name.lower() in NAMED_KEYS:
        return NAMED_KEYS[name.lower()]
    s = name.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def process_one(src, dst, key=None, tol=0.18, feather=1.5, despill=True):
    img = Image.open(src)
    # If the input already has real transparency (re-run, or an alpha PNG from Drive),
    # trust it and skip chroma-key so we don't damage clean edges.
    pre_alpha = False
    if "A" in img.getbands():
        a = np.asarray(img.convert("RGBA"))[..., 3]
        pre_alpha = (a < 16).mean() > 0.05
    if pre_alpha:
        keyed, used = img.convert("RGBA"), "pre-keyed"
    else:
        keyed, used = chroma_key(img, _key_rgb(key), tol, feather, despill)
    sprite = fit_canvas(autocrop(keyed))
    data = compress_png(sprite)
    Path(dst).write_bytes(data)
    cov = (np.asarray(sprite)[..., 3] > 16).mean() * 100
    print(f"  {Path(src).name} -> {Path(dst).name}  key={used}  {len(data)//1024} KB  fill={cov:.0f}%")
    return data


def cmd_process(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in Path(a.inp).iterdir()
                   if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"))
    if not files:
        sys.exit(f"No images in {a.inp}")
    for f in files:
        process_one(f, out / (f.stem + ".png"), a.key, a.tol, a.feather, not a.no_despill)
    print(f"✓ {len(files)} sprite(s) -> {out}")


def cmd_slice(a):
    """One image holding several subjects on a flat key background -> N sprites.
    Finds each subject by connected-component detection, so it works on a neat grid
    OR a loosely scattered layout (the AI never aligns to a real grid anyway)."""
    if not HAVE_SCIPY:
        sys.exit("`slice` needs scipy:  pip install scipy")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.glow:                                  # bright-on-black FX: alpha = brightness
        rgb = np.asarray(Image.open(a.inp).convert("RGB")).astype(np.float32)
        lum = rgb.max(axis=2)
        keyed = Image.fromarray(np.dstack([rgb, lum]).astype(np.uint8), "RGBA")
        used = "glow(luminance-alpha)"
        mask = lum > a.glow_thresh
    else:
        keyed, used = chroma_key(Image.open(a.inp), _key_rgb(a.key), a.tol, a.feather, not a.no_despill)
        mask = np.asarray(keyed)[..., 3] > 32
    seeds = ndimage.binary_erosion(mask, iterations=a.erode) if a.erode > 0 else mask
    lbl, n = ndimage.label(seeds)
    H, W = mask.shape
    min_px = a.min_area / 100.0 * H * W

    blobs = []
    for i in range(1, n + 1):
        ys, xs = np.where(lbl == i)
        if len(xs) < min_px:
            continue
        pad = a.erode + 2
        box = (max(0, xs.min() - pad), max(0, ys.min() - pad),
               min(W, xs.max() + 1 + pad), min(H, ys.max() + 1 + pad))
        blobs.append(((box[1] + box[3]) / 2, (box[0] + box[2]) / 2, box))
    if not blobs:
        sys.exit("No subjects found — wrong --key, or lower --min-area / --erode.")

    row_h = float(np.median([b[2][3] - b[2][1] for b in blobs]))
    blobs.sort(key=lambda b: (round(b[0] / max(row_h, 1)), b[1]))  # top→bottom, left→right
    for idx, (_, _, box) in enumerate(blobs, 1):
        sprite = fit_canvas(autocrop(keyed.crop(box)))
        data = compress_png(sprite)
        (out / f"{a.prefix}_{idx:02d}.png").write_bytes(data)
        print(f"  {a.prefix}_{idx:02d}  bbox={box}  {len(data)//1024} KB")
    print(f"✓ sliced {len(blobs)} sprite(s) from {Path(a.inp).name}  (key={used}) -> {out}")
    print("  Rename them to the manifest keys, then run `integrate`.")


def _resolve_map(files, explicit):
    """Build {sprite_path: manifest_key} from --map or the default filename map."""
    out = {}
    overrides = dict(s.split(":", 1) for s in (explicit or []))
    for f in files:
        key = overrides.get(f.name) or overrides.get(f.stem) or DEFAULT_MAP.get(f.stem)
        if key:
            out[f] = key
        else:
            print(f"  · skipping {f.name} (no manifest key — pass --map {f.name}:someKey)")
    return out


def cmd_integrate(a):
    html_path = Path(a.html)
    html = html_path.read_text(encoding="utf-8")
    files = sorted(p for p in Path(a.inp).iterdir() if p.suffix.lower() == ".png")
    mapping = _resolve_map(files, a.map)
    if not mapping:
        sys.exit("Nothing to integrate (no filename matched a manifest key).")

    shutil.copy(html_path, html_path.with_suffix(html_path.suffix + ".bak"))
    if a.mode == "files":
        assets = Path(a.assets_dir); assets.mkdir(parents=True, exist_ok=True)

    for f, key in mapping.items():
        if a.mode == "inline":
            uri = "data:image/png;base64," + base64.b64encode(f.read_bytes()).decode()
            html = patch_manifest(html, key, uri)
            print(f"  inline  {f.name} -> {key}")
        else:
            dest = Path(a.assets_dir) / f.name
            shutil.copy(f, dest)
            html = patch_manifest(html, key, str(dest).replace("\\", "/"))
            print(f"  file    {f.name} -> {dest} -> {key}")

    if not MANIFEST_RE.search(html):
        sys.exit("Refusing to write: manifest block went missing. Restored nothing; check .bak")
    html_path.write_text(html, encoding="utf-8")
    print(f"✓ patched {html_path}  (backup: {html_path.name}.bak)")
    print("  Next: open the game, confirm sprites render + procedural fallback still works, run the smoke check.")


def cmd_generate(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    prompts = json.loads(Path(a.prompts).read_text(encoding="utf-8"))
    for item in prompts:
        name = item["name"]
        print(f"  generating {name} …")
        gemini_generate(item["prompt"], out / f"{name}.png", a.model, a.api_key)
    print(f"✓ {len(prompts)} render(s) -> {out}  (now: process, then integrate)")


def cmd_pipeline(a):
    cmd_process(a)
    a.inp = a.out
    cmd_integrate(a)


# ─────────────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Octane asset pipeline")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="prompts.json -> Gemini image API -> raw PNGs")
    g.add_argument("--prompts", required=True)
    g.add_argument("--out", default="raw")
    g.add_argument("--model", default="gemini-2.5-flash-image")
    g.add_argument("--api-key", default=None)
    g.set_defaults(func=cmd_generate)

    p = sub.add_parser("process", help="raw PNGs -> 64x128 transparent sprites")
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--out", default="sprites")
    p.add_argument("--key", default=None, help="magenta|green|#RRGGBB (default: auto from corners)")
    p.add_argument("--tol", type=float, default=0.18, help="key color tolerance 0..1")
    p.add_argument("--feather", type=float, default=1.5, help="edge softness in px")
    p.add_argument("--no-despill", action="store_true")
    p.set_defaults(func=cmd_process)

    sl = sub.add_parser("slice", help="one multi-subject sheet -> individual sprites")
    sl.add_argument("--in", dest="inp", required=True, help="path to the sheet image")
    sl.add_argument("--out", default="sprites")
    sl.add_argument("--key", default=None, help="magenta|green|#RRGGBB (default: auto)")
    sl.add_argument("--tol", type=float, default=0.18)
    sl.add_argument("--erode", type=int, default=1, help="pixels to shrink before splitting touching items")
    sl.add_argument("--min-area", type=float, default=0.3, help="ignore blobs below this %% of the image")
    sl.add_argument("--prefix", default="cell")
    sl.add_argument("--feather", type=float, default=1.5)
    sl.add_argument("--no-despill", action="store_true")
    sl.add_argument("--glow", action="store_true", help="bright-on-black FX: alpha from brightness (screen/additive)")
    sl.add_argument("--glow-thresh", type=float, default=24, help="brightness cutoff for --glow blob detection")
    sl.set_defaults(func=cmd_slice)

    i = sub.add_parser("integrate", help="sprites -> patch assetManifest")
    i.add_argument("--in", dest="inp", required=True)
    i.add_argument("--html", default="index.html")
    i.add_argument("--mode", choices=["inline", "files"], default="inline")
    i.add_argument("--assets-dir", default="assets/cars")
    i.add_argument("--map", nargs="*", help="override: name.png:manifestKey …")
    i.set_defaults(func=cmd_integrate)

    pl = sub.add_parser("pipeline", help="process + integrate")
    pl.add_argument("--in", dest="inp", required=True)
    pl.add_argument("--out", default="sprites")
    pl.add_argument("--key", default=None); pl.add_argument("--tol", type=float, default=0.18)
    pl.add_argument("--feather", type=float, default=1.5); pl.add_argument("--no-despill", action="store_true")
    pl.add_argument("--html", default="index.html")
    pl.add_argument("--mode", choices=["inline", "files"], default="inline")
    pl.add_argument("--assets-dir", default="assets/cars")
    pl.add_argument("--map", nargs="*")
    pl.set_defaults(func=cmd_pipeline)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
