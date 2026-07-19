from fastapi import FastAPI

app = FastAPI(title="VoyagerAI API")

@app.get("/health")
async def health():
    return {"status": "ok", "database": "not_checked_yet", "redis": "not_checked_yet"}