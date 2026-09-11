# Programming ACK of design delivery

This is a receiver-produced ACK by the real programming context
`/root/studio_programming`, addressed to `/root/studio_design`, replying to
DELIVER `7d6feb40-1300-4804-afe0-9c1878aa8ffd`. The project is
`key-door-studio-demo`, shared world revision 1. The contract and world are
unchanged.

I read the current world and contract, the delivery note and packet, the design
source/tool, the saved level JSON and design evidence. The handoff helper returned
`CURRENT` for the delivery's pinned bytes. That result establishes snapshot
integrity; this note separately states the technical acceptance performed here.

`programming/build.py` reads the actual saved `design/generated/level.json` and
calls `design/level_tool.py`'s `validate_level` on it with the shared contract.
It embeds that JSON directly in `index.html`. The generated build evidence binds
the consumed level and validator hashes to the HTML output. I did not rerun the
design-owned producers in place or modify their outputs; the design role's
recorded 13-case run remains its own evidence.

The actual JavaScript extracted from the HTML ran under Node with a minimal DOM
double. Through its registered keyboard callback, design's
`up right down right right right` sequence produced bounds, wall and locked-exit
blocks, ending at `[3,0]` with no key or win and three accepted moves. Its saved
16-move solution collected the key at move 8 and won at move 16. The checks also
observed key-image hiding, key/objective text assignments, a stable won state,
and Restart returning all gameplay state to the initial values. The removed-lock
negative witness was rejected by the same locked-exit check. Seven grouped
runtime checks passed; details are in
`programming/generated/runtime-evidence.json`.

Technical acceptance: the delivered design data is genuinely consumed by the
build and supports the contracted behavior in the shipped JS. Product acceptance
is limited: a real browser, image rendering, CSS layout, focus/accessibility,
human playtesting and enjoyment were not observed. No fresh-machine structural
reconstruction or exhaustive discriminative claim is made.

The runtime and evidence are offered to the real design context as the scoped
peer for this integration event. Its own later ACK/CONCUR or CHALLENGE must be
read for any independent conclusion; this sender does not claim it in advance.
The next useful action is to inspect that peer result and, when a browser is
available, open the self-contained HTML for an actual playtest. No design
decision or contract change is requested.
