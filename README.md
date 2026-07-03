# Production RAG System

Production-grade Retrieval-Augmented Generation system with MLOps best practices.

## Architecture

```
├── src/rag/
│   ├── config/          # Pydantic settings, structured logging
│   ├── ingestion/       # Multi-format document loaders + chunking
│   ├── embeddings/      # Local sentence-transformers embeddings
│   ├── vectorstore/     # Qdrant vector database integration
│   ├── retrieval/       # Semantic retrieval engine
│   ├── generation/      # Ollama LLM integration
│   ├── orchestrator/    # RAG pipeline orchestration
│   ├── guardrails/      # Input/output validation
│   ├── evaluation/      # RAGAS evaluation pipeline
│   ├── monitoring/      # Prometheus metrics, OpenTelemetry tracing
│   ├── api/             # FastAPI with async support
│   └── utils/           # Shared utilities
├── tests/               # Unit, integration, evaluation tests
├── configs/             # Configuration files
├── monitoring/          # Prometheus, Grafana configs
├── scripts/             # Setup and evaluation scripts
├── docker-compose.yml   # Local development
├── docker-compose.prod.yml  # Production deployment
├── Dockerfile           # Multi-stage production build
└── pyproject.toml       # uv project configuration
```

## Quick Start

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup
bash scripts/setup.sh

# Start API
uv run uvicorn rag.api.app:app --reload

# Ingest documents
curl -X POST http://localhost:8000/api/v1/ingest/directory \
  -H "Content-Type: application/json" \
  -d '{"text": "./data"}'

# Query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'
```

## Services

| Service | URL | Purpose |
|---------|-----|---------|
| API | http://localhost:8000 | RAG API |
| Docs | http://localhost:8000/docs | Swagger UI |
| Metrics | http://localhost:8000/metrics | Prometheus metrics |
| Qdrant | http://localhost:6333 | Vector database |
| MLflow | http://localhost:5000 | Experiment tracking |
| Prometheus | http://localhost:9090 | Metrics collection |
| Grafana | http://localhost:3001 | Dashboards |

## MLOps Features

- **Structured Logging** - JSON logs with structlog
- **Prometheus Metrics** - Request latency, retrieval quality, ingestion stats
- **OpenTelemetry Tracing** - Distributed tracing across services
- **MLflow Integration** - Experiment tracking and model registry
- **RAGAS Evaluation** - Automated RAG quality assessment
- **Guardrails** - Input/output validation and sanitization
- **Rate Limiting** - Per-client request throttling
- **Docker Multi-stage** - Optimized production images
- **CI/CD** - GitHub Actions for lint, test, deploy
- **Monitoring Dashboard** - Pre-built Grafana dashboard

## Development

```bash
# Install dev dependencies
uv sync --all-extras

# Lint
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type check
uv run mypy src/

# Test
uv run pytest tests/ -v

# Evaluate RAG quality
bash scripts/evaluate.sh
```
