@echo off
REM CasaOS Deployment Script for Imou Gateway (Windows batch version)

echo.
echo ================================
echo Imou Gateway v2.0.0 - Setup
echo ================================
echo.

REM Create directories
echo [1/4] Creating directories...
if not exist "%AppData%\imou-gateway\database" mkdir "%AppData%\imou-gateway\database"
if not exist "%AppData%\imou-gateway\images" mkdir "%AppData%\imou-gateway\images"
if not exist "%AppData%\imou-gateway\logs" mkdir "%AppData%\imou-gateway\logs"
echo Directories created

REM Create .env file if not exists
echo [2/4] Setting up environment variables...
if not exist "%AppData%\imou-gateway\.env" (
    (
        echo # MQTT Configuration
        echo MQTT_HOST=192.168.1.21
        echo MQTT_PORT=1883
        echo MQTT_USERNAME=
        echo MQTT_PASSWORD=
        echo MQTT_TOPIC_ROOT=imou
        echo.
        echo # Gateway Configuration
        echo GATEWAY_LOG_LEVEL=INFO
        echo GATEWAY_MOTION_TIMEOUT=30
        echo.
        echo # Database Configuration
        echo DATABASE_PATH=/app/database/events.db
        echo.
        echo # Images Configuration
        echo IMAGES_PATH=/app/images
        echo.
        echo # Python Configuration
        echo PYTHONUNBUFFERED=1
    ) > "%AppData%\imou-gateway\.env"
    echo Created .env file
) else (
    echo .env file already exists
)

REM Copy docker-compose.yml
echo [3/4] Setting up docker-compose...
if not exist "%AppData%\imou-gateway\docker-compose.yml" (
    copy docker-compose.yml "%AppData%\imou-gateway\" >nul
    echo Copied docker-compose.yml
) else (
    echo docker-compose.yml already exists
)

echo [4/4] Setup complete!
echo.
echo ================================
echo Next Steps:
echo ================================
echo.
echo 1. Edit %AppData%\imou-gateway\.env with your MQTT settings
echo.
echo 2. Run docker-compose:
echo    cd "%AppData%\imou-gateway"
echo    docker-compose up -d
echo.
echo 3. Verify installation:
echo    curl http://localhost:5000/health
echo.
echo 4. View logs:
echo    docker logs imou-gateway
echo.
pause
