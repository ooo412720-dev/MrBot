# app/main.py

from fastapi import FastAPI
from app.api.metrics import metrics
from app.api.health import check_health
from app.core.sentry import init_sentry
from app.core.lifecycle import lifespan


init_sentry()

app = FastAPI(
    title="MrBot",
    version="2.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {"running": True}


@app.get("/health")
async def health():
    return await check_health()


@app.get("/metrics")
async def prometheus():
    return await metrics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
