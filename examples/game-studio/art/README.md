# Key & Door art

Five generated vector assets share a moss-stone, teal and brass palette. The wall is solid masonry, the player is a round-headed teal adventurer, the key has a ring and teeth, and the exit is an arched wood door. Shape and color both distinguish the three entities.

From the project root on Windows, run:

```powershell
py -3 art/generate_assets.py
```

The tool needs Python 3.10+ and only its standard library. On this build host the equivalent command is `python art/generate_assets.py`. There is no random seed. Edit `art/palette.json` to adjust named colors, outline width (1–2px), wall corner radius (2–5px), player scale (0.85–1), or key angle (−45–0 degrees). The generator rejects unsupported parameter values before writing any output. Asset IDs and 32 × 32 size remain controlled by `studio/game-contract.json`.

The real outputs are `art/generated/{floor,wall,player,key,exit}.svg`; their integration map is `art/generated/manifest.json`. All SVGs have width and height 32 and viewBox `0 0 32 32`. Floor is an opaque base tile. The other four assets have transparent backgrounds. Draw floor first, then the relevant wall or entity, with a shared top-left origin and no pivot offset. The graphics use paths and basic shapes with no linked fonts, images, scripts or external references.

`art/generated/preview.svg` embeds the actual produced SVG files at inspection size and native 32px. When `design/generated/level.json` exists, the generator also lays out that exact level. `art/generated/production.json` pins input parameters, source hashes, level hash when available, and output hashes. `--output` supports comparison builds within `art/`; `--palette` accepts a project-local parameter file, and `--level` accepts a produced level JSON. The default output paths are the integration contract.

Run `py -3 art/check_assets.py` to check the generated files and write `art/validation.json`. This also tries a permitted palette change and confirms that the validator rejects a wrong viewBox and a linked raster. The preview SVG can be opened directly in a browser. The supplied PNG is an inspection rendering made with PyMuPDF on the build host; that package is not required to generate or use the SVG assets.

One exit graphic is deliberate: the runtime should express “find key”, “door ready”, and “won” with its visible status text. Removing the collected key and preserving player visibility on the exit are runtime responsibilities. Actual in-game acceptance belongs to programming after integration; preview acceptance alone does not prove the playable game.
