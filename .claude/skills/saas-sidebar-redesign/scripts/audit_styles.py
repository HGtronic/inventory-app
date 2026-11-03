#!/usr/bin/env python3
"""Audit a Vue/CSS source tree for spacing, color and layout-coupling issues.

Usage:
    python3 audit_styles.py <src-dir> [--json]

Reports:
  1. Spacing values (padding/margin/gap/inset) that are not on a 4px scale and
     are not CSS variables. These are the inconsistencies a token system fixes.
  2. Hardcoded colors by frequency. Useful for deriving tokens from the
     existing palette, and for checking how many remain after migration.
  3. Lines likely coupled to the old header's height (sticky/fixed offsets,
     100vh calcs, scroll-margin). These break when the nav moves.
  4. z-index values, so the stacking order (sidebar < overlay < modal) can be checked.

Stdlib only. Only <style> blocks of .vue files and .css/.scss files are scanned.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Matches declarations anywhere on a line, so one-line rules like
# `.card { padding: 18px; margin: 0 }` are counted too. The leading boundary
# keeps `top` from matching inside `margin-top` (that is caught as margin-top).
SPACING_PROPS = re.compile(
    r"(?:^|[;{\s])(padding|margin|gap|row-gap|column-gap|inset|top|right|bottom|left)"
    r"(-(top|right|bottom|left|inline|block)(-(start|end))?)?\s*:\s*([^;}]+)",
    re.I,
)
LENGTH = re.compile(r"(-?\d*\.?\d+)(px|rem|em)\b")
COLOR = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b|rgba?\([^)]*\)")
COUPLING = re.compile(
    r"(position\s*:\s*(sticky|fixed))|((?:^|[;{\s])top\s*:\s*\d+(\.\d+)?(px|rem))|"
    r"(calc\(\s*100vh\s*-)|(scroll-margin-top)|(scroll-padding-top)",
    re.I,
)
ZINDEX = re.compile(r"z-index\s*:\s*(-?\d+)", re.I)
STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)


def to_px(value, unit):
    v = float(value)
    return v * 16 if unit in ("rem", "em") else v


def on_scale(px):
    # 0, 1px and 2px are fine (hairlines, borders); otherwise require multiples of 4
    return px in (0, 1, 2) or abs(px / 4 - round(px / 4)) < 1e-6


def style_lines(path):
    """Yield (line_number, line) for CSS content only."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".vue":
        for m in STYLE_BLOCK.finditer(text):
            start_line = text[: m.start(1)].count("\n") + 1
            for i, line in enumerate(m.group(1).split("\n")):
                yield start_line + i, line
    else:
        for i, line in enumerate(text.split("\n"), 1):
            yield i, line


def audit(src):
    src = Path(src)
    files = [p for p in src.rglob("*") if p.suffix in (".vue", ".css", ".scss")
             and "node_modules" not in p.parts and "dist" not in p.parts]
    off_scale = defaultdict(list)       # value -> [file:line]
    spacing_total = 0
    spacing_tokenized = 0
    colors = Counter()
    color_files = defaultdict(set)
    coupling = []
    zindex = []

    for f in sorted(files):
        rel = f.relative_to(src)
        for ln, line in style_lines(f):
            for m in SPACING_PROPS.finditer(line):
                if "--" in line[: m.start(1)].split(";")[-1]:
                    continue  # part of a custom property definition
                spacing_total += 1
                val = m.group(6)
                if "var(" in val:
                    spacing_tokenized += 1
                for num, unit in LENGTH.findall(val):
                    px = to_px(num, unit)
                    if not on_scale(abs(px)):
                        off_scale[f"{num}{unit}"].append(f"{rel}:{ln}")
            for c in COLOR.findall(line):
                if "--" in line.split(":")[0]:
                    continue  # token definitions themselves
                key = c.lower().replace(" ", "")
                colors[key] += 1
                color_files[key].add(str(rel))
            if COUPLING.search(line):
                coupling.append(f"{rel}:{ln}: {line.strip()}")
            z = ZINDEX.search(line)
            if z:
                zindex.append((int(z.group(1)), f"{rel}:{ln}"))

    return {
        "files_scanned": len(files),
        "spacing_declarations": spacing_total,
        "spacing_using_tokens": spacing_tokenized,
        "off_scale_spacing": {k: v for k, v in sorted(off_scale.items(), key=lambda kv: -len(kv[1]))},
        "off_scale_count": sum(len(v) for v in off_scale.values()),
        "hardcoded_colors": [
            {"color": c, "count": n, "files": len(color_files[c])} for c, n in colors.most_common()
        ],
        "hardcoded_color_count": sum(colors.values()),
        "layout_coupling": coupling,
        "z_index": sorted(zindex),
    }


def print_report(r):
    print(f"Scanned {r['files_scanned']} style sources\n")
    print(f"== Spacing: {r['spacing_using_tokens']}/{r['spacing_declarations']} declarations use tokens; "
          f"{r['off_scale_count']} off-4px-scale values ==")
    for val, locs in list(r["off_scale_spacing"].items())[:20]:
        print(f"  {val:>10}  x{len(locs):<3} e.g. {', '.join(locs[:3])}")
    print(f"\n== Hardcoded colors: {r['hardcoded_color_count']} uses, {len(r['hardcoded_colors'])} distinct ==")
    for c in r["hardcoded_colors"][:25]:
        print(f"  {c['color']:<28} x{c['count']:<4} in {c['files']} file(s)")
    print(f"\n== Possible header-height coupling ({len(r['layout_coupling'])}) ==")
    for line in r["layout_coupling"]:
        print(f"  {line}")
    print(f"\n== z-index values ({len(r['z_index'])}) ==")
    for z, loc in r["z_index"]:
        print(f"  {z:>6}  {loc}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    result = audit(sys.argv[1])
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)
