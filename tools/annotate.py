#!/usr/bin/env python3
"""Draw numbered call-outs on a raw screenshot, from a JSON spec.

Why this exists
---------------
The docs box elements and number them (1, 2, 3…) so prose can say "click (2)". Painting
those by hand in an image editor means that the day BMM's UI moves a button, nobody can
update the picture — they'd have to re-paint it, so in practice it rots and the docs start
lying. Here the annotation is *text*: a JSON file next to the raw capture, versioned,
reviewable in a diff, and re-rendered on every build. Retake the screenshot, keep the spec.

It also keeps the numbering honest across languages: one spec drives both the EN and FR
pages, so (2) is the same box in both — the prose is translated, the picture isn't duplicated.

Spec format (docs/assets/screens/<name>.json)
---------------------------------------------
{
  "image": "library.png",           // raw capture, same folder
  "scale": 1,                       // optional: source is a HiDPI capture (2 = retina)
  "boxes": [
    {"n": 1, "xy": [40, 96, 320, 140], "label": "Search"},   // [x1,y1,x2,y2] in image px
    {"n": 2, "xy": [340, 96, 420, 140]}
  ]
}

Usage
-----
  python tools/annotate.py                       # render every spec under docs/assets/screens
  python tools/annotate.py docs/assets/screens/library.json
  python tools/annotate.py --check               # CI: fail if any output is stale/missing

Output: <name>.annotated.png next to the source. Pages reference the annotated file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required:  pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parent.parent
SCREENS = ROOT / "docs" / "assets" / "screens"

# BMM's brand orange. High contrast on both its dark UI and a light one, and the badge text
# is white on that orange (4.5:1+), so a call-out is readable in a printed PDF too.
ACCENT = (249, 115, 22, 255)
BADGE_TEXT = (255, 255, 255, 255)
HALO = (0, 0, 0, 90)  # a dark halo under the box, so the orange survives a light background


def _font(size: int):
    for name in ("segoeuib.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render(spec_path: Path) -> Path:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    src = spec_path.parent / spec["image"]
    if not src.exists():
        raise FileNotFoundError(f"{spec_path.name}: image not found: {src}")

    img = Image.open(src).convert("RGBA")
    scale = float(spec.get("scale", 1) or 1)
    # Sizes follow the image, so a 4K capture doesn't get hairline boxes and a 720p one
    # doesn't get a badge covering the button it points at.
    unit = max(img.width, img.height) / 1000.0
    width = max(2, round(3 * unit))
    radius = max(4, round(6 * unit))
    badge_r = max(11, round(15 * unit))
    font = _font(max(11, round(19 * unit)))

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    for box in spec.get("boxes", []):
        x1, y1, x2, y2 = (round(v * scale) for v in box["xy"])
        d.rounded_rectangle([x1 - 1, y1 - 1, x2 + 1, y2 + 1], radius=radius,
                            outline=HALO, width=width + 2)
        d.rounded_rectangle([x1, y1, x2, y2], radius=radius, outline=ACCENT, width=width)

        # Badge on the top-left corner, nudged inside if the box hugs the image edge.
        cx = max(badge_r, min(x1, img.width - badge_r))
        cy = max(badge_r, min(y1, img.height - badge_r))
        d.ellipse([cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r],
                  fill=ACCENT, outline=(0, 0, 0, 120), width=max(1, round(unit)))
        n = str(box["n"])
        tb = d.textbbox((0, 0), n, font=font)
        d.text((cx - (tb[2] - tb[0]) / 2 - tb[0], cy - (tb[3] - tb[1]) / 2 - tb[1]),
               n, font=font, fill=BADGE_TEXT)

    out = src.with_suffix("")
    out = out.parent / f"{out.name}.annotated.png"
    Image.alpha_composite(img, overlay).save(out)
    _save_stamp(out.name, _fingerprint(spec_path, src))
    return out


# ── Staleness, without mtimes ──────────────────────────────────────────────────────────
#
# `--check` used to compare modification times. That cannot work in CI: git does not
# preserve mtimes, so a fresh checkout stamps everything at clone time in write order — and
# `x.annotated.png` sorts BEFORE `x.json`, so the output is written first and looks older
# than its own spec. Reproduced exactly: the check passes locally and fails on the runner.
#
# Comparing the RENDERED bytes instead would fail for a different reason — _font() picks
# segoeuib.ttf on Windows and DejaVuSans-Bold.ttf on Linux, so the same spec renders
# different pixels on the two machines.
#
# So the fingerprint is of the INPUTS: the spec and its source image. That is exactly the
# question the gate asks — "was this re-rendered after the spec or the screenshot changed?"
# — and it is identical on every platform.
STAMPS = SCREENS / ".annotations.json"


def _fingerprint(spec_path: Path, src: Path) -> str:
    # The spec is hashed as PARSED CONTENT, not as raw bytes. With core.autocrlf=true the
    # working copy holds CRLF while the blob holds LF, so the same spec is a different byte
    # string on Windows and on the Linux runner — which is exactly how the first version of
    # this manifest failed: 9 of 10 stale in CI, and the one that passed (library.json) was
    # the one file that happened to be stored with LF.
    #
    # sort_keys so a reordered-but-identical spec doesn't read as a change either.
    h = hashlib.sha256()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    h.update(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    # The screenshot is binary; git leaves it alone, so its bytes are safe to hash directly.
    h.update(src.read_bytes())
    return h.hexdigest()


def _load_stamps() -> dict:
    try:
        return json.loads(STAMPS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save_stamp(out_name: str, digest: str) -> None:
    stamps = _load_stamps()
    stamps[out_name] = digest
    # Sorted so the file has a stable diff rather than reordering on every render.
    STAMPS.write_text(json.dumps(stamps, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Render numbered call-outs from JSON specs.")
    ap.add_argument("specs", nargs="*", type=Path)
    ap.add_argument("--check", action="store_true",
                    help="CI mode: fail if an annotated image is missing or older than its spec/source")
    args = ap.parse_args()

    # pathlib's glob matches dotfiles, so the stamps file would be read as a spec and die on
    # a missing "image" key. Excluded by name rather than moved: keeping it beside the
    # screenshots is what makes it obvious it belongs to them.
    specs = args.specs or sorted(q for q in SCREENS.glob("*.json") if q.name != STAMPS.name)
    stamps = _load_stamps()
    if not specs:
        print(f"no specs found in {SCREENS} — nothing to do")
        return 0

    stale = []
    for s in specs:
        spec = json.loads(s.read_text(encoding="utf-8"))
        src = s.parent / spec["image"]
        out = src.parent / f"{src.with_suffix('').name}.annotated.png"
        if args.check:
            if not out.exists():
                stale.append(out.name)
            elif stamps.get(out.name) != _fingerprint(s, src):
                stale.append(out.name)
            continue
        print(f"  {s.name} -> {render(s).name}")

    if args.check and stale:
        print("stale or missing annotations: " + ", ".join(stale))
        print("run:  python tools/annotate.py")
        return 1
    print("annotate: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
