#!/bin/bash
# CasaOS Deployment Script for Imou Gateway

set -e

echo "================================"
echo "Imou Gateway v2.0.0 - CasaOS Setup"
echo "================================"
echo ""

# Check if running on CasaOS
if [ ! -d "/DATA/AppData" ]; then
    echo "Warning: /DATA/AppData not found. This may not be CasaOS."
    echo "Continuing anyway..."
fi

# Create directories
echo "[1/5] Creating directories..."
mkdir -p /DATA/AppData/imou-gateway/database
mkdir -p /DATA/AppData/imou-gateway/images
mkdir -p /DATA/AppData/imou-gateway/logs
chmod 755 /DATA/AppData/imou-gateway
chmod 755 /DATA/AppData/imou-gateway/database
chmod 755 /DATA/AppData/imou-gateway/images
chmod 755 /DATA/AppData/imou-gateway/logs

# Create .env file
echo "[2/5] Setting up environment variables..."
if [ ! -f "/DATA/AppData/imou-gateway/.env" ]; then
    cat > /DATA/AppData/imou-gateway/.env << EOF
# MQTT Configuration
MQTT_HOST=192.168.1.21
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_TOPIC_ROOT=imou

# Gateway Configuration
GATEWAY_LOG_LEVEL=INFO
GATEWAY_MOTION_TIMEOUT=30

# Database Configuration
DATABASE_PATH=/app/database/events.db

# Images Configuration
IMAGES_PATH=/app/images

# Python Configuration
PYTHONUNBUFFERED=1
EOF
    echo "Created .env file at /DATA/AppData/imou-gateway/.env"
    echo "Please edit it with your MQTT settings"
else
    echo ".env file already exists"
fi

# Copy docker-compose.yml
echo "[3/5] Setting up docker-compose..."
if [ ! -f "/DATA/AppData/imou-gateway/docker-compose.yml" ]; then
    cp docker-compose.yml /DATA/AppData/imou-gateway/
    echo "Copied docker-compose.yml"
else
    echo "docker-compose.yml already exists"
fi

# Create appfile.json symlink for CasaOS
echo "[4/5] Creating CasaOS integration..."
if [ -d "/CasaOS/Apps" ]; then
    ln -sf $(pwd)/appfile.json /CasaOS/Apps/imou-gateway.json 2>/dev/null || true
    echo "CasaOS integration created"
fi

# Show next steps
echo "[5/5] Setup complete!"
echo ""
echo "================================"
echo "Next Steps:"
echo "================================"
echo ""
echo "1. Edit /DATA/AppData/imou-gateway/.env with your MQTT settings"
echo ""
echo "2. Option A - Use Docker Compose:"
echo "   cd /DATA/AppData/imou-gateway"
echo "   docker-compose up -d"
echo ""
echo "3. Option B - Use CasaOS Web UI:"
echo "   - Open CasaOS"
echo "   - Go to App Store"
echo "   - Search for 'Imou Gateway'"
echo "   - Install and configure"
echo ""
echo "4. Verify installation:"
echo "   curl http://localhost:5000/health"
echo ""
echo "5. For troubleshooting, check logs:"
echo "   docker logs imou-gateway"
echo ""
echo "================================"
echo "Documentation:"
echo "================================"
echo "- README.md - Quick start guide"
echo "- CASAOS-GUIDE.md - Detailed CasaOS guide"
echo "- appfile.json - CasaOS app manifest"
echo ""
