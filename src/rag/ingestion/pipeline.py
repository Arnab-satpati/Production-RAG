from __future__ import annotations

import asyncio
from pathlib import Path

import structlog

from rag.config.settings import get_settings
from rag.ingestion.chunking.recursive import RecursiveChunker
from rag.ingestion.loaders.base import BaseLoader, ChunkedDocument, Document
from rag.ingestion.loaders.code import CodeLoader
from rag.ingestion.loaders.csv_loader import CSVLoader
from rag.ingestion.loaders.docx import DocxLoader
from rag.ingestion.loaders.html import HTMLLoader
from rag.ingestion.loaders.markdown import MarkdownLoader
from rag.ingestion.loaders.pdf import PDFLoader

logger = structlog.get_logger(__name__)

LOADER_REGISTRY: list[type[BaseLoader]] = [
    PDFLoader,
    MarkdownLoader,
    DocxLoader,
    HTMLLoader,
    CSVLoader,
    CodeLoader,
]


def get_loader(file_path: str | Path) -> BaseLoader:
    path = Path(file_path)
    for loader_cls in LOADER_REGISTRY:
        if loader_cls.can_load(path):
            return loader_cls(path)
    raise ValueError(f"No loader found for file: {path}")


class IngestionPipeline:
    def __init__(self, chunker: RecursiveChunker | None = None) -> None:
        self._chunker = chunker or RecursiveChunker()
        self._settings = get_settings()

    async def ingest_file(self, file_path: str | Path) -> list[ChunkedDocument]:
        logger.info("ingesting_file", file_path=str(file_path))
        loader = get_loader(file_path)
        documents = await asyncio.to_thread(loader.load)
        chunks = self._chunker.chunk(documents)
        logger.info(
            "file_ingested",
            file_path=str(file_path),
            pages=len(documents),
            chunks=len(chunks),
        )
        return chunks

    async def ingest_directory(
        self, dir_path: str | Path, patterns: list[str] | None = None,
    ) -> list[ChunkedDocument]:
        path = Path(dir_path)
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")

        patterns = patterns or ["**/*"]
        all_chunks: list[ChunkedDocument] = []

        files = []
        for pattern in patterns:
            files.extend(path.glob(pattern))

        valid_files = [
            f for f in files
            if f.is_file() and not f.name.startswith(".")
        ]

        logger.info("ingesting_directory", dir_path=str(path), file_count=len(valid_files))

        for file_path in valid_files:
            try:
                loader = get_loader(file_path)
                documents = await asyncio.to_thread(loader.load)
                chunks = self._chunker.chunk(documents)
                all_chunks.extend(chunks)
            except (ValueError, Exception) as e:
                logger.warning("skip_file", file_path=str(file_path), error=str(e))

        logger.info(
            "directory_ingested",
            dir_path=str(path),
            total_chunks=len(all_chunks),
        )
        return all_chunks

    async def ingest_text(
        self, text: str, metadata: dict | None = None,
    ) -> list[ChunkedDocument]:
        doc = Document(content=text, metadata=metadata or {})
        return self._chunker.chunk([doc])
