"""Observable tests for portable handoff freshness, routing, and preservation."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


DEFAULT_TOOL = Path(__file__).resolve().parents[2] / "skills/ai-game-studio/scripts/studio_handoff.py"
TOOL = Path(sys.argv.pop(1)).resolve() if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else DEFAULT_TOOL


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "studio").mkdir()
        (self.root / "design").mkdir()
        self.world = {
            "schema": 1, "project_id": "test-game", "revision": 1,
            "scope": "One level", "target": "Windows browser",
            "integrator": "programming", "contracts": ["studio/contract.json"],
        }
        self.write_world()
        (self.root / "studio/contract.json").write_text('{"width":5}\n', encoding="utf-8")
        (self.root / "design/level.json").write_text('{"title":"鑰匙與門","width":5}\n', encoding="utf-8")
        (self.root / "note.md").write_text("Produced level; path witness passes. Visual quality not measured. Import next.\n", encoding="utf-8")
        self.packet = self.root / "delivery.json"

    def write_world(self):
        (self.root / "studio/world.json").write_text(json.dumps(self.world) + "\n", encoding="utf-8")

    def command(self, *args):
        return subprocess.run([sys.executable, str(TOOL), *map(str, args)],
                              text=True, encoding="utf-8", capture_output=True, timeout=10)

    def pack(self, *extra):
        return self.command("pack", "--project", self.root, "--from-role", "design",
                            "--to-role", "programming", "--context", "test-context",
                            "--note", self.root / "note.md", "--artifact", "design/level.json",
                            "--output", self.packet, *extra)

    def verify(self, role="programming"):
        return self.command("verify", "--project", self.root, "--packet", self.packet,
                            "--as-role", role)

    def test_fresh_packet_preserves_sources_and_is_not_receipt(self):
        sources = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        packed = self.pack()
        self.assertEqual(packed.returncode, 0, packed.stderr)
        self.assertIn("receiver has not acknowledged", json.loads(packed.stdout)["delivery"])
        current = self.verify()
        self.assertEqual(current.returncode, 0, current.stderr)
        self.assertEqual(json.loads(current.stdout)["status"], "CURRENT")
        for path, content in sources.items():
            self.assertEqual(path.read_bytes(), content)

    def test_changed_asset_is_rejected(self):
        self.assertEqual(self.pack().returncode, 0)
        (self.root / "design/level.json").write_text('{"width":6}', encoding="utf-8")
        result = self.verify()
        self.assertEqual(result.returncode, 2)
        self.assertIn("Artifact bytes changed", result.stderr)

    def test_changed_contract_is_rejected(self):
        self.assertEqual(self.pack().returncode, 0)
        (self.root / "studio/contract.json").write_text('{"width":6}', encoding="utf-8")
        result = self.verify()
        self.assertEqual(result.returncode, 2)
        self.assertIn("Contract snapshot changed", result.stderr)

    def test_advanced_revision_is_rejected(self):
        self.assertEqual(self.pack().returncode, 0)
        self.world["revision"] = 2
        self.write_world()
        result = self.verify()
        self.assertEqual(result.returncode, 2)
        self.assertIn("Stale world revision", result.stderr)

    def test_world_change_without_revision_is_rejected(self):
        self.assertEqual(self.pack().returncode, 0)
        self.world["scope"] = "A different level"
        self.write_world()
        self.assertIn("World bytes changed", self.verify().stderr)
        self.assertEqual(self.verify().returncode, 2)

    def test_wrong_project_and_recipient_are_rejected(self):
        self.assertEqual(self.pack().returncode, 0)
        self.assertEqual(self.verify("art").returncode, 2)
        self.world["project_id"] = "another-game"
        self.write_world()
        result = self.verify()
        self.assertEqual(result.returncode, 2)
        self.assertIn("Wrong project", result.stderr)

    def test_existing_delivery_is_not_overwritten(self):
        self.assertEqual(self.pack().returncode, 0)
        original = self.packet.read_bytes()
        self.assertEqual(self.pack().returncode, 2)
        self.assertEqual(self.packet.read_bytes(), original)

    def test_missing_artifact_and_outside_path_rejected(self):
        (self.root / "design/level.json").unlink()
        self.assertEqual(self.pack().returncode, 2)
        self.assertFalse(self.packet.exists())
        (self.root / "design/level.json").write_text('{}', encoding="utf-8")
        result = self.pack("--artifact", "../outside.json")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Path leaves project", result.stderr)
        self.assertFalse(self.packet.exists())

    def test_ack_requires_a_referenced_packet(self):
        result = self.pack("--kind", "ACK")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.packet.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
