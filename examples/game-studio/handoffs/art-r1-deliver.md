# Art contribution — revision 1

Source: art architect, host-observed context `/root/studio_art`. Recipient: programming architect, context `/root/studio_programming` reported by the host and observed through its reply. Project: `key-door-studio-demo`, base world revision 1. `studio/world.json` and `studio/game-contract.json` were read; neither was edited by art. No contract change is proposed.

## Delivered tool and actual output

`art/generate_assets.py` is the project-specific parameterized SVG production tool. It uses Python 3.10+ standard library, reads the shared contract and `art/palette.json`, writes the five drawings and manifest, and makes a preview by reading those actual SVG files. The preview also consumes the produced `design/generated/level.json`.

Run from the project root:

```powershell
py -3 art/generate_assets.py
py -3 art/check_assets.py
```

Current shape parameters: outline 1.5px, wall corner radius 3.5px, player scale 0.95, key angle −32 degrees. There is no random seed or nondeterminism. Named palette colors and shape parameters are the repeatable source inputs. Supported ranges and controls are described in `art/README.md`. `art/generated/production.json` pins the source, palette, contract, level and generated output bytes.

| ID | Actual SVG file | Use |
| --- | --- | --- |
| floor | `art/generated/floor.svg` | Opaque 32px stone base |
| wall | `art/generated/wall.svg` | Moss masonry overlay |
| player | `art/generated/player.svg` | Teal adventurer overlay |
| key | `art/generated/key.svg` | Gold ring-and-teeth key overlay |
| exit | `art/generated/exit.svg` | Arched wood door overlay |

All assets have width and height 32, viewBox `0 0 32 32`, common top-left placement, and no external references. Total SVG payload: 3,456 bytes. Use the paths in `art/generated/manifest.json`; draw floor below other assets and player last. One door graphic is intentional under the contract. The runtime supplies visible key possession, door readiness and victory text, and removes the collected key.

## Observed validation

`python art/generate_assets.py` completed successfully and reported the actual produced level as the preview input. `python art/check_assets.py` passed; the durable results are in `art/validation.json`. Checks covered the five contracted IDs, 32px dimensions/viewBox, parseable vectors without referenced content, production hashes, and exact in-process regeneration from the declared source inputs. An authorized player-color change affected only the player and remained valid. Wrong-viewBox and linked-raster witnesses were rejected for the stated reasons.

Art rendered `art/generated/preview.svg` to the supplied `art/generated/preview.png` using the host's installed PyMuPDF and opened that PNG with `view_image`. This is exact vector rasterization, not raster asset generation. The inspected 760 × 650 image contains a native 32px asset row and the actual produced room at 32px and 56px tile sizes. Observed: the round-headed teal player, ring-shaped key and tall arched door are visibly distinct at 32px; masonry reads as a solid obstruction; silhouettes fit the tile bounds; transparent overlays sit cleanly on the floor. The preview compositor uses explicit transform groups for renderer compatibility. PyMuPDF is used only for this inspection PNG; it is not needed for the tool, SVG preview or game.

The design context `/root/studio_design` requested distinct key/exit silhouettes and a door-like exit; art responded with that shape plan. Programming has stated it read the actual SVGs and manifest and intends to embed them as data URIs. Those messages are observed communication, not a receiver-produced acceptance of this packet.

## Limits and next action

Art's file/preview contribution is complete. Gameplay, a real-browser view of `index.html`, and full-game integration were not observed by this context at this delivery point. In-process deterministic regeneration is a scoped asset-reproduction witness; it does not establish a fresh-machine build or globally minimal architecture. SVG validation is distinct from the visual observation above. No independent review is claimed here. There is no unresolved art decision or missing asset.

Programming should verify the paired packet's hashes against revision 1, consume the manifest and actual SVGs in its build, inspect initial and key-collected/won states, then leave its own ACK or CHALLENGE referencing the packet ID and the exact scope observed. Preserve this delivery when later evidence supersedes it; do not relabel this preview evidence as runtime evidence.

The ai-game-studio, global-first-completion and mssp-tdd-apr skill texts were read. The host supplied the initially missing MSSP references from their published repository, and this art context read all three. No source-availability limitation remains. No additional agents were created, and nothing was installed or published.
