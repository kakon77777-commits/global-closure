# Design contribution

The player explores one 5×5 grid, collects a key, and enters the exit. The gameplay
rules remain authoritative in `studio/game-contract.json`. The arrangement is
authored in `design/level-layout.txt`: `P` player, `K` key, `E` exit, `#` wall, `.` floor.
The source places the exit near the starting route so a player can encounter its
locked state before taking the detour to the key. This is a design intention;
player understanding and enjoyment have not been measured.

Run these commands from the project root with Python 3.10+; no packages are needed:

```powershell
py -3 design/level_tool.py build
py -3 design/verify_design.py
py -3 design/level_tool.py validate design/generated/level.json
```

On Linux, substitute `python3` for `py -3`. Production writes only the level and
build evidence in `design/generated/`; the witness runner writes `verification.json`.
Only `level.json` is a game input. The programming build must read that JSON and
embed it in the offline HTML, rather than copying its coordinates into runtime code.

The producer accepts `build --source PATH --output PATH --evidence PATH` for local
edits. Its output has exactly the contracted fields. It obtains required dimensions
from the shared contract, then checks coordinate types, bounds and non-overlap.
Two breadth-first searches prove player-to-key reachability with the exit blocked,
then key-to-exit reachability with the exit available. Neighbor order is right,
down, left, up; generation is deterministic and uses no random seed or sweep.

The saved level has 7 walls and 18 traversable cells. Its shortest legal completion
uses 16 moves: 8 to the key and 8 from the key to the exit. An executable solution
is saved in `design/generated/build-evidence.json`.

The 13 named witnesses exercise the saved output, a reflected equivalent, a key
behind a locked exit, isolated key/exit cases, overlap and coordinate errors,
blocked movement, and a complete key-before-win replay. The movement replay
independently reads the generated JSON; it is a design model, not the browser game.
The counterexamples are deliberately constructed and are not a random coverage claim.

The simulator assumes each action is exactly one cardinal move; collecting a key
is immediate on entry, and entering an exit with the key wins. It models no timing,
animation, input repeat, or browser events. Runtime integration and visual feedback
require programming evidence. Human playtesting, difficulty, clarity and fun are
`NotMeasured`. The recorded hashes bind evidence to the exact tool, contract and data.

Resume from `handoffs/design-deliver-r1.json` and its referenced note. Only the
programming integrator may update the shared project revision or contract.
