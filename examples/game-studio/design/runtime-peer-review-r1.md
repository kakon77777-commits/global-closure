# Design peer review: CONCUR within the stated boundary

Reviewer: design, host-observed `/root/studio_design`. Lead: programming,
host-observed `/root/studio_programming`. Project: `key-door-studio-demo`,
`studio/world.json` revision 1. This is the one scoped review requested by both
the parent and programming; it does not change the contract or earlier deliveries.

**CONCUR** that the current integration consumes the actual design output and that
the implemented movement, locked-exit, key, win and restart logic matches the shared
contract within the executed JavaScript/DOM-double boundary.

## What the reviewer actually observed

I read the current world and contract, `programming/build.py`,
`programming/runtime.js`, `programming/verify_runtime.cjs`, and both programming
evidence files. A fresh read-only Python audit exited 0 and established:

- The build report's relevant contract, world, design, validator, builder and runtime
  hashes match the current files.
- The current `index.html` hash matches both the build output and runtime input
  hashes, and the runtime witness hash matches the reviewed witness file.
- The HTML's parsed `level-data` equals the saved `design/generated/level.json`.
- The HTML's `game-runtime` equals the reviewed runtime source, allowing only
  surrounding whitespace.
- The current runtime report records seven passing checks. I inspected their
  assertions and observations; I did not rerun the witness or change its evidence.

The importer reads the contracted level path and invokes the design validator.
The runtime reads its embedded level, moves by cardinal vectors, rejects bounds
and walls, blocks the exit without the key, collects the key on entry, and wins
only on entering the exit while holding it. Restart resets position, possession,
win state and move count and restores the key's DOM visibility.

Programming's recorded replay covers the design's blocked sequence, key collection
on move 8, victory on move 16, stable victory state, and restart. The reviewed
witness also checks the inventory/objective/key DOM assignments and rejects a
runtime with the locked-exit guard disabled. This supports the named behavior
and discrimination claims; it is not an exhaustive input or engine test.

## Snapshot binding (SHA-256)

| Artifact | Hash |
| --- | --- |
| `studio/world.json` | `80951e95ffd2e8cf2e04543f4e2b22d304a1bad361d43a9144005bb3a1a8b9d0` |
| `studio/game-contract.json` | `1f238eda7ee5daecabe26aee996896155d239b083988f43ac6e9f6c956c943c4` |
| `design/generated/level.json` | `75c8a6387def87a916b568dabaff55a9d2d110c0c432fd7a1ceb2b013f684eaf` |
| `programming/build.py` | `f8820694819821311bcca852abeecdc6d79c19fb1d6d4fe45ec46789f370939b` |
| `programming/runtime.js` | `39f8e59e90f6f3764c39cebe652d6a23418c3272fcd42d9d8ea799ebdf19611c` |
| `programming/verify_runtime.cjs` | `ab280af65d3b9653a6210e70d2e898c6a7f6dd9497f10314144a32a4f6f0537e` |
| `index.html` | `fe6001654c6776bf65f71a0c54d3a629a815c80db925cf389d2bad5d6a7941d2` |
| `programming/generated/build-evidence.json` | `c53bc8278a5ae07bcab7aa3e534bc75912f674559300e8c89410bbd34e027176` |
| `programming/generated/runtime-evidence.json` | `66005ea928b5644156869a5b0fba7c4f02a2d10d3b5c1f8a90d75ad35a7dfebc` |

## Limits and next action

Actual browser rendering, image decoding, layout, focus handling, screen-reader
behavior and human playtesting were not exercised by this review or by the cited
DOM-double replay. Browser-visible presentation, ease of play and enjoyment remain
unverified. This note makes no clean-environment reconstruction claim.

During this review I received and read the real programming ACK at
`handoffs/programming-ack-design-r1.json`, ID
`aec1b005-01dc-4748-ae8b-8bc1b4aafe1e`, replying to the original design delivery.
The handoff helper returned `CURRENT` when checked as the actual design recipient.
That result establishes snapshot integrity only. Programming's recorded technical
acceptance and this design peer's source/evidence review are separate observations.
Programming may continue scoped integration closure while retaining the limitations.

## Separate targeted art observation

At art's request, I visually inspected `art/generated/preview.png`, SHA-256
`0b44a51baa60bac85da8d691e32de04294587094e3362b9ad5d5d5832b91b02d`.
At the native 32px samples and the native-size produced-level preview, the gold
key's ring-and-shaft silhouette and the tall arched wooden exit remain visually
distinct. This observation comes from the rendered image, not code inspection.
It does not establish browser rendering, readability during play, or broad art
quality or product acceptance. The same scoped observation was sent to the real
art context `/root/studio_art`.
