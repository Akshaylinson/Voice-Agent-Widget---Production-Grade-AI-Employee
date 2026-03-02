@echo off
REM Deploy new client instance
REM Usage: deploy-client.bat <client_id> <port>

set CLIENT_ID=%1
set PORT=%2

if "%CLIENT_ID%"=="" (
    echo Usage: deploy-client.bat ^<client_id^> ^<port^>
    echo Example: deploy-client.bat client2 8002
    exit /b 1
)

if "%PORT%"=="" (
    echo Usage: deploy-client.bat ^<client_id^> ^<port^>
    echo Example: deploy-client.bat client2 8002
    exit /b 1
)

echo Deploying Voice Agent for client: %CLIENT_ID% on port: %PORT%

REM Create client-specific docker-compose file
(
echo version: '3.8'
echo.
echo services:
echo   voice-agent-%CLIENT_ID%:
echo     build: ./backend
echo     container_name: voice-agent-%CLIENT_ID%
echo     environment:
echo       - CLIENT_ID=%CLIENT_ID%
echo       - DATABASE_URL=postgresql://postgres:postgres@db-%CLIENT_ID%:5432/voice_agent
echo       - OPENAI_API_KEY=${OPENAI_API_KEY}
echo       - JWT_SECRET=${JWT_SECRET}
echo       - PORT=8000
echo     ports:
echo       - "%PORT%:8000"
echo     depends_on:
echo       - db-%CLIENT_ID%
echo     networks:
echo       - %CLIENT_ID%-network
echo     restart: unless-stopped
echo.
echo   db-%CLIENT_ID%:
echo     image: postgres:15-alpine
echo     container_name: db-%CLIENT_ID%
echo     environment:
echo       - POSTGRES_DB=voice_agent
echo       - POSTGRES_USER=postgres
echo       - POSTGRES_PASSWORD=postgres
echo     volumes:
echo       - %CLIENT_ID%-db-data:/var/lib/postgresql/data
echo     networks:
echo       - %CLIENT_ID%-network
echo     restart: unless-stopped
echo.
echo volumes:
echo   %CLIENT_ID%-db-data:
echo.
echo networks:
echo   %CLIENT_ID%-network:
echo     driver: bridge
) > docker-compose-%CLIENT_ID%.yml

REM Deploy
docker-compose -f docker-compose-%CLIENT_ID%.yml up -d

echo.
echo ✅ Client %CLIENT_ID% deployed successfully!
echo API URL: http://localhost:%PORT%/api
echo Widget URL: http://localhost:%PORT%/voice-agent-widget.js
