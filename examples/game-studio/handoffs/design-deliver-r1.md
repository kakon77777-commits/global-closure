# Design delivery for programming

- Project: `key-door-studio-demo` at `studio/world.json` revision 1.
- Source role/context: design, host-observed `/root/studio_design`.
- Recipient: programming; its context locator is not yet observed at delivery.
- Integration owner: programming. No shared contract or world state was changed.
- Delivery packet: `handoffs/design-deliver-r1.json`; it pins the baseline, contract,
  source, producer, output and evidence bytes.

## Delivered contribution

`design/level_tool.py` compiles the authored `design/level-layout.txt` into the actual
game input `design/generated/level.json`. `design/verify_design.py` reads that saved
input, checks required reachability and falsifying cases, and independently replays
movement. Rerun commands and assumptions are in `design/README.md`.

The level is 5×5, with player `[0,0]`, key `[0,4]`, exit `[4,0]`, and 7 walls. The
design intention is a brief exploration loop with an initially reachable locked
door and a detour to its key. The shortest legal winning sequence is:

`down down right right down down left left right right right right up up up up`

The eighth accepted move collects the key; the sixteenth wins. From a fresh start,
`up right down right right right` exercises out-of-bounds blocking, a wall, and a
blocked exit attempt; it should leave the player at `[3,0]` without the key or a win.

## Observed checks and their limits

- Production command exited 0 and emitted the contracted JSON plus a BFS witness.
- The witness runner reported **13/13 passed**, with detailed observations saved in
  `design/generated/verification.json`.
- Behavioral evidence: the saved data supports the intended key-then-exit route in
  the independent movement model. Browser consumption remains pending.
- Discriminative evidence: named tests reject a key reachable only by crossing the
  locked exit, isolated objectives, overlapping entities, entity/wall overlap,
  out-of-bounds cells and boolean coordinates. Reflection and wall reordering pass.
- Structural evidence: inputs, deterministic algorithm and byte hashes are supplied.
  A separate clean-environment reconstruction has not been claimed.
- The initial pre-implementation witness invocation exited 1 because `level_tool`
  did not yet exist; after the producer was implemented, production and witnesses
  passed. This initial result alone was not a behavioral defect diagnosis.
- Human playtesting, visual clarity and enjoyment: `NotMeasured`.

Art at host-observed `/root/studio_art` responded to the targeted affordance request:
its planned key has a gold circular bow and toothed shaft, and its exit is a large
arched wooden door with a keyhole. This is a received description, not a claim of
design-side visual inspection or independent acceptance of the gameplay validator.
No programming ACK or independent peer review has been received at delivery.

The ai-game-studio, global-first-completion and MSSP guidance were loaded. Missing
MSSP reference documents were subsequently supplied by the parent from the published
source and read; there is no remaining source-availability blocker. No additional
agents, installations, publication or external services were used by this role.

## Required next action

1. Read the shared world and contract; verify this packet against the current bytes.
   If the baseline or contract changed, compare the change before reusing evidence.
2. Run the design producer and witness runner, then have the integration tool consume
   `design/generated/level.json` directly into the self-contained browser game.
3. Exercise the blocked-movement sequence and the 16-move solution in the real runtime;
   verify visible key possession, locked-door feedback, win state and restart.
4. Write a receiver-produced ACK or CHALLENGE identifying what was inspected or
   integrated and the resulting revision. Receipt, technical and product acceptance
   remain separate. Only the integrator advances `studio/world.json`.

No design decisions or contract proposals remain unresolved. Integration acceptance
is pending the actual programming receiver; this packet does not imply it occurred.
