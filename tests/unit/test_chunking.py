from rag.ingestion.chunking.recursive import RecursiveChunker
from rag.ingestion.loaders.base import Document


def test_recursive_chunker_basic():
    chunker = RecursiveChunker(chunk_size=100, chunk_overlap=10)
    doc = Document(content="A" * 500, metadata={"source": "test"})
    chunks = chunker.chunk([doc])
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.content) <= 110


def test_recursive_chunker_small_text():
    chunker = RecursiveChunker(chunk_size=512)
    doc = Document(content="Short text", metadata={"source": "test"})
    chunks = chunker.chunk([doc])
    assert len(chunks) == 1
    assert chunks[0].content == "Short text"


def test_recursive_chunker_multiple_docs():
    chunker = RecursiveChunker(chunk_size=100)
    docs = [
        Document(content="First document " * 20, metadata={"source": "a.md"}),
        Document(content="Second document " * 20, metadata={"source": "b.md"}),
    ]
    chunks = chunker.chunk(docs)
    assert len(chunks) > 2
    sources = {c.source for c in chunks}
    assert "a.md" in sources
    assert "b.md" in sources
