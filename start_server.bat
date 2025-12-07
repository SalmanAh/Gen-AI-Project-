@echo off
echo Starting Audio Search API Server...
echo.
echo Models will auto-download on first run (~3GB)
echo This may take 5-10 minutes...
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
