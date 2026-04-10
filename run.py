"""
LexGraph AI - Entry Point
Run the FastAPI server with uvicorn.
"""
import os
import sys

# Force UTF-8 output on Windows
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print("")
    print("=" * 42)
    print("     LexGraph AI v1.0.0")
    print("     Legal Knowledge Graph System")
    print("=" * 42)
    print("")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
    )
