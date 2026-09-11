#!/usr/bin/env python3
"""Produce Key & Door's five SVG tiles with Python 3.10+ standard library.

The shared contract fixes IDs and viewBox size; palette.json controls the family.
All output is confined to art/. No network, raster tools, or packages are needed.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET


PROJECT = Path(__file__).resolve().parents[1]
ART = PROJECT / "art"
NS = "http://www.w3.org/2000/svg"
COLORS = (
    "ink", "floor", "floor_line", "wall", "wall_light", "wall_dark",
    "player", "player_light", "face", "gold", "gold_light", "wood", "wood_light",
)
RANGES = {
    "outline": (1.0, 2.0),
    "wall_corner": (2.0, 5.0),
    "player_scale": (0.85, 1.0),
    "key_angle": (-45.0, 0.0),
}
TITLES = {
    "floor": "Stone floor",
    "wall": "Moss stone wall",
    "player": "Teal adventurer",
    "key": "Gold key",
    "exit": "Arched exit door",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(PROJECT).as_posix()


def load_parameters(path: Path) -> tuple[dict, dict]:
    config = json.loads(path.read_text(encoding="utf-8"))
    palette = config["palette"]
    geometry = config["geometry"]
    for name in COLORS:
        if not isinstance(palette.get(name), str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", palette[name]):
            raise ValueError(f"palette.{name} must be a six-digit hex color")
    for name, (low, high) in RANGES.items():
        value = geometry.get(name)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high:
            raise ValueError(f"geometry.{name} must be between {low} and {high}")
    return palette, geometry


def make_assets(p: dict, g: dict) -> dict[str, str]:
    ink, outline = p["ink"], g["outline"]
    common = f'stroke="{ink}" stroke-width="{outline:g}" stroke-linejoin="round" stroke-linecap="round"'
    scale = g["player_scale"]
    offset = 16 * (1 - scale)
    bodies = {
        "floor": f'''
  <rect width="32" height="32" fill="{p['floor']}"/>
  <path d="M0.5 32V0.5H32 M5 8H10 M24 26H28" fill="none" stroke="{p['floor_line']}" stroke-width="1"/>
''',
        "wall": f'''
  <rect x="1.5" y="3.5" width="29" height="27" rx="{g['wall_corner']:g}" fill="{p['wall_dark']}"/>
  <rect x="1.5" y="1.5" width="29" height="26" rx="{g['wall_corner']:g}" fill="{p['wall']}" {common}/>
  <path d="M5 6H27" fill="none" stroke="{p['wall_light']}" stroke-width="2" stroke-linecap="round"/>
  <path d="M2.5 15.5H29.5 M16 2.5V15.5 M9 15.5V27 M24 15.5V27" fill="none" stroke="{p['wall_dark']}" stroke-width="1.5"/>
''',
        "player": f'''
  <ellipse cx="16" cy="28" rx="10" ry="2" fill="{ink}" opacity="0.15"/>
  <g transform="translate({offset:g} {offset:g}) scale({scale:g})" {common}>
    <path d="M10 24V28H14V25 M18 25V28H22V24" fill="{ink}"/>
    <path d="M10 18Q16 14 22 18L24 25Q16 29 8 25Z" fill="{p['player']}"/>
    <path d="M16 18V26" fill="none" stroke="{p['player_light']}"/>
    <circle cx="16" cy="10.5" r="7" fill="{p['player']}"/>
    <path d="M10.5 10Q16 7 21.5 10V12Q16 19 10.5 12Z" fill="{p['face']}"/>
    <path d="M12 6.5Q16 4.5 20 6.5" fill="none" stroke="{p['player_light']}"/>
    <circle cx="13.5" cy="11.5" r="0.75" fill="{ink}" stroke="none"/>
    <circle cx="18.5" cy="11.5" r="0.75" fill="{ink}" stroke="none"/>
    <path d="M11 22H21" fill="none"/>
    <rect x="14.5" y="20.5" width="3" height="3" rx="0.5" fill="{p['gold']}"/>
  </g>
''',
        "key": f'''
  <ellipse cx="16" cy="28" rx="10" ry="2" fill="{ink}" opacity="0.12"/>
  <g transform="rotate({g['key_angle']:g} 16 16)" {common}>
    <path d="M13 14H28V20H24V17H21V20H17V18H13Z" fill="{p['gold']}"/>
    <path d="M9 9.5A6.5 6.5 0 1 1 9 22.5A6.5 6.5 0 1 1 9 9.5Z M9 13.3A2.7 2.7 0 1 0 9 18.7A2.7 2.7 0 1 0 9 13.3Z" fill="{p['gold']}" fill-rule="evenodd"/>
    <path d="M5.5 13Q7 11 9 11 M17 15.2H26.5" fill="none" stroke="{p['gold_light']}" stroke-width="1"/>
  </g>
''',
        "exit": f'''
  <path d="M4.5 29.5V13A11.5 11.5 0 0 1 27.5 13V29.5Z" fill="{p['wall_light']}" {common}/>
  <path d="M8 29V14A8 8 0 0 1 24 14V29Z" fill="{p['wood']}" {common}/>
  <path d="M16 7V28 M11 13V27 M21 13V27" fill="none" stroke="{p['wood_light']}" stroke-width="1"/>
  <path d="M10 12Q16 5.5 22 12" fill="none" stroke="{p['wood_light']}" stroke-width="1.5"/>
  <path d="M4.5 29.5H27.5" fill="none" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>
  <circle cx="18.5" cy="19" r="2.2" fill="{p['gold']}" stroke="{ink}" stroke-width="1"/>
  <path d="M18.5 18A0.9 0.9 0 1 1 18.5 19.8L19.3 22H17.7L18.5 19.8A0.9 0.9 0 0 1 18.5 18Z" fill="{ink}"/>
  <path d="M15 3H17" fill="none" stroke="{p['gold_light']}" stroke-width="1.5" stroke-linecap="round"/>
''',
    }
    return {
        name: f'<svg xmlns="{NS}" width="32" height="32" viewBox="0 0 32 32" role="img">\n  <title>{TITLES[name]}</title>\n{body}</svg>\n'
        for name, body in bodies.items()
    }


def check_svg(name: str, text: str) -> None:
    root = ET.fromstring(text)
    if root.tag != f"{{{NS}}}svg" or root.get("viewBox") != "0 0 32 32":
        raise ValueError(f"{name}: expected SVG with a 0 0 32 32 viewBox")
    if root.get("width") != "32" or root.get("height") != "32":
        raise ValueError(f"{name}: width and height must be 32")
    if root.find(f"{{{NS}}}path") is None and root.find(f"{{{NS}}}g") is None:
        raise ValueError(f"{name}: drawing geometry is missing")
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] in {"script", "image", "foreignObject", "use"}:
            raise ValueError(f"{name}: SVG must contain only its own vector drawing")
        for attribute, value in element.attrib.items():
            if attribute.rsplit("}", 1)[-1] in {"href", "src"} or "url(" in value:
                raise ValueError(f"{name}: external/referenced content is not allowed")


def tile(svg: str, x: int, y: int, size: int) -> str:
    body = svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
    return f'<g transform="translate({x} {y}) scale({size / 32:g})">{body}</g>'


def make_preview(output: Path, ids: list[str], level_path: Path | None) -> tuple[str, dict | None]:
    # Read the produced assets: this preview is an actual downstream consumer.
    assets = {name: (output / f"{name}.svg").read_text(encoding="utf-8") for name in ids}
    parts = [f'<svg xmlns="{NS}" width="760" height="650" viewBox="0 0 760 650">',
             '<rect width="760" height="650" fill="#F7F6EE"/>',
             '<g font-family="sans-serif" fill="#203C39">',
             '<text x="32" y="38" font-size="22" font-weight="bold">KEY &amp; DOOR</text>',
             '<text x="32" y="64" font-size="13">Generated vector family · 32 × 32 logical pixels · no external assets</text>']
    for i, name in enumerate(ids):
        x = 40 + i * 144
        parts.append(tile(assets["floor"], x, 91, 80))
        if name != "floor":
            parts.append(tile(assets[name], x, 91, 80))
        parts.append(f'<text x="{x}" y="195" font-size="14" font-weight="bold">{html.escape(name)}</text>')
        parts.append(tile(assets["floor"], x, 213, 32))
        if name != "floor":
            parts.append(tile(assets[name], x, 213, 32))
    parts.append('<text x="32" y="273" font-size="12">Top: 2.5× inspection. Bottom: native 32px tiles, composited over floor.</text>')
    level = None
    if level_path is not None:
        level = json.loads(level_path.read_text(encoding="utf-8"))
        parts.append('<text x="32" y="313" font-size="14" font-weight="bold">Produced level · native 32px</text>')
        parts.append('<text x="300" y="313" font-size="14" font-weight="bold">Same level · 56px display tiles</text>')
        walls = set(map(tuple, level["walls"]))
        for size, origin_x in [(32, 32), (56, 300)]:
            for y in range(level["height"]):
                for x in range(level["width"]):
                    px, py = origin_x + x * size, 334 + y * size
                    parts.append(tile(assets["floor"], px, py, size))
                    if (x, y) in walls:
                        parts.append(tile(assets["wall"], px, py, size))
                    for name in ["exit", "key", "player"]:
                        if [x, y] == level[name]:
                            parts.append(tile(assets[name], px, py, size))
        parts.append(f'<text x="32" y="642" font-size="11">Level source: {html.escape(relative(level_path))}. This is an art preview; gameplay integration is separate.</text>')
    else:
        parts.append('<text x="32" y="330" font-size="14">Level output was not available at generation time.</text>')
        parts.append('<text x="32" y="353" font-size="13">Rerun after design/generated/level.json is present to inspect the produced room.</text>')
    parts.append('</g></svg>\n')
    return "\n".join(parts), level


def run(args: argparse.Namespace) -> dict:
    output = args.output.resolve()
    if not output.is_relative_to(ART):
        raise ValueError("output must remain within this project's art/ directory")
    contract_path = PROJECT / "studio/game-contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    ids = contract["art"]["ids"]
    if set(ids) != set(TITLES) or len(ids) != len(TITLES):
        raise ValueError("contract asset IDs differ from this five-asset generator")
    if contract["art"]["manifest_format"]["tile_size"] != 32:
        raise ValueError("this tool implements the contracted 32px tile family")
    p, g = load_parameters(args.palette)
    assets = make_assets(p, g)
    for name in ids:
        check_svg(name, assets[name])
    output.mkdir(parents=True, exist_ok=True)
    for name in ids:
        (output / f"{name}.svg").write_text(assets[name], encoding="utf-8", newline="\n")
    manifest = {"tile_size": 32, "assets": {name: relative(output / f"{name}.svg") for name in ids}}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    level_path = args.level
    if level_path is None and (PROJECT / "design/generated/level.json").exists():
        level_path = PROJECT / "design/generated/level.json"
    preview, _ = make_preview(output, ids, level_path)
    (output / "preview.svg").write_text(preview, encoding="utf-8", newline="\n")
    output_paths = [output / f"{name}.svg" for name in ids] + [output / "manifest.json", output / "preview.svg"]
    report = {
        "schema": 1,
        "producer": "art/generate_assets.py",
        "source_sha256": {relative(Path(__file__)): digest(Path(__file__)), relative(args.palette): digest(args.palette), relative(contract_path): digest(contract_path)},
        "parameters": {"palette": p, "geometry": g},
        "randomness": "none; output is deterministic for identical input bytes",
        "preview_level": None if level_path is None else {"path": relative(level_path), "sha256": digest(level_path)},
        "outputs_sha256": {relative(path): digest(path) for path in output_paths},
        "contract_checks": ["five contracted IDs", "32px width, height and viewBox", "parseable SVG", "no referenced or external content", "project-relative manifest paths"],
    }
    (output / "production.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--palette", type=Path, default=ART / "palette.json")
    parser.add_argument("--output", type=Path, default=ART / "generated")
    parser.add_argument("--level", type=Path, help="Optional produced level JSON; detected automatically when present")
    args = parser.parse_args()
    try:
        report = run(args)
    except (ValueError, KeyError, OSError, ET.ParseError) as error:
        parser.exit(2, f"asset generation failed: {error}\n")
    print(f"Generated {len(TITLES)} SVG assets, manifest and preview in {relative(args.output)}")
    print(f"Preview level: {report['preview_level']['path'] if report['preview_level'] else 'not yet available'}")


if __name__ == "__main__":
    main()
