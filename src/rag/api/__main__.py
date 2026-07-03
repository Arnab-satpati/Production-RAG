from __future__ import annotations

import uvicorn

from rag.config.settings import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "rag.api.app:create_app",
        host=settings.api.host,
        port=settings.api.port,
        workers=settings.api.workers,
        factory=True,
        reload=False,
    )


if __name__ == "__main__":
    main()
