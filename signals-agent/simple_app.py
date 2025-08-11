#!/usr/bin/env python3
"""Simple FastAPI app for Railway deployment."""

import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"ok": True, "mode": "production"}

@app.get("/")
async def root():
    return {"message": "Signals Agent API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("simple_app:app", host="0.0.0.0", port=port, reload=False)
