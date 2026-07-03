from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Document:
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]
        source = self.metadata.get("source", "unknown")
        return f"{source}:{content_hash}"

    @property
    def source(self) -> str:
        return self.metadata.get("source", "unknown")

    @property
    def doc_type(self) -> str:
        return self.metadata.get("doc_type", "unknown")


@dataclass(frozen=True)
class ChunkedDocument(Document):
    chunk_index: int = 0
    total_chunks: int = 1
    chunk_id: str = ""

    def __post_init__(self) -> None:
        if not self.chunk_id:
            object.__setattr__(
                self, "chunk_id", f"{self.id}:chunk:{self.chunk_index}",
            )


class BaseLoader:
    supported_extensions: list[str] = []

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

    def load(self) -> list[Document]:
        raise NotImplementedError

    def _base_metadata(self) -> dict[str, Any]:
        stat = self.file_path.stat()
        return {
            "source": str(self.file_path),
            "filename": self.file_path.name,
            "extension": self.file_path.suffix.lower(),
            "doc_type": self.__class__.__name__.replace("Loader", "").lower(),
            "file_size_bytes": stat.st_size,
            "file_hash": hashlib.md5(  # noqa: S324
                self.file_path.read_bytes(),
            ).hexdigest(),
        }

    @classmethod
    def can_load(cls, file_path: str | Path) -> bool:
        return Path(file_path).suffix.lower() in cls.supported_extensions
