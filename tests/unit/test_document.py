from rag.ingestion.loaders.base import ChunkedDocument, Document


def test_document_id():
    doc = Document(content="Hello world", metadata={"source": "test.pdf"})
    assert doc.id.startswith("test.pdf:")
    assert len(doc.id) > 10


def test_document_properties():
    doc = Document(content="Test", metadata={"source": "file.md", "doc_type": "markdown"})
    assert doc.source == "file.md"
    assert doc.doc_type == "markdown"


def test_chunked_document():
    chunk = ChunkedDocument(
        content="Chunk content",
        metadata={"source": "test.pdf"},
        chunk_index=0,
        total_chunks=3,
    )
    assert chunk.chunk_index == 0
    assert chunk.total_chunks == 3
    assert "chunk:0" in chunk.chunk_id
