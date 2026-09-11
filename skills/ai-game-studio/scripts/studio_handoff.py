"""Create or check a local, version-bound handoff. No network or agent execution."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import uuid


ROLES = ("programming", "art", "design")
KINDS = ("DELIVER", "REQUEST", "ACK", "CHALLENGE")


def require(value, message):
    if not value:
        raise ValueError(message)


def text_field(value, label):
    require(isinstance(value, str) and value.strip(), f"Missing {label}")
    return value


def safe_path(root, name):
    require(isinstance(name, str) and name and "\\" not in name and ":" not in name,
            "Use a relative project path with forward slashes")
    relative = PurePosixPath(name)
    require(not relative.is_absolute() and ".." not in relative.parts,
            f"Path leaves project: {name}")
    path = (root / name).resolve()
    require(path.is_relative_to(root), f"Path leaves project: {name}")
    require(path.is_file(), f"Missing project file: {name}")
    return path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_record(root, name):
    path = safe_path(root, name)
    data = path.read_bytes()
    return {"path": name, "sha256": digest(data), "bytes": len(data)}


def read_world(root, name):
    data = safe_path(root, name).read_bytes()
    world = json.loads(data)
    require(isinstance(world, dict) and type(world.get("schema")) is int
            and world["schema"] == 1, "Unsupported world schema")
    text_field(world.get("project_id"), "project_id")
    require(type(world.get("revision")) is int and world["revision"] >= 1,
            "World revision must be a positive integer")
    text_field(world.get("scope"), "scope")
    text_field(world.get("target"), "target")
    require(world.get("integrator") in ROLES, "Invalid integration owner")
    contracts = world.get("contracts")
    require(isinstance(contracts, list) and all(isinstance(p, str) for p in contracts),
            "World contracts must be a list of project paths")
    require(len(set(contracts)) == len(contracts), "Duplicate contract path")
    return world, {"path": name, "sha256": digest(data)}


def create_packet(args):
    root = args.project.resolve()
    world, world_ref = read_world(root, args.world)
    summary = args.note.read_text(encoding="utf-8")
    text_field(summary, "handoff note")
    text_field(args.context, "source context locator")
    if args.kind in ("ACK", "CHALLENGE"):
        text_field(args.reply_to, "reply-to packet ID")
    artifacts = args.artifact or []
    require(len(set(artifacts)) == len(artifacts), "Duplicate artifact path")
    packet = {
        "schema": 1, "id": str(uuid.uuid4()),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": world["project_id"], "revision": world["revision"],
        "world": world_ref, "from_role": args.from_role, "to_role": args.to_role,
        "source_context": args.context, "kind": args.kind, "reply_to": args.reply_to,
        "summary": summary,
        "contracts": [file_record(root, p) for p in world["contracts"]],
        "artifacts": [file_record(root, p) for p in artifacts],
    }
    # Never overwrite another conversation's packet or mutate the project world.
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(packet, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return {"status": "PACKED", "id": packet["id"], "output": str(args.output),
            "delivery": "local file only; receiver has not acknowledged"}


def verify_packet(args):
    root = args.project.resolve()
    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    require(isinstance(packet, dict) and type(packet.get("schema")) is int
            and packet["schema"] == 1, "Unsupported handoff schema")
    text_field(packet.get("id"), "packet ID")
    text_field(packet.get("source_context"), "source context")
    text_field(packet.get("summary"), "summary")
    require(packet.get("from_role") in ROLES and packet.get("to_role") in ROLES,
            "Invalid role")
    require(packet["to_role"] == args.as_role, "Handoff addressed to another role")
    require(packet.get("kind") in KINDS, "Invalid packet kind")
    if packet["kind"] in ("ACK", "CHALLENGE"):
        text_field(packet.get("reply_to"), "reply-to packet ID")
    world, world_ref = read_world(root, args.world)
    require(packet.get("project_id") == world["project_id"], "Wrong project")
    require(type(packet.get("revision")) is int and packet["revision"] == world["revision"],
            "Stale world revision")
    require(packet.get("world") == world_ref, "World bytes changed or wrong world path")
    expected_contracts = [file_record(root, p) for p in world["contracts"]]
    require(packet.get("contracts") == expected_contracts, "Contract snapshot changed")
    artifacts = packet.get("artifacts")
    require(isinstance(artifacts, list), "Missing artifacts list")
    seen = set()
    for item in artifacts:
        require(isinstance(item, dict), "Invalid artifact record")
        name = item.get("path")
        actual = file_record(root, name)
        require(name not in seen, "Duplicate artifact path")
        seen.add(name)
        require(item == actual, f"Artifact bytes changed: {name}")
    return {"status": "CURRENT", "id": packet["id"], "role": args.as_role,
            "scope": "snapshot and file integrity only; no semantic approval or peer receipt"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    pack = sub.add_parser("pack", help="Write an immutable packet referencing selected files")
    verify = sub.add_parser("verify", help="Check a packet against the current local snapshot")
    for command in (pack, verify):
        command.add_argument("--project", type=Path, required=True)
        command.add_argument("--world", default="studio/world.json")
    pack.add_argument("--from-role", choices=ROLES, required=True)
    pack.add_argument("--to-role", choices=ROLES, required=True)
    pack.add_argument("--context", required=True, help="Observed context locator, or explicit unknown label")
    pack.add_argument("--kind", choices=KINDS, default="DELIVER")
    pack.add_argument("--reply-to")
    pack.add_argument("--note", type=Path, required=True)
    pack.add_argument("--artifact", action="append")
    pack.add_argument("--output", type=Path, required=True)
    verify.add_argument("--packet", type=Path, required=True)
    verify.add_argument("--as-role", choices=ROLES, required=True)
    args = parser.parse_args()
    try:
        result = create_packet(args) if args.command == "pack" else verify_packet(args)
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
