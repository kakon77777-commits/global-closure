"""The shared contract between scanning, reporting, and the command line."""

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Document:
    path: str
    title: str
    characters: int
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class Notice:
    path: str
    reason: str


@dataclass
class Inventory:
    source_name: str
    documents: list[Document] = field(default_factory=list)
    issues: list[Notice] = field(default_factory=list)
    skipped: list[Notice] = field(default_factory=list)

    def to_dict(self) -> dict:
        groups: dict[str, list[str]] = {}
        for document in self.documents:
            groups.setdefault(document.sha256, []).append(document.path)
        duplicates = [
            {"sha256": digest, "paths": paths}
            for digest, paths in groups.items()
            if len(paths) > 1
        ]
        return {
            "schema_version": 1,
            "source_name": self.source_name,
            "summary": {
                "documents": len(self.documents),
                "characters": sum(d.characters for d in self.documents),
                "size_bytes": sum(d.size_bytes for d in self.documents),
                "duplicate_groups": len(duplicates),
                "duplicate_extra_copies": sum(len(g["paths"]) - 1 for g in duplicates),
                "issues": len(self.issues),
                "skipped_entries": len(self.skipped),
            },
            "documents": [asdict(d) for d in self.documents],
            "duplicates": duplicates,
            "issues": [asdict(i) for i in self.issues],
            "skipped": [asdict(i) for i in self.skipped],
        }
