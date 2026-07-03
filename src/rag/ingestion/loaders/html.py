from __future__ import annotations

from bs4 import BeautifulSoup

from rag.ingestion.loaders.base import BaseLoader, Document

SKIP_TAGS = {"script", "style", "nav", "footer", "header", "aside"}
MAIN_TAGS = {"article", "main", "section", "div.content", "div.post"}


class HTMLLoader(BaseLoader):
    supported_extensions = [".html", ".htm"]

    def load(self) -> list[Document]:
        raw = self.file_path.read_text(encoding="utf-8", errors="replace")
        return self._parse_html(raw)

    def _parse_html(self, raw: str) -> list[Document]:
        soup = BeautifulSoup(raw, "html.parser")
        base_meta = self._base_metadata()

        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        for tag in soup.find_all(SKIP_TAGS):
            tag.decompose()

        content = self._extract_main_content(soup)
        if not content:
            content = soup.get_text(separator="\n", strip=True)

        documents: list[Document] = []
        if content.strip():
            metadata = {**base_meta, "title": title, "html_length": len(raw)}
            documents.append(Document(content=content, metadata=metadata))

        return documents

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        for selector in MAIN_TAGS:
            elements = soup.select(selector)
            if elements:
                return "\n\n".join(el.get_text(separator="\n", strip=True) for el in elements)
        return ""
