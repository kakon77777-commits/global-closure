#!/usr/bin/env python3
"""Run bounded art-contract and parameter witnesses; save the observed evidence."""

import json
from pathlib import Path
import xml.etree.ElementTree as ET

import generate_assets as gen


def main() -> None:
    project = gen.PROJECT
    output = project / "art/generated"
    contract = json.loads((project / "studio/game-contract.json").read_text(encoding="utf-8"))
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    production = json.loads((output / "production.json").read_text(encoding="utf-8"))
    assert list(manifest["assets"]) == contract["art"]["ids"], "manifest IDs differ from contract"
    assert manifest["tile_size"] == 32, "manifest tile size differs from contract"
    for path, expected in {**production["source_sha256"], **production["outputs_sha256"]}.items():
        assert gen.digest(project / path) == expected, f"production hash mismatch: {path}"

    palette, geometry = gen.load_parameters(project / "art/palette.json")
    assets = gen.make_assets(palette, geometry)
    assert assets == gen.make_assets(palette, geometry), "asset generation is nondeterministic"
    for name, path in manifest["assets"].items():
        svg = (project / path).read_text(encoding="utf-8")
        gen.check_svg(name, svg)
        assert svg == assets[name], f"{name}: disk output differs from regenerated drawing"

    # A different authorized palette is valid and must affect the intended asset.
    alternative = gen.make_assets({**palette, "player": "#3366BB"}, geometry)
    assert {name for name in assets if alternative[name] != assets[name]} == {"player"}
    for name, svg in alternative.items():
        gen.check_svg(name, svg)

    rejected = {}
    mutants = {
        "wrong_viewbox": ("player", assets["player"].replace('viewBox="0 0 32 32"', 'viewBox="0 0 64 32"')),
        "linked_raster": ("key", assets["key"].replace("</svg>", '<image href="https://example.invalid/key.png"/></svg>')),
    }
    for witness, (name, svg) in mutants.items():
        try:
            gen.check_svg(name, svg)
        except ValueError as error:
            rejected[witness] = str(error)
        else:
            raise AssertionError(f"falsifying witness was accepted: {witness}")

    level_ref = production["preview_level"]
    level_path = project / level_ref["path"] if level_ref else None
    if level_path:
        assert gen.digest(level_path) == level_ref["sha256"], "preview level changed"
    regenerated_preview, _ = gen.make_preview(output, contract["art"]["ids"], level_path)
    assert regenerated_preview == (output / "preview.svg").read_text(encoding="utf-8")
    ET.fromstring(regenerated_preview)
    evidence = {
        "schema": 1,
        "command": "python art/check_assets.py",
        "observed_context": "/root/studio_art",
        "input_production_sha256": gen.digest(output / "production.json"),
        "positive_witnesses": [
            "Manifest contains all five contracted asset IDs in contract order.",
            "Five SVGs parse, use a 32x32 viewBox and dimensions, and contain no linked content.",
            "Current source, palette, contract and outputs match production hashes.",
            "Regeneration from source and palette reproduces all five SVG files exactly.",
            "Changing only the player color changes only the player asset; all alternatives validate.",
            "Preview is reproduced from the produced SVG files and declared level, and parses as SVG."
        ],
        "falsifying_witnesses": rejected,
        "limits": [
            "These witnesses concern the art producer and files, not runtime gameplay.",
            "In-process regeneration does not establish a clean-machine build or global minimal architecture.",
            "SVG parsing alone does not establish visual quality; visual observations are in the art delivery note."
        ]
    }
    path = project / "art/validation.json"
    path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
