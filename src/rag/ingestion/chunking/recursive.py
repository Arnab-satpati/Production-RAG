from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.config.settings import get_settings
from rag.ingestion.loaders.base import ChunkedDocument, Document

if TYPE_CHECKING:
    from collections.abc import Iterator


class RecursiveChunker:
    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        settings = get_settings().chunking
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size or settings.chunk_size,
            chunk_overlap=chunk_overlap or settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk(self, documents: list[Document]) -> list[ChunkedDocument]:
        chunks: list[ChunkedDocument] = []

        for doc in documents:
            text_chunks = self._splitter.split_text(doc.content)
            total = len(text_chunks)

            for i, text in enumerate(text_chunks):
                metadata = {
                    **doc.metadata,
                    "chunk_index": i,
                    "total_chunks": total,
                    "chunk_size": len(text),
                }
                chunks.append(
                    ChunkedDocument(
                        content=text,
                        metadata=metadata,
                        chunk_index=i,
                        total_chunks=total,
                    ),
                )

        return chunks

    def chunk_stream(self, documents: list[Document]) -> Iterator[ChunkedDocument]:
        for doc in documents:
            text_chunks = self._splitter.split_text(doc.content)
            total = len(text_chunks)

            for i, text in enumerate(text_chunks):
                metadata = {
                    **doc.metadata,
                    "chunk_index": i,
                    "total_chunks": total,
                    "chunk_size": len(text),
                }
                yield ChunkedDocument(
                    content=text,
                    metadata=metadata,
                    chunk_index=i,
                    total_chunks=total,
                )
