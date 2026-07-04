# Imou Gateway - CasaOS Installation & Setup Guide

## Overview

Imou Gateway is a service that acts as a bridge between Imou IP cameras and MQTT brokers. It processes camera webhooks and publishes events to MQTT.

## System Requirements

- CasaOS 0.3.0 or later
- 512MB RAM minimum
- 500MB disk space
- MQTT Broker (Mosquitto recommended)
- Imou camera(s) with webhook support

## Installation Methods

### Method 1: Using CasaOS App Store (Recommended)

1. Open CasaOS Web Interface (`http://your-casaos-ip:80`)
2. Go to **App Store**
3. Search for **Imou Gateway**
4. Click **Install**
5. Configure environment variables:
   - `MQTT_HOST`: Your MQTT broker address (e.g., `192.168.1.21`)
   - `MQTT_PORT`: MQTT port (default: `1883`)
   - `MQTT_USERNAME`: Username (if required)
   - `MQTT_PASSWORD`: Password (if required)
   - `MQTT_TOPIC_ROOT`: Topic prefix (default: `imou`)
   - `GATEWAY_LOG_LEVEL`: Log level (default: `INFO`)
6. Click **Next** and review storage paths
7. Click **Install**

### Method 2: Manual Docker Installation

```bash
# Pull image
docker pull your-registry/imou-gateway:latest

# Create .env file
cp .env.example .env
# Edit .env with your MQTT settings

# Run with docker-compose
docker-compose up -d

# Or run directly
docker run -d \
  --name imou-gateway \
  --restart unless-stopped \
  -p 5000:5000 \
  -v imou-db:/app/database \
  -v imou-images:/app/images \
  -v imou-logs:/app/logs \
  --env-file .env \
  your-registry/imou-gateway:latest
```

### Method 3: Native Installation (Advanced)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create directories
mkdir -p database images logs

# Configure
cp .env.example .env.local
source .env.local

# Run
python app.py
```

## Configuration

### Environment Variables

All configuration is done via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MQTT_HOST` | `192.168.1.21` | MQTT Broker hostname/IP |
| `MQTT_PORT` | `1883` | MQTT Broker port |
| `MQTT_USERNAME` | (empty) | MQTT username (optional) |
| `MQTT_PASSWORD` | (empty) | MQTT password (optional) |
| `MQTT_TOPIC_ROOT` | `imou` | MQTT topic prefix |
| `GATEWAY_LOG_LEVEL` | `INFO` | Log level: DEBUG, INFO, WARNING, ERROR |
| `GATEWAY_MOTION_TIMEOUT` | `30` | Motion detection timeout in seconds |
| `DATABASE_PATH` | `/app/database/events.db` | SQLite database path |
| `IMAGES_PATH` | `/app/images` | Images storage path |
| `PYTHONUNBUFFERED` | `1` | Python output buffering (keep as 1) |

### Imou Camera Configuration

1. Log into your Imou camera's web interface
2. Go to **Settings** → **Network** → **Advanced**
3. Configure **Webhook URL**:
   ```
   http://your-casaos-ip:5000/webhook
   ```
4. Test the connection

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```
Response:
```json
{
  "status": "healthy",
  "mqtt_connected": true,
  "timestamp": "2026-01-01T12:00:00"
}
```

### Get Events
```bash
# Get last 50 events
curl http://localhost:5000/events

# Get last 100 events
curl "http://localhost:5000/events?limit=100"

# Filter by channel
curl "http://localhost:5000/events?channel=1"

# Filter by event type
curl "http://localhost:5000/events?type=motion"
```

### Get Statistics
```bash
curl http://localhost:5000/stats
```

### Cleanup Old Events (Admin)
```bash
# Remove events older than 30 days
curl -X POST "http://localhost:5000/events/cleanup?days=30"
```

### Root Endpoint
```bash
curl http://localhost:5000/
```

## MQTT Topics

Events are published to these MQTT topics:

- **Raw Events**: `imou/raw` - All raw webhook data
- **Processed Events**: `imou/event` - Processed event data
- **Motion Detection**: `imou/camera/{channel}/motion` - Motion on/off events

### Example MQTT Messages

Motion Event:
```
Topic: imou/camera/1/motion
Payload: ON  # or OFF
```

Event Data:
```
Topic: imou/event
Payload: {
  "channel": 1,
  "type": "motion",
  "description": "Motion detected on channel 1",
  "timestamp": "2026-01-01T12:00:00"
}
```

## Monitoring

### Logs

Logs are stored in `/DATA/AppData/imou-gateway/logs/imou-gateway.log`

View logs in CasaOS:
1. Go to **My Apps** → **Imou Gateway**
2. Click **Logs** tab

Or via command line:
```bash
docker logs imou-gateway -f
```

### Database Maintenance

The application automatically uses WAL (Write-Ahead Logging) for better concurrency.

View statistics:
```bash
curl http://localhost:5000/stats
```

Cleanup old events:
```bash
# Keep only last 30 days
curl -X POST "http://localhost:5000/events/cleanup?days=30"
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker logs imou-gateway
```

Common issues:
- MQTT connection failed - Check MQTT_HOST and MQTT_PORT
- Permission denied - Check volume permissions
- Port 5000 already in use - Change port in docker-compose.yml

### MQTT not connecting

1. Verify MQTT broker is running:
   ```bash
   docker ps | grep mosquitto
   ```

2. Test MQTT connection:
   ```bash
   mosquitto_sub -h your-mqtt-host -t imou/# -v
   ```

3. Check credentials:
   ```bash
   docker logs imou-gateway | grep MQTT
   ```

### High disk usage

Database may be growing too quickly:

1. Check database size:
   ```bash
   ls -lh /DATA/AppData/imou-gateway/database/
   ```

2. Cleanup old events:
   ```bash
   curl -X POST "http://localhost:5000/events/cleanup?days=7"
   ```

3. Enable automatic cleanup (add to cron):
   ```bash
   0 2 * * * curl -X POST "http://localhost:5000/events/cleanup?days=30"
   ```

## Performance Optimization

For optimal performance on CasaOS:

1. **Memory**: Service typically uses 50-100MB RAM
2. **Storage**: Database WAL mode is enabled for better concurrency
3. **Network**: Uses persistent MQTT connection
4. **Logging**: Set to INFO level for production, DEBUG for troubleshooting

## Upgrade

To upgrade to a new version:

1. In CasaOS, go to **My Apps** → **Imou Gateway**
2. Click the **⋯** menu → **Upgrade**
3. Confirm the upgrade

Or manually:
```bash
docker-compose down
docker pull your-registry/imou-gateway:latest
docker-compose up -d
```

## Support & Issues

- GitHub Issues: https://github.com/your-org/imou-gateway/issues
- Documentation: https://github.com/your-org/imou-gateway/wiki
- MQTT Documentation: https://mqtt.org/

## License

See LICENSE file in the repository.

## Changelog

### v2.0.0
- Docker support
- CasaOS integration
- Database WAL mode optimization
- Improved logging
- Graceful shutdown
- API statistics endpoint
- Event cleanup endpoint
- Environment variable configuration
