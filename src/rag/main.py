"""Entry point for the RAG API server."""
import uvicorn

from rag.api.app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "rag.api.app:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
        reload=True,
        log_level="info",
    )
