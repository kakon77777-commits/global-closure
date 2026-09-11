"""Bounded, executable design witnesses; uses Python 3.10+ standard library only."""
import copy
import hashlib
import json
import sys
from pathlib import Path

from level_tool import LevelError, compile_layout, validate_level


ROOT = Path(__file__).resolve().parents[1]
MOVES = {"right": (1, 0), "down": (0, 1), "left": (-1, 0), "up": (0, -1)}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def simulate(level, actions):
    """Independent replay consumer for the contracted movement/key/exit behavior."""
    position = tuple(level["player"])
    walls = {tuple(cell) for cell in level["walls"]}
    key = tuple(level["key"])
    door = tuple(level["exit"])
    has_key = False
    won = False
    events = []
    for action in actions:
        dx, dy = MOVES[action]
        candidate = (position[0] + dx, position[1] + dy)
        x, y = candidate
        if not (0 <= x < level["width"] and 0 <= y < level["height"]):
            result = "blocked_bounds"
        elif candidate in walls:
            result = "blocked_wall"
        elif candidate == door and not has_key:
            result = "blocked_exit"
        else:
            position = candidate
            if position == key and not has_key:
                has_key = True
                result = "key_collected"
            elif position == door and has_key:
                won = True
                result = "won"
            else:
                result = "moved"
        events.append({"action": action, "position": list(position), "result": result,
                       "has_key": has_key, "won": won})
    return events


def run():
    contract_path = ROOT / "studio/game-contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    level_path = ROOT / "design/generated/level.json"
    level = json.loads(level_path.read_text(encoding="utf-8"))
    cases = []

    def check(name, condition, observation):
        cases.append({"case": name, "passed": bool(condition), "observation": observation})

    def rejects(name, candidate, expected_code):
        try:
            validate_level(candidate, contract)
            observed = "ACCEPTED"
        except LevelError as exc:
            observed = exc.code
        check(name, observed == expected_code, {"expected": expected_code, "actual": observed})

    proof = validate_level(level, contract)
    check("generated_file_matches_source", level == compile_layout(
        (ROOT / "design/level-layout.txt").read_text(encoding="utf-8")),
        "Compiled the saved source and compared the generated JSON values.")
    check("accepted_level_has_8_then_8_step_route",
          proof["steps_to_key"] == 8 and proof["steps_key_to_exit"] == 8, proof)

    mirrored = copy.deepcopy(level)
    for entity in ("player", "key", "exit"):
        mirrored[entity][0] = 4 - mirrored[entity][0]
    mirrored["walls"] = [[4 - x, y] for x, y in reversed(level["walls"])]
    mirror_proof = validate_level(mirrored, contract)
    check("accepted_reflection_and_wall_reordering",
          mirror_proof["total_steps"] == 16, {"total_steps": mirror_proof["total_steps"]})

    door_first = {"width": 5, "height": 5, "walls": [[x, y] for y in range(5)
                  for x in range(1, 5)], "player": [0, 0], "key": [0, 4], "exit": [0, 2]}
    rejects("reject_key_behind_locked_exit", door_first, "KEY_UNREACHABLE_BEFORE_EXIT")
    check("door_first_fixture_is_connected_if_lock_is_ignored",
          all([0, y] not in door_first["walls"] for y in range(5)),
          {"otherwise_open_route": [[0, y] for y in range(5)], "exit_on_route": [0, 2]})

    unreachable_key = copy.deepcopy(level)
    unreachable_key["walls"].append([1, 4])
    rejects("reject_isolated_key", unreachable_key, "KEY_UNREACHABLE_BEFORE_EXIT")
    unreachable_exit = {"width": 5, "height": 5, "walls": [[x, 3] for x in range(5)],
                        "player": [0, 0], "key": [1, 0], "exit": [4, 4]}
    rejects("reject_exit_unreachable_after_key", unreachable_exit, "EXIT_UNREACHABLE_AFTER_KEY")
    overlap = copy.deepcopy(level)
    overlap["key"] = overlap["player"]
    rejects("reject_entity_overlap", overlap, "ENTITY_OVERLAP")
    outside = copy.deepcopy(level)
    outside["key"] = [5, 4]
    rejects("reject_out_of_bounds_entity", outside, "COORDINATE_BOUNDS")
    wall_overlap = copy.deepcopy(level)
    wall_overlap["walls"].append(wall_overlap["key"])
    rejects("reject_entity_wall_overlap", wall_overlap, "ENTITY_WALL_OVERLAP")
    non_integer = copy.deepcopy(level)
    non_integer["key"] = [False, 4]
    rejects("reject_boolean_coordinate", non_integer, "COORDINATE_TYPE")

    early_door = simulate(level, ["up", "right", "down", "right", "right", "right"])
    check("replay_blocks_bounds_wall_and_locked_exit",
          [event["result"] for event in early_door] == ["blocked_bounds", "moved", "blocked_wall",
                                                          "moved", "moved", "blocked_exit"], early_door)
    replay = simulate(level, proof["actions"])
    check("saved_level_replay_collects_key_before_win",
          len(replay) == 16 and replay[7]["result"] == "key_collected"
          and all(not event["won"] for event in replay[:-1])
          and replay[-1]["result"] == "won", replay)

    report = {"schema": 1, "passed": all(case["passed"] for case in cases),
              "checks": cases, "input": "design/generated/level.json",
              "input_sha256": digest(level_path), "contract_sha256": digest(contract_path),
              "tool_sha256": digest(ROOT / "design/level_tool.py"),
              "witness_sha256": digest(Path(__file__)),
              "consumer": "design/verify_design.py independent movement replay model",
              "scope": "One deterministic 5x5 level; finite named witnesses, not exhaustive engine testing.",
              "runtime_integration": "Pending programming receiver evidence.",
              "human_playtest": "NotMeasured"}
    evidence_path = ROOT / "design/generated/verification.json"
    evidence_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    passed = sum(case["passed"] for case in cases)
    print(f"{passed}/{len(cases)} design checks passed; evidence: {evidence_path.relative_to(ROOT)}")
    for case in cases:
        if not case["passed"]:
            print(json.dumps(case), file=sys.stderr)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(run())
