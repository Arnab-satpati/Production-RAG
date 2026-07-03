from __future__ import annotations

from rag.ingestion.loaders.base import BaseLoader, Document

CODE_EXTENSIONS = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".jsx": "jsx", ".tsx": "tsx", ".go": "go", ".rs": "rust",
    ".java": "java", ".kt": "kotlin", ".rb": "ruby",
    ".cpp": "cpp", ".c": "c", ".h": "c_header",
    ".cs": "csharp", ".php": "php", ".swift": "swift",
    ".scala": "scala", ".r": "r", ".R": "r",
    ".sql": "sql", ".sh": "bash", ".bash": "bash",
    ".yaml": "yaml", ".yml": "yaml", ".toml": "toml",
    ".json": "json", ".xml": "xml", ".env": "dotenv",
    ".dockerfile": "dockerfile", ".tf": "terraform",
    ".proto": "protobuf", ".graphql": "graphql",
}


class CodeLoader(BaseLoader):
    supported_extensions = list(CODE_EXTENSIONS.keys())

    def load(self) -> list[Document]:
        raw = self.file_path.read_text(encoding="utf-8", errors="replace")
        base_meta = self._base_metadata()
        lang = CODE_EXTENSIONS.get(self.file_path.suffix.lower(), "unknown")

        documents: list[Document] = []

        if len(raw) > 10000:
            chunks = self._split_by_functions(raw, lang)
            for i, chunk in enumerate(chunks):
                metadata = {
                    **base_meta,
                    "language": lang,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }
                documents.append(Document(content=chunk, metadata=metadata))
        else:
            metadata = {**base_meta, "language": lang}
            documents.append(Document(content=raw.strip(), metadata=metadata))

        return documents

    def _split_by_functions(self, code: str, language: str) -> list[str]:  # noqa: ARG002
        lines = code.split("\n")
        chunks: list[str] = []
        current_chunk: list[str] = []

        for line in lines:
            current_chunk.append(line)
            if (
                len(current_chunk) >= 50
                and line.strip() == ""
                and len("\n".join(current_chunk)) > 1500
            ):
                chunks.append("\n".join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks if chunks else [code]
