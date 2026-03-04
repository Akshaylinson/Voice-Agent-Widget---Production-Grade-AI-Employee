@echo off
echo ========================================
echo   Voice Widget Fix - Restart Backend
echo ========================================
echo.

echo [1/3] Stopping backend...
docker-compose stop backend

echo.
echo [2/3] Starting backend...
docker-compose up -d backend

echo.
echo [3/3] Checking status...
timeout /t 3 >nul
docker-compose ps backend

echo.
echo ========================================
echo   Backend restarted successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Clear browser cache (Ctrl+Shift+Delete)
echo 2. Reload CodelessAi.html or demo_acme.html
echo 3. Click avatar to test
echo 4. Check console (F12) for logs
echo.
echo Expected logs:
echo   - [WIDGET] Playing Google Cloud TTS audio (if configured)
echo   - [WIDGET] Playing browser TTS (fallback)
echo.
pause
