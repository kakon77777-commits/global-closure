"""Read source bytes without changing them; never follow nested symlinks."""

import hashlib
import os
import re
from pathlib import Path

from .models import Document, Inventory, Notice

EXCLUDED_DIRS = {".git", "node_modules", "__pycache__"}
EXTENSIONS = {".md", ".markdown"}
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
H1 = re.compile(r"^ {0,3}#(?:[ \t]+(.*)|[ \t]*)$")


def extract_title(text: str, fallback: str) -> str:
    """Use the first ATX H1 outside fenced code, or the filename stem."""
    active_fence = ""
    for line in text.splitlines():
        match = FENCE.match(line)
        if match:
            marker, rest = match.groups()
            if not active_fence:
                active_fence = marker
            elif (
                marker[0] == active_fence[0]
                and len(marker) >= len(active_fence)
                and not rest.strip()
            ):
                active_fence = ""
            continue
        if active_fence:
            continue
        heading = H1.match(line)
        if heading:
            title = re.sub(r"[ \t]+#+[ \t]*$", "", heading.group(1) or "").strip()
            if title:
                return title
    return fallback


def scan(source: Path) -> Inventory:
    source = source.resolve(strict=True)
    if not source.is_dir():
        raise ValueError("Source must be a directory.")
    result = Inventory(source_name=source.name or source.anchor)

    def relative(path: Path) -> str:
        return path.relative_to(source).as_posix()

    def walk_error(error: OSError) -> None:
        path = Path(error.filename) if error.filename else source
        result.issues.append(Notice(relative(path), "directory_unreadable"))

    for directory, dirs, filenames in os.walk(source, followlinks=False, onerror=walk_error):
        parent = Path(directory)
        kept = []
        for name in sorted(dirs, key=lambda item: (item.casefold(), item)):
            path = parent / name
            if path.is_symlink():
                result.skipped.append(Notice(relative(path), "symlink"))
            elif name.casefold() in EXCLUDED_DIRS:
                result.skipped.append(Notice(relative(path), "excluded_directory"))
            else:
                kept.append(name)
        dirs[:] = kept
        for name in sorted(filenames, key=lambda item: (item.casefold(), item)):
            path = parent / name
            if path.suffix.casefold() not in EXTENSIONS:
                continue
            if path.is_symlink():
                result.skipped.append(Notice(relative(path), "symlink"))
                continue
            try:
                raw = path.read_bytes()
                text = raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                result.issues.append(Notice(relative(path), "invalid_utf8"))
                continue
            except OSError:
                result.issues.append(Notice(relative(path), "file_unreadable"))
                continue
            result.documents.append(
                Document(
                    path=relative(path),
                    title=extract_title(text, path.stem),
                    characters=len(text),
                    size_bytes=len(raw),
                    sha256=hashlib.sha256(raw).hexdigest(),
                )
            )
    result.documents.sort(key=lambda d: (d.path.casefold(), d.path))
    result.issues.sort(key=lambda item: (item.path.casefold(), item.path))
    result.skipped.sort(key=lambda item: (item.path.casefold(), item.path))
    return result
