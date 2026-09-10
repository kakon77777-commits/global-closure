"""Replay the three stored LSPR outcomes in temporary, isolated directories.

This checks recorded code and witnesses; it does not rerun an AI agent.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def materialize(root, files):
    for name, content in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="")


def run(root, args, input_text=None):
    result = subprocess.run(
        [sys.executable, *args], cwd=root, input=input_text,
        text=True, encoding="utf-8", capture_output=True, timeout=30,
    )
    return {
        "command": ["python", *args], "exit_code": result.returncode,
        "stdout": result.stdout, "stderr": result.stderr,
    }


def observe(root, witness):
    result = run(root, ["query_cli.py"], json.dumps(witness["input"]))
    result["input"] = witness["input"]
    result["expected"] = witness["expected"]
    result["matches_contract"] = (
        result["exit_code"] == 0
        and not result["stderr"]
        and json.loads(result["stdout"]) == witness["expected"]
    )
    return result


def replay(case):
    before = case["before_files"]
    after = dict(before, **case["after_changes"])
    changed = sorted(name for name in after if before.get(name) != after[name])
    production_changed = [name for name in changed if name.startswith("query_")]
    require(changed == case["expected_changed_files"], f"{case['name']}: change boundary")
    require(production_changed == case["expected_production_changes"], f"{case['name']}: production boundary")
    preserved = sorted(name for name in before if before[name] == after[name])
    with tempfile.TemporaryDirectory(prefix="lspr-replay-") as temporary:
        root = Path(temporary)
        old, new = root / "before", root / "after"
        materialize(old, before)
        materialize(new, after)
        old_witness = observe(old, case["witness"])
        new_witness = observe(new, case["witness"])
        old_tests = run(old, ["-m", "unittest", "-v"])
        new_tests = run(new, ["-m", "unittest", "-v"])
    require(old_witness["matches_contract"] == case["witness"]["before_matches"], f"{case['name']}: before witness")
    require(new_witness["matches_contract"], f"{case['name']}: after witness")
    require(old_tests["exit_code"] == case["baseline_test_exit"], f"{case['name']}: before tests")
    require(new_tests["exit_code"] == 0, f"{case['name']}: after tests")
    return {
        "name": case["name"], "responsibility": case["responsibility"],
        "changed_files": changed, "production_changed": production_changed,
        "preserved_files": preserved,
        "before_sha256": {n: hashlib.sha256(c.encode("utf-8")).hexdigest() for n, c in before.items()},
        "after_sha256": {n: hashlib.sha256(c.encode("utf-8")).hexdigest() for n, c in after.items()},
        "before_witness": old_witness, "after_witness": new_witness,
        "before_tests": old_tests, "after_tests": new_tests, "passed": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional JSON result path")
    args = parser.parse_args()
    fixture_path = Path(__file__).with_name("cases.json")
    fixture_bytes = fixture_path.read_bytes()
    fixture = json.loads(fixture_bytes)
    skill_path = Path(__file__).resolve().parents[2] / "skills" / "lspr" / "SKILL.md"
    skill_sha256 = hashlib.sha256(skill_path.read_bytes()).hexdigest()
    require(skill_sha256 == fixture["skill_sha256"], "Skill differs from the forward-tested version")
    report = {
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "platform": platform.platform(),
        "skill_sha256": skill_sha256,
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "method": "Independent replay of stored before/after artifacts; no new agent execution",
        "cases": [replay(case) for case in fixture["cases"]],
    }
    report["passed"] = all(case["passed"] for case in report["cases"])
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for case in report["cases"]:
        print(f"PASS {case['name']}: responsibility={case['responsibility']}; production changes={case['production_changed']}")
    if args.output:
        print(f"Results: {args.output}")


if __name__ == "__main__":
    main()
