from __future__ import annotations

import pandas as pd

from rag.ingestion.loaders.base import BaseLoader, Document


class CSVLoader(BaseLoader):
    supported_extensions = [".csv", ".tsv", ".xlsx", ".xls"]

    def load(self) -> list[Document]:
        ext = self.file_path.suffix.lower()

        if ext in (".xlsx", ".xls"):
            df = pd.read_excel(str(self.file_path))
        else:
            sep = "\t" if ext == ".tsv" else ","
            df = pd.read_csv(str(self.file_path), sep=sep)

        base_meta = self._base_metadata()
        documents: list[Document] = []

        columns = list(df.columns)
        for idx, row in df.iterrows():
            row_text = "\n".join(
                f"{col}: {row[col]}" for col in columns if pd.notna(row[col])
            )
            if row_text.strip():
                metadata = {
                    **base_meta,
                    "row_index": int(idx),
                    "columns": columns,
                }
                documents.append(Document(content=row_text, metadata=metadata))

        return documents
