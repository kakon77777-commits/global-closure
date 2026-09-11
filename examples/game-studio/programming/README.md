# Programming contribution

Open the root `index.html` in a desktop browser to play. Arrow keys or WASD move
one cardinal tile per press; R or the Restart button resets the room. Holding a
key does not repeat moves. Key possession, door feedback, accepted move count,
and victory are visible. After victory, movement stops until restart.

The output is one self-contained HTML file. It needs no server, account, network,
installation, or third-party runtime library. Browser JavaScript must be enabled.

## Production tool

From the project root on Windows, after the design and art producers have run:

```powershell
py -3 programming/build.py
```

On Linux the observed command was `python programming/build.py`.
Python 3.10+ standard library is sufficient. The tool reads the authoritative
shared contract and world; the actual `design/generated/level.json`; the design
producer's validator; the art manifest and each of its five referenced SVGs;
and `programming/page.html` plus `programming/runtime.js`.

It validates the produced level through the design-owned algorithm, checks the
contracted art IDs and dimensions, embeds the level JSON, and places the exact
SVG bytes in image data URIs. Floor tiles are underneath other art. Player is the
last overlay so it stays visible on the exit. There is no copied level layout in
the runtime. The build writes `index.html` and
`programming/generated/build-evidence.json`, including all consumed file hashes
and the HTML output hash. No random input is used.

`--output PATH --evidence PATH` selects alternate project-local outputs. These
options are for local diagnostic builds; the contracted entry remains `index.html`.
The build is an importer, not a game editor or a general engine.

## Observed verification

For development verification with an existing Node installation:

```powershell
node programming/verify_runtime.cjs
```

This witness extracts the JavaScript from the generated HTML and executes that
exact source with Node's standard `vm` module and a small DOM double. It calls the
registered keyboard and restart callbacks, observes the runtime snapshot and DOM
assignments, and compares embedded data and SVG bytes to the produced inputs.
Node is not required to play the game.

The observed run passed seven grouped checks:

- Exact consumption of the saved design JSON.
- Actual use of all five SVG asset byte sequences and static offline structure.
- Initial position and visible key/objective status assignments.
- Bounds, wall and locked-door blocking through the keyboard callback.
- Design's 16-move solution: key at move 8, win at move 16, stable win and restart.
- WASD, uppercase input, ignored key repeats/modifiers, and R restart.
- The same blocked-door witness rejects a deliberately disabled lock guard.

Detailed traces, the generated HTML hash and the witness hash are saved in
`programming/generated/runtime-evidence.json`. The initial invocation before
implementation failed because `index.html` did not exist; that was an absent
entry-point witness, not a demonstrated gameplay defect. After the complete
build existed, the first full runtime witness passed.

## Evidence boundaries and resumption

Behavioral evidence covers the shipped JavaScript, event callbacks, and DOM
property/text assignments under a test double. No browser engine was run, so
actual image decoding, CSS layout, focus behavior, assistive technology output,
human playtesting and enjoyment remain unverified. The host's advertised
Playwright Chromium executable was reported unavailable; no browser was
downloaded or installed. Art's separate SVG preview inspection is its own
evidence and is not a browser view of this HTML.

Structural evidence consists of explicit inputs, a rerunnable producer and exact
hashes; no fresh-machine or minimal-architecture reconstruction is claimed.
Discriminative evidence is limited to the named removed-lock witness and its
passing original control. It is not exhaustive runtime verification.

The base is `studio/world.json` revision 1. This role did not advance the shared
world or change the contract. Programming was the integration Lead; the real
design context `/root/studio_design` was asked to be its event-local peer for
design consumption and gameplay semantics. Treat any actual later peer packet
as the authority for the scope it observed; this README does not imply receipt
or independent acceptance. Receiver notes and hashed packets are under
`handoffs/programming-ack-*-r1.*`.
