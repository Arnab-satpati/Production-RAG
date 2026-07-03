from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from rag.ingestion.loaders.base import BaseLoader, Document


class PDFLoader(BaseLoader):
    supported_extensions = [".pdf"]

    def load(self) -> list[Document]:
        reader = PdfReader(str(self.file_path))
        base_meta = self._base_metadata()
        documents: list[Document] = []

        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            if text.strip():
                metadata = {
                    **base_meta,
                    "page_number": page_num,
                    "total_pages": len(reader.pages),
                }
                documents.append(Document(content=text.strip(), metadata=metadata))

        return documents

    @classmethod
    def can_load(cls, file_path: str | Path) -> bool:
        path = Path(file_path)
        if path.suffix.lower() in cls.supported_extensions:
            return True
        try:
            with path.open("rb") as f:
                header = f.read(5)
                return header == b"%PDF-"
        except OSError:
            return False
