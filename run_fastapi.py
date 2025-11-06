#!/usr/bin/env python
"""Run the bot with FastAPI instead of aiohttp."""

import sys
import os
import uvicorn

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main_fastapi:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 3978)),
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
