@echo off
REM Gemini Voice Agent - Quick Start Script (Windows)

echo ================================
echo Gemini Voice Agent Setup
echo ================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo WARNING: Please edit .env and add your GEMINI_API_KEY
    pause
    exit /b 1
)

REM Check if GEMINI_API_KEY is set
findstr /C:"GEMINI_API_KEY=AIza" .env >nul
if errorlevel 1 (
    echo WARNING: GEMINI_API_KEY not configured in .env
    echo Please add your Gemini API key to .env file
    pause
    exit /b 1
)

echo Environment configured
echo.

REM Build and start containers
echo Building Docker containers...
docker-compose down
docker-compose build --no-cache

echo Starting services...
docker-compose up -d

REM Wait for services
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check health
echo Checking service health...
curl -s http://localhost:8000/health

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Admin Dashboard: http://localhost:3000
echo API Endpoint: http://localhost:8000/api
echo Documentation: GEMINI_UPGRADE.md
echo.
echo Next steps:
echo 1. Open admin dashboard
echo 2. Create a tenant
echo 3. Add knowledge entries
echo 4. Embed widget on your website
echo.
pause
