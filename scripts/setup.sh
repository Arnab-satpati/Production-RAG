#!/usr/bin/env bash
set -euo pipefail

echo "=== Production RAG - Setup ==="

if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "Installing dependencies..."
uv sync --all-extras

echo "Pulling Ollama models..."
if command -v ollama &> /dev/null; then
    ollama pull llama3.1:8b || echo "Warning: Could not pull Ollama model"
    ollama pull nomic-embed-text || echo "Warning: Could not pull embedding model"
else
    echo "Warning: Ollama not installed. Install from https://ollama.ai"
fi

echo "Starting services..."
docker compose up -d qdrant redis mlflow

echo "Waiting for Qdrant..."
sleep 3

echo "=== Setup Complete ==="
echo "API:      http://localhost:8000"
echo "Docs:     http://localhost:8000/docs"
echo "Metrics:  http://localhost:8000/metrics"
echo "Qdrant:   http://localhost:6333/dashboard"
echo "MLflow:   http://localhost:5000"
