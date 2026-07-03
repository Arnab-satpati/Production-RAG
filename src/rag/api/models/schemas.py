from __future__ import annotations

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=10000, description="The question to answer")
    top_k: int | None = Field(None, ge=1, le=20, description="Number of results to retrieve")
    filter_source: str | None = Field(None, description="Filter by document source")
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(None, ge=1, le=8192)


class SourceChunk(BaseModel):
    content: str
    score: float
    source: str
    chunk_id: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    metadata: dict


class IngestRequest(BaseModel):
    text: str | None = Field(None, description="Direct text to ingest")
    metadata: dict | None = Field(None, description="Optional metadata for the document")


class IngestResponse(BaseModel):
    chunks_ingested: int
    source: str
    status: str


class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict[str, str]


class CollectionInfoResponse(BaseModel):
    name: str
    vectors_count: int | None
    points_count: int | None
    status: str


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None
