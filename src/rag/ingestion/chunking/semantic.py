from __future__ import annotations

import numpy as np

from rag.config.settings import get_settings
from rag.ingestion.chunking.recursive import RecursiveChunker
from rag.ingestion.loaders.base import ChunkedDocument, Document

# Re-export for convenience
RecursiveChunker = RecursiveChunker


class SemanticChunker:
    def __init__(self, embedding_fn: callable | None = None) -> None:
        self._settings = get_settings().chunking
        self._recursive = RecursiveChunker()
        self._embedding_fn = embedding_fn

    def chunk(self, documents: list[Document]) -> list[ChunkedDocument]:
        if self._embedding_fn is None:
            return self._recursive.chunk(documents)

        chunks: list[ChunkedDocument] = []
        for doc in documents:
            sentences = self._split_sentences(doc.content)
            if len(sentences) <= 3:
                chunks.extend(
                    ChunkedDocument(
                        content=doc.content,
                        metadata={**doc.metadata, "chunk_method": "semantic"},
                        chunk_index=0,
                        total_chunks=1,
                    ),
                )
                continue

            groups = self._group_by_semantics(sentences)
            total = len(groups)
            for i, group in enumerate(groups):
                text = " ".join(group)
                metadata = {
                    **doc.metadata,
                    "chunk_method": "semantic",
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

    def _split_sentences(self, text: str) -> list[str]:
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _group_by_semantics(self, sentences: list[str]) -> list[list[str]]:
        if len(sentences) <= 1:
            return [sentences]

        embeddings = np.array(self._embedding_fn(sentences))
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = float(np.dot(embeddings[i], embeddings[i + 1]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i + 1])
            ))
            similarities.append(sim)

        threshold = np.mean(similarities) - 0.5 * np.std(similarities)
        threshold = max(threshold, 0.3)

        groups: list[list[str]] = []
        current_group: list[str] = [sentences[0]]

        for i, sim in enumerate(similarities):
            if sim < threshold:
                groups.append(current_group)
                current_group = [sentences[i + 1]]
            else:
                current_group.append(sentences[i + 1])

        groups.append(current_group)
        return groups
