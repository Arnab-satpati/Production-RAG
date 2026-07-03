#!/bin/bash
set -e

echo "=== Production RAG Setup ==="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed."
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose is not available."
    echo "Install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create .env from .env.docker if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from .env.docker..."
    cp .env.docker .env
fi

echo "Starting services..."
docker compose up -d

echo ""
echo "Waiting for Ollama to start..."
sleep 10

echo "Pulling LLM model (llama3.2:1b)..."
docker compose exec ollama ollama pull llama3.2:1b

echo "Pulling embedding model (nomic-embed-text)..."
docker compose exec ollama ollama pull nomic-embed-text

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Services:"
echo "  Frontend:  http://localhost:3000"
echo "  API:       http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  Ollama:    http://localhost:11434"
echo "  Qdrant:    http://localhost:6333"
echo ""
echo "To stop: docker compose down"
echo "To view logs: docker compose logs -f"
