import uvicorn
from rag.api.app import create_app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000, workers=1)
