#!/usr/bin/env python3
"""Simple FastAPI app for Railway deployment."""

import os
from fastapi import FastAPI

# Create FastAPI app at module level
app = FastAPI()

# Health route at the very top - must respond instantly
@app.get("/health")
async def health():
    """Health check endpoint that returns HTTP 200 when application is live and ready."""
    return {"ok": True, "mode": "production"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Signals Agent API", "status": "running"}

# Only call uvicorn.run inside if __name__ == "__main__"
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("simple_app:app", host="0.0.0.0", port=port, reload=False)
