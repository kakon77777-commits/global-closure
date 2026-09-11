"""Compile this game's small text layout and prove its two-stage reachability."""
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
DIRECTIONS = (("right", 1, 0), ("down", 0, 1), ("left", -1, 0), ("up", 0, -1))


class LevelError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(f"{code}: {message}")


def require(condition, code, message):
    if not condition:
        raise LevelError(code, message)


def compile_layout(text):
    rows = text.splitlines()
    require(bool(rows) and bool(rows[0]), "LAYOUT_EMPTY", "The layout must contain cells.")
    require(all(len(row) == len(rows[0]) for row in rows), "LAYOUT_RECTANGLE",
            "Every layout row must have the same width.")
    level = {"width": len(rows[0]), "height": len(rows), "walls": []}
    entities = {"P": "player", "K": "key", "E": "exit"}
    for y, row in enumerate(rows):
        for x, symbol in enumerate(row):
            require(symbol in ".#PKE", "LAYOUT_SYMBOL", f"Unknown cell {symbol!r} at [{x},{y}].")
            if symbol == "#":
                level["walls"].append([x, y])
            elif symbol in entities:
                entity = entities[symbol]
                require(entity not in level, "LAYOUT_ENTITY_COUNT", f"Multiple {entity} cells.")
                level[entity] = [x, y]
    require(all(name in level for name in entities.values()), "LAYOUT_ENTITY_COUNT",
            "Provide exactly one player, key and exit.")
    return level


def shortest_path(level, start, goal, blocked):
    start, goal = tuple(start), tuple(goal)
    queue = deque([start])
    previous = {start: None}
    while queue:
        cell = queue.popleft()
        if cell == goal:
            path, actions = [], []
            while cell != start:
                path.append(list(cell))
                cell, action = previous[cell]
                actions.append(action)
            path.append(list(start))
            return list(reversed(path)), list(reversed(actions))
        for action, dx, dy in DIRECTIONS:
            candidate = (cell[0] + dx, cell[1] + dy)
            x, y = candidate
            if (0 <= x < level["width"] and 0 <= y < level["height"]
                    and candidate not in blocked and candidate not in previous):
                previous[candidate] = (cell, action)
                queue.append(candidate)
    return None


def validate_level(level, contract):
    require(isinstance(level, dict), "LEVEL_TYPE", "The level must be a JSON object.")
    required = ("width", "height", "walls", "player", "key", "exit")
    require(all(field in level for field in required), "LEVEL_FIELDS", "Missing contracted fields.")
    level_format = contract["gameplay"]["level_format"]
    for axis in ("width", "height"):
        specification = re.fullmatch(r"integer (\d+)", level_format[axis])
        require(specification is not None, "CONTRACT_DIMENSION", "Unsupported dimension contract.")
        require(type(level[axis]) is int and level[axis] == int(specification.group(1)),
                "LEVEL_DIMENSIONS", f"{axis} must satisfy {level_format[axis]}.")

    def coordinate(value):
        require(isinstance(value, list) and len(value) == 2
                and all(type(component) is int for component in value),
                "COORDINATE_TYPE", "Coordinates must be [x,y] integer pairs.")
        require(0 <= value[0] < level["width"] and 0 <= value[1] < level["height"],
                "COORDINATE_BOUNDS", f"Coordinate {value} is out of bounds.")
        return tuple(value)

    require(isinstance(level["walls"], list), "WALLS_TYPE", "Walls must be a list.")
    wall_cells = [coordinate(cell) for cell in level["walls"]]
    walls = set(wall_cells)
    entities = [coordinate(level[entity]) for entity in ("player", "key", "exit")]
    require(len(set(entities)) == 3, "ENTITY_OVERLAP", "Player, key and exit must be distinct.")
    require(not any(cell in walls for cell in entities), "ENTITY_WALL_OVERLAP",
            "Entities cannot occupy wall cells.")
    player, key, door = entities
    first = shortest_path(level, player, key, walls | {door})
    require(first is not None, "KEY_UNREACHABLE_BEFORE_EXIT",
            "The key must be reachable while the exit is blocked.")
    second = shortest_path(level, key, door, walls)
    require(second is not None, "EXIT_UNREACHABLE_AFTER_KEY",
            "The exit must be reachable after the key is collected.")
    return {"accepted": True, "path_to_key": first[0], "path_key_to_exit": second[0],
            "steps_to_key": len(first[1]), "steps_key_to_exit": len(second[1]),
            "total_steps": len(first[1]) + len(second[1]), "actions": first[1] + second[1]}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(path):
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(resolved)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Compile the source layout into gameplay JSON.")
    build.add_argument("--source", type=Path, default=ROOT / "design/level-layout.txt")
    build.add_argument("--output", type=Path, default=ROOT / "design/generated/level.json")
    build.add_argument("--evidence", type=Path, default=ROOT / "design/generated/build-evidence.json")
    validate = commands.add_parser("validate", help="Validate a gameplay JSON file.")
    validate.add_argument("level", type=Path)
    args = parser.parse_args()
    contract_path = ROOT / "studio/game-contract.json"
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        if args.command == "validate":
            level = json.loads(args.level.read_text(encoding="utf-8"))
            print(json.dumps(validate_level(level, contract), indent=2))
        else:
            level = compile_layout(args.source.read_text(encoding="utf-8"))
            proof = validate_level(level, contract)
            write_json(args.output, level)
            evidence = {"schema": 1, "producer": "design/level_tool.py",
                        "source_sha256": sha256(args.source), "tool_sha256": sha256(Path(__file__)),
                        "contract_sha256": sha256(contract_path), "output_sha256": sha256(args.output),
                        "algorithm": "Breadth-first search: player-to-key with exit blocked, then key-to-exit.",
                        "parameters": {"source": reference(args.source), "output": reference(args.output),
                                       "seed": None,
                                       "neighbor_order": [entry[0] for entry in DIRECTIONS]},
                        "proof": proof}
            write_json(args.evidence, evidence)
            print(f"Built {args.output}; valid key-and-exit route: {proof['total_steps']} steps.")
        return 0
    except (LevelError, OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
