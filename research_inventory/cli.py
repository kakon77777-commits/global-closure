"""Command line orchestration and explicit completion status."""

import argparse
import sys
from pathlib import Path

from . import __version__
from .reports import write_reports
from .scanner import scan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inventory UTF-8 Markdown documents without changing source files."
    )
    parser.add_argument("source", type=Path, help="Directory to scan recursively")
    parser.add_argument("--output", type=Path, required=True, help="Report directory outside source")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)
    try:
        source = args.source.resolve(strict=True)
        output = args.output.resolve()
        if output.is_relative_to(source):
            raise ValueError("Output must be outside the source directory to preserve original files.")
        inventory = scan(source)
        data = write_reports(inventory, output)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    summary = data["summary"]
    print(
        f"Indexed {summary['documents']} documents; "
        f"duplicate groups: {summary['duplicate_groups']}; "
        f"read issues: {summary['issues']}."
    )
    if summary["issues"]:
        print("PARTIAL: reports were written; inspect the issues section.", file=sys.stderr)
        return 1
    print("Complete: inventory.json and inventory.md were written.")
    return 0
