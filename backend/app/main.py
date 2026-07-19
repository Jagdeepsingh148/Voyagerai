import os

import redis.asyncio as redis
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

app = FastAPI(title="VoyagerAI API")

DATABASE_URL = os.environ.get("DATABASE_URL", "")
REDIS_URL = os.environ.get("REDIS_URL", "")

engine = create_async_engine(DATABASE_URL) if DATABASE_URL else None


@app.get("/health")
async def health():
    db_status = "not_configured"
    redis_status = "not_configured"

    if engine:
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            db_status = "ok"
        except Exception as e:
            db_status = f"error: {e}"

    if REDIS_URL:
        try:
            r = redis.from_url(REDIS_URL)
            pong = await r.ping()
            redis_status = "ok" if pong else "error: no pong"
            await r.aclose()
        except Exception as e:
            redis_status = f"error: {e}"

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"

    return {
        "status": overall,
        "database": db_status,
        "redis": redis_status,
    }