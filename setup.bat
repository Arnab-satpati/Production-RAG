@echo off
echo === Production RAG Setup ===
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed.
    echo Install Docker: https://docs.docker.com/get-docker/
    exit /b 1
)

REM Create .env from .env.docker if it doesn't exist
if not exist .env (
    echo Creating .env from .env.docker...
    copy .env.docker .env
)

echo Starting services...
docker compose up -d

echo.
echo Waiting for Ollama to start...
timeout /t 15 /nobreak >nul

echo Pulling LLM model (llama3.2:1b)...
docker compose exec ollama ollama pull llama3.2:1b

echo Pulling embedding model (nomic-embed-text)...
docker compose exec ollama ollama pull nomic-embed-text

echo.
echo === Setup Complete ===
echo.
echo Services:
echo   Frontend:  http://localhost:3000
echo   API:       http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo   Ollama:    http://localhost:11434
echo   Qdrant:    http://localhost:6333
echo.
echo To stop: docker compose down
echo To view logs: docker compose logs -f
