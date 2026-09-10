"""Behavior tests for correctness, source preservation, and real CLI execution."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from research_inventory.reports import write_reports
from research_inventory.scanner import extract_title, scan

PROJECT = Path(__file__).resolve().parents[1]


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "中文 papers"
        self.source.mkdir()
        self.output = self.base / "output reports"

    def put(self, relative, content):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
        return path

    def cli(self, source=None, output=None):
        return subprocess.run(
            [sys.executable, str(PROJECT / "run.py"), str(source or self.source),
             "--output", str(output or self.output)],
            cwd=self.base, capture_output=True, encoding="utf-8", check=False,
        )

    def test_recursive_unicode_paths_extensions_and_title_fallback(self):
        content = "# 離線研究\n\nHello 世界\n"
        self.put("子目錄/paper.MD", content)
        self.put("notes.markdown", "no h1\n")
        self.put("ignored.txt", "# not a document")
        data = scan(self.source).to_dict()
        self.assertEqual(data["summary"]["documents"], 2)
        by_path = {item["path"]: item for item in data["documents"]}
        self.assertEqual(by_path["子目錄/paper.MD"]["title"], "離線研究")
        self.assertEqual(by_path["子目錄/paper.MD"]["characters"], len(content))
        self.assertEqual(by_path["子目錄/paper.MD"]["size_bytes"], len(content.encode("utf-8")))
        self.assertEqual(by_path["notes.markdown"]["title"], "notes")

    def test_title_ignores_fenced_code_and_closing_hashes(self):
        body = "````python\n# hidden\n```\n# still hidden\n`````\n~~~txt\n# hidden too\n~~~\n# Real title ###\n"
        self.assertEqual(extract_title(body, "fallback"), "Real title")
        self.assertEqual(extract_title("#hashtag\n## H2\n#\n", "fallback"), "fallback")

    def test_bom_is_removed_only_for_decoded_character_count(self):
        raw = b"\xef\xbb\xbf" + "# 標題\r\n".encode("utf-8")
        self.put("bom.md", raw)
        document = scan(self.source).documents[0]
        self.assertEqual(document.title, "標題")
        self.assertEqual(document.characters, len("# 標題\r\n"))
        self.assertEqual(document.sha256, hashlib.sha256(raw).hexdigest())

    def test_duplicates_do_not_normalize_newlines_or_bom(self):
        for name in ("a.md", "b.md", "nested/c.md"):
            self.put(name, b"# Same\n")
        self.put("different-newline.md", b"# Same\r\n")
        self.put("different-bom.md", b"\xef\xbb\xbf# Same\n")
        data = scan(self.source).to_dict()
        self.assertEqual(data["summary"]["duplicate_groups"], 1)
        self.assertEqual(data["summary"]["duplicate_extra_copies"], 2)
        self.assertEqual(data["duplicates"][0]["paths"], ["a.md", "b.md", "nested/c.md"])

    def test_known_generated_directories_are_excluded(self):
        for directory in (".git", "node_modules", "__pycache__"):
            self.put(f"{directory}/hidden.md", "# hidden")
        self.put("visible.md", "# visible")
        data = scan(self.source).to_dict()
        self.assertEqual(data["summary"]["documents"], 1)
        self.assertEqual(data["summary"]["skipped_entries"], 3)

    def test_nested_symlinks_are_not_followed(self):
        target = self.put("original.md", "# original")
        try:
            (self.source / "alias.md").symlink_to(target)
            (self.source / "cycle").symlink_to(self.source, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation unavailable on this host")
        data = scan(self.source).to_dict()
        self.assertEqual(data["summary"]["documents"], 1)
        self.assertEqual([n["path"] for n in data["skipped"]], ["alias.md", "cycle"])

    def test_invalid_utf8_yields_partial_report_and_exit_one(self):
        self.put("bad.md", b"\xff\xfe\x00")
        self.put("good.md", "# readable")
        completed = self.cli()
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("PARTIAL", completed.stderr)
        data = json.loads((self.output / "inventory.json").read_text(encoding="utf-8"))
        self.assertEqual(data["summary"]["documents"], 1)
        self.assertEqual(data["issues"], [{"path": "bad.md", "reason": "invalid_utf8"}])
        self.assertTrue((self.output / "inventory.md").exists())

    def test_markdown_table_is_escaped_and_json_preserves_original_title(self):
        self.put("paper.md", "# A | B <tag> & C\n")
        data = write_reports(scan(self.source), self.output)
        markdown = (self.output / "inventory.md").read_text(encoding="utf-8")
        self.assertEqual(data["documents"][0]["title"], "A | B <tag> & C")
        self.assertIn("A \\| B &lt;tag&gt; &amp; C", markdown)
        self.assertEqual(json.loads((self.output / "inventory.json").read_text(encoding="utf-8")), data)

    def test_cli_integrates_all_outputs_without_mutating_sources(self):
        self.put("a.md", "# 測試\n")
        self.put("sub/b.md", "# 測試\n")
        before = {p.relative_to(self.source): p.read_bytes() for p in self.source.rglob("*") if p.is_file()}
        completed = self.cli()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        data = json.loads((self.output / "inventory.json").read_text(encoding="utf-8"))
        self.assertEqual(data["summary"]["documents"], 2)
        self.assertEqual(data["summary"]["duplicate_groups"], 1)
        self.assertIn("sub/b.md", (self.output / "inventory.md").read_text(encoding="utf-8"))
        after = {p.relative_to(self.source): p.read_bytes() for p in self.source.rglob("*") if p.is_file()}
        self.assertEqual(after, before)

    def test_missing_source_fails_without_creating_output(self):
        completed = self.cli(source=self.base / "missing")
        self.assertEqual(completed.returncode, 2)
        self.assertFalse(self.output.exists())
        self.assertNotIn("Traceback", completed.stderr)

    def test_file_source_is_rejected(self):
        source_file = self.put("a.md", "# test")
        completed = self.cli(source=source_file)
        self.assertEqual(completed.returncode, 2)
        self.assertFalse(self.output.exists())

    def test_output_inside_source_is_rejected_without_overwriting(self):
        original = self.put("reports/inventory.md", "# original draft")
        completed = self.cli(output=original.parent)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(original.read_bytes(), b"# original draft")
        self.assertFalse((original.parent / "inventory.json").exists())

    def test_output_equal_to_source_is_rejected(self):
        self.put("a.md", "# test")
        completed = self.cli(output=self.source)
        self.assertEqual(completed.returncode, 2)
        self.assertFalse((self.source / "inventory.json").exists())

    def test_output_path_that_is_a_file_has_clear_failure(self):
        self.output.write_bytes(b"existing output path")
        completed = self.cli()
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(self.output.read_bytes(), b"existing output path")
        self.assertNotIn("Traceback", completed.stderr)

    def test_repeated_run_is_deterministic(self):
        self.put("z.md", "# z\n")
        self.put("a.md", "# a\n")
        first = self.cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        second = self.cli()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual({p.name: p.read_bytes() for p in self.output.iterdir()}, before)

    def test_empty_directory_is_a_valid_complete_inventory(self):
        completed = self.cli()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        data = json.loads((self.output / "inventory.json").read_text(encoding="utf-8"))
        self.assertEqual(data["summary"]["documents"], 0)
        self.assertEqual(data["duplicates"], [])

    def test_help_and_module_entrypoint(self):
        completed = subprocess.run(
            [sys.executable, "-m", "research_inventory", "--help"],
            cwd=PROJECT, capture_output=True, encoding="utf-8", check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--output", completed.stdout)


if __name__ == "__main__":
    unittest.main()
