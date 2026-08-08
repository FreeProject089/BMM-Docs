#!/usr/bin/env python3
"""Report which docs media is still a stand-in rather than a real recording.

Why this exists: the pages used to carry the word "placeholder" next to every embed, which
was honest but ugly. Removing it makes the docs *claim* each clip shows what its title says
— so something has to keep that claim true. This does, without failing the build: media is
recorded over time, and a red CI on every unshot clip would just get ignored.

Two things give a stand-in away, and neither needs a human to look:

  Replays  — thirteen files with the same SHA-256 are one recording copied thirteen times.
  Screens  — a 900x420 PNG of a near-uniform dark rectangle is the generated placeholder,
             not a screenshot. Real UI has hundreds of distinct colours; the stand-in has a
             handful.

Run: python tools/check_media.py            (report)
     python tools/check_media.py --strict   (exit 1 if anything is still a stand-in)
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPLAYS = ROOT / "docs" / "assets" / "replays"
SCREENS = ROOT / "docs" / "assets" / "screens"

# Below this many distinct colours, a 900x420 PNG is the empty call-out template rather than
# a captured interface. Measured: the generated placeholders sit in the low tens.
COLOUR_FLOOR = 256


def check_replays() -> list[str]:
    by_hash: dict[str, list[str]] = defaultdict(list)
    for f in sorted(REPLAYS.glob("*.bmmreplay")):
        by_hash[hashlib.sha256(f.read_bytes()).hexdigest()].append(f.name)

    stand_ins = []
    for names in by_hash.values():
        if len(names) > 1:
            stand_ins.extend(names)

    print(f"replays: {sum(len(v) for v in by_hash.values())} file(s), "
          f"{len(by_hash)} distinct recording(s)")
    for digest, names in sorted(by_hash.items(), key=lambda kv: -len(kv[1])):
        if len(names) > 1:
            print(f"  ! {len(names)} identical ({digest[:12]}): {', '.join(names)}")
    return stand_ins


def check_screens() -> list[str]:
    try:
        from PIL import Image
    except ImportError:
        print("screens: skipped (Pillow not installed)")
        return []

    stand_ins = []
    sources = [f for f in sorted(SCREENS.glob("*.png")) if ".annotated" not in f.name]
    for f in sources:
        with Image.open(f) as im:
            colours = im.convert("RGB").getcolors(maxcolors=1 << 20)
            n = len(colours) if colours else 1 << 20
            if n < COLOUR_FLOOR:
                stand_ins.append(f.name)
                print(f"  ! {f.name}: {im.size[0]}x{im.size[1]}, {n} distinct colour(s) "
                      f"— an empty template, not a screenshot")
    print(f"screens: {len(sources)} source(s), {len(stand_ins)} still a template")
    return stand_ins


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when anything is still a stand-in")
    args = ap.parse_args()

    pending = check_replays() + check_screens()

    print()
    if not pending:
        print("every embed points at its own real recording.")
        return 0

    print(f"{len(pending)} media file(s) still to record. "
          f"The shooting list is .Assets/MEDIA_TO_RECORD.md")
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
