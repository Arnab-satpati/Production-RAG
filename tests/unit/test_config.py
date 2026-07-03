from rag.config.settings import get_settings


def test_settings_loads():
    settings = get_settings()
    assert settings.ollama.model == "llama3.2:3b"
    assert settings.qdrant.port == 6333
    assert settings.chunking.chunk_size == 512
    assert settings.retrieval.top_k == 5


def test_qdrant_settings():
    settings = get_settings()
    assert settings.qdrant.collection == "rag_documents"
    assert settings.qdrant.embedding_dim == 768
