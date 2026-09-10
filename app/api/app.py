from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title="RepairFlow API",
        version="1.0.0",
        description="Backend API for RepairFlow renovation CRM.",
    )
    app.include_router(router)

    @app.get("/health")
    async def health():
        return JSONResponse({"status": "ok"})

    return app


app = create_app()
