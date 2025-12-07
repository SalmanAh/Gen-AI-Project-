@echo off
echo ========================================
echo Audio Scene Analysis Server
echo ========================================
echo.
echo Starting server on http://localhost:8000
echo Web interface: http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
