from __future__ import annotations

import time
from pathlib import Path

import structlog
from fastapi import APIRouter, File, HTTPException, UploadFile

from rag.api.models.schemas import IngestRequest, IngestResponse
from rag.embeddings.service import get_embedding_service
from rag.ingestion.pipeline import IngestionPipeline
from rag.monitoring.metrics import get_metrics_collector
from rag.vectorstore.qdrant import QdrantVectorStore

router = APIRouter(prefix="/api/v1", tags=["ingest"])
logger = structlog.get_logger(__name__)


@router.post("/ingest/text", response_model=IngestResponse)
async def ingest_text(request: IngestRequest) -> IngestResponse:
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required")

    start = time.perf_counter()
    try:
        pipeline = IngestionPipeline()
        chunks = await pipeline.ingest_text(
            text=request.text,
            metadata=request.metadata or {},
        )

        embedding_service = get_embedding_service()
        embeddings = await embedding_service.aembed([c.content for c in chunks])

        vector_store = QdrantVectorStore()
        vector_store.ensure_collection()
        count = vector_store.upsert(chunks, embeddings)

        elapsed = time.perf_counter() - start
        metrics = get_metrics_collector()
        metrics.record_ingestion("text", count)
        metrics.record_request("POST", "/api/v1/ingest/text", "200", elapsed)

        return IngestResponse(
            chunks_ingested=count,
            source="direct_text",
            status="success",
        )

    except Exception as e:
        logger.error("ingest_text_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/ingest/file", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)) -> IngestResponse:  # noqa: B008
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    start = time.perf_counter()
    try:
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / file.filename

        content = await file.read()
        file_path.write_bytes(content)

        pipeline = IngestionPipeline()
        chunks = await pipeline.ingest_file(file_path)

        embedding_service = get_embedding_service()
        embeddings = await embedding_service.aembed([c.content for c in chunks])

        vector_store = QdrantVectorStore()
        vector_store.ensure_collection()
        count = vector_store.upsert(chunks, embeddings)

        elapsed = time.perf_counter() - start
        metrics = get_metrics_collector()
        metrics.record_ingestion(file.filename.rsplit(".", 1)[-1], count)
        metrics.record_request("POST", "/api/v1/ingest/file", "200", elapsed)

        return IngestResponse(
            chunks_ingested=count,
            source=str(file_path),
            status="success",
        )

    except Exception as e:
        logger.error("ingest_file_failed", filename=file.filename, error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/ingest/directory", response_model=IngestResponse)
async def ingest_directory(request: IngestRequest) -> IngestResponse:
    if not request.text:
        raise HTTPException(status_code=400, detail="Directory path is required in 'text' field")

    dir_path = Path(request.text)
    if not dir_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Not a directory: {dir_path}")

    start = time.perf_counter()
    try:
        pipeline = IngestionPipeline()
        chunks = await pipeline.ingest_directory(dir_path)

        if not chunks:
            return IngestResponse(
                chunks_ingested=0,
                source=str(dir_path),
                status="no_files_found",
            )

        embedding_service = get_embedding_service()
        embeddings = await embedding_service.aembed([c.content for c in chunks])

        vector_store = QdrantVectorStore()
        vector_store.ensure_collection()
        count = vector_store.upsert(chunks, embeddings)

        elapsed = time.perf_counter() - start
        metrics = get_metrics_collector()
        metrics.record_ingestion("directory", count)
        metrics.record_request("POST", "/api/v1/ingest/directory", "200", elapsed)

        return IngestResponse(
            chunks_ingested=count,
            source=str(dir_path),
            status="success",
        )

    except Exception as e:
        logger.error("ingest_directory_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e
