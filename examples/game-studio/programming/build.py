"""Embed the real designed level and generated SVG family into one offline HTML."""
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project_path(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Path must be inside this project: {relative}")
    return path


def build(output, evidence_path):
    contract_path = ROOT / "studio/game-contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    world = json.loads((ROOT / "studio/world.json").read_text(encoding="utf-8"))
    level_path = project_path(contract["gameplay"]["level_path"])
    level = json.loads(level_path.read_text(encoding="utf-8"))

    # The design producer owns level semantics. Reuse its validator, not a second
    # hard-coded set of dimensions or copied coordinates in the runtime.
    design_path = ROOT / "design/level_tool.py"
    spec = importlib.util.spec_from_file_location("studio_design_level", design_path)
    design = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(design)
    proof = design.validate_level(level, contract)
    manifest_path = project_path(contract["art"]["manifest_path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    tile_size = contract["art"]["manifest_format"]["tile_size"]
    if manifest["tile_size"] != tile_size or set(manifest["assets"]) != set(contract["art"]["ids"]):
        raise ValueError("Art manifest IDs or tile size disagree with the shared contract.")

    consumed = [contract_path, ROOT / "studio/world.json", level_path, design_path, manifest_path,
                ROOT / "programming/build.py", ROOT / "programming/page.html", ROOT / "programming/runtime.js"]
    assets = {}
    for asset_id in contract["art"]["ids"]:
        path = project_path(manifest["assets"][asset_id])
        raw = path.read_bytes()
        svg = ET.fromstring(raw)
        if (svg.tag.rsplit("}", 1)[-1] != "svg" or svg.get("viewBox") != f"0 0 {tile_size} {tile_size}"
                or svg.get("width") != str(tile_size) or svg.get("height") != str(tile_size)):
            raise ValueError(f"Asset {asset_id} does not have the contracted SVG dimensions.")
        assets[asset_id] = "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")
        consumed.append(path)

    def image(asset_id, extra=""):
        return f'<img data-asset="{asset_id}" src="{assets[asset_id]}" alt="" draggable="false" {extra}>'

    walls = {tuple(cell) for cell in level["walls"]}
    cells = []
    for y in range(level["height"]):
        for x in range(level["width"]):
            foreground = image("wall") if (x, y) in walls else ""
            cells.append('<div class="tile">' + image("floor") + foreground + '</div>')
    # All overlays share top-left origin. Player is last so it stays on top at win.
    for entity in ("key", "exit", "player"):
        x, y = level[entity]
        position = f'left:{x / level["width"] * 100:g}%;top:{y / level["height"] * 100:g}%'
        cells.append(image(entity, f'id="{entity}" class="entity" style="{position}"'))
    runtime = (ROOT / "programming/runtime.js").read_text(encoding="utf-8")
    values = {"WIDTH":str(level["width"]), "HEIGHT":str(level["height"]),
              "LEVEL_DATA":json.dumps(level, separators=(",", ":")).replace("<", "\\u003c"),
              "BOARD":"\n".join(cells), "GAME_RUNTIME":runtime}
    html = (ROOT / "programming/page.html").read_text(encoding="utf-8")
    for name, value in values.items():
        html = html.replace("{{" + name + "}}", value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    report = {"schema":1, "producer":"programming/build.py", "project_id":world["project_id"],
              "revision":world["revision"], "parameters":{"seed":None, "art_encoding":"exact SVG bytes as base64 data URIs"},
              "consumed_sha256":{p.relative_to(ROOT).as_posix():digest(p) for p in consumed},
              "output":{"path":output.relative_to(ROOT).as_posix(), "sha256":digest(output), "bytes":output.stat().st_size},
              "consumer_checks":{"design_validator":proof["accepted"], "solution_steps":proof["total_steps"],
                                 "svg_ids":list(assets), "svg_dimensions":tile_size},
              "boundary":"Importer and emitted bytes verified here; runtime replay is recorded separately."}
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Built {output.relative_to(ROOT)} ({output.stat().st_size} bytes); consumed level and {len(assets)} SVG assets.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="index.html")
    parser.add_argument("--evidence", default="programming/generated/build-evidence.json")
    args = parser.parse_args()
    try:
        build(project_path(args.output), project_path(args.evidence))
        return 0
    except (OSError, ValueError, KeyError, ET.ParseError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
