# Production RAG System

## Overview

The Production RAG (Retrieval-Augmented Generation) system is a production-grade implementation that combines document retrieval with large language model generation.

## Architecture

### Components

1. **Document Loaders**: Support for PDF, Markdown, DOCX, HTML, CSV/Excel, and code files
2. **Chunking Engine**: Recursive and semantic chunking strategies
3. **Embedding Service**: Uses sentence-transformers with nomic-embed-text model
4. **Vector Store**: Qdrant for efficient similarity search
5. **Retrieval Engine**: Semantic search with context building
6. **LLM Generator**: Ollama integration for local LLM inference
7. **Guardrails**: Input validation and output filtering
8. **Monitoring**: Prometheus metrics, structlog, and OpenTelemetry tracing

### Data Flow

1. Documents are loaded and chunked
2. Chunks are embedded using sentence-transformers
3. Embeddings are stored in Qdrant vector database
4. User queries are embedded and used for similarity search
5. Retrieved context is combined with the query
6. LLM generates a response based on the context

## Configuration

All configuration is managed through environment variables or `.env` file:

- `OLLAMA_MODEL`: LLM model name (default: llama3.2:1b)
- `QDRANT_COLLECTION`: Vector store collection name
- `CHUNKING_CHUNK_SIZE`: Maximum chunk size in tokens
- `RETRIEVAL_TOP_K`: Number of results to retrieve

## API Endpoints

- `GET /health`: Health check
- `POST /api/v1/query`: Query the RAG system
- `POST /api/v1/ingest/text`: Ingest text content
- `POST /api/v1/ingest/file`: Ingest a file
- `POST /api/v1/ingest/directory`: Ingest all files in a directory

## Deployment

### Docker

```bash
docker-compose up -d
```

### Local Development

```bash
uv sync
uv run uvicorn rag.api.app:create_app --factory --reload
```
