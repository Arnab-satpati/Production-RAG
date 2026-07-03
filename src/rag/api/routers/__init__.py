from rag.api.routers.ingest import router as ingest_router
from rag.api.routers.query import router as query_router
from rag.api.routers.system import router as system_router

__all__ = ["query_router", "ingest_router", "system_router"]
