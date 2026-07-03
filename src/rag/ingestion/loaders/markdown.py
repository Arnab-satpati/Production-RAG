from __future__ import annotations

import re

import markdown_it

from rag.ingestion.loaders.base import BaseLoader, Document


class MarkdownLoader(BaseLoader):
    supported_extensions = [".md", ".mdx", ".markdown"]

    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self._md = markdown_it.MarkdownIt()

    def load(self) -> list[Document]:
        raw = self.file_path.read_text(encoding="utf-8")
        base_meta = self._base_metadata()

        sections = self._split_by_headings(raw)
        documents: list[Document] = []

        for i, (heading, content) in enumerate(sections):
            if content.strip():
                metadata = {
                    **base_meta,
                    "section_heading": heading,
                    "section_index": i,
                }
                documents.append(
                    Document(content=content.strip(), metadata=metadata),
                )

        if not documents:
            documents.append(Document(content=raw.strip(), metadata=base_meta))

        return documents

    def _split_by_headings(self, text: str) -> list[tuple[str, str]]:
        heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        matches = list(heading_pattern.finditer(text))

        if not matches:
            return [("", text)]

        sections: list[tuple[str, str]] = []

        if matches[0].start() > 0:
            sections.append(("", text[: matches[0].start()]))

        for i, match in enumerate(matches):
            len(match.group(1))
            heading_text = match.group(2).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            sections.append((heading_text, text[start:end]))

        return sections
