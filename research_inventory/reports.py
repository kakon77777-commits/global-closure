"""Serialize the same inventory contract to JSON and Markdown."""

import html
import json
import os
import tempfile
from pathlib import Path

from .models import Inventory


def cell(value: str) -> str:
    """Escape document-controlled text in Markdown tables and list items."""
    value = html.escape(value, quote=False)
    value = value.replace("\\", "\\\\")
    for character in ("|", "`", "*", "_", "[", "]"):
        value = value.replace(character, "\\" + character)
    return value.replace("\r", " ").replace("\n", " ")


def render_markdown(data: dict) -> str:
    summary = data["summary"]
    lines = [
        "# 研究稿盤點報告",
        "",
        f"來源資料夾：{cell(data['source_name'])}",
        "",
        f"文件：{summary['documents']}；字元：{summary['characters']}；"
        f"原始位元組：{summary['size_bytes']}。",
        f"重複群組：{summary['duplicate_groups']}；額外副本："
        f"{summary['duplicate_extra_copies']}；讀取問題：{summary['issues']}。",
        "",
        "## 文件目錄",
        "",
        "| 相對路徑 | 標題 | 字元數 | 位元組 |",
        "| --- | --- | ---: | ---: |",
    ]
    for document in data["documents"]:
        lines.append(
            f"| {cell(document['path'])} | {cell(document['title'])} | "
            f"{document['characters']} | {document['size_bytes']} |"
        )
    if not data["documents"]:
        lines.extend(["", "沒有可讀取的 Markdown 文件。"])
    lines.extend(["", "## 完全相同的內容", ""])
    for index, group in enumerate(data["duplicates"], start=1):
        lines.extend([f"### 群組 {index}", "", f"SHA-256：`{group['sha256']}`", ""])
        lines.extend(f"- {cell(path)}" for path in group["paths"])
        lines.append("")
    if not data["duplicates"]:
        lines.append("未發現重複群組。")
    reasons = {
        "invalid_utf8": "非有效 UTF-8，未納入統計",
        "file_unreadable": "無法讀取檔案，未納入統計",
        "directory_unreadable": "無法讀取資料夾，該範圍未完成掃描",
        "symlink": "略過符號連結",
        "excluded_directory": "略過預設排除資料夾",
    }
    for title, key in (("讀取問題", "issues"), ("略過項目", "skipped")):
        lines.extend(["", f"## {title}", ""])
        if not data[key]:
            lines.append("無。")
        for notice in data[key]:
            lines.append(f"- {cell(notice['path'])}：{reasons[notice['reason']]}")
    lines.extend([
        "",
        "## 計算方式",
        "",
        "字元數是解碼後的 Unicode code point 數，包含 Markdown 標記、空白及換行，"
        "不含 UTF-8 BOM；不是詞數或視覺字形數。",
        "重複群組以原始檔案 SHA-256 識別，不正規化 BOM、空白或換行；"
        "不代表語義相同或學術價值相同。",
        "原稿僅讀取，不修改或刪除。非 Markdown 檔案不納入盤點。",
        "",
    ])
    return "\n".join(lines)


def _write_text(path: Path, text: str) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(text)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_reports(inventory: Inventory, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    data = inventory.to_dict()
    _write_text(output / "inventory.json", json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    _write_text(output / "inventory.md", render_markdown(data))
    return data
