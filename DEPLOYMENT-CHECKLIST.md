# Imou Gateway v2.0.0 - Deployment Checklist for CasaOS

## Project Files Summary

### Core Application
- ✅ `app.py` - Flask app với graceful shutdown, health checks, comprehensive logging
- ✅ `config.py` - Configuration manager với env variable support
- ✅ `config.json` - Configuration file
- ✅ `database.py` - SQLite manager với WAL optimization, indexing
- ✅ `mqtt_client.py` - MQTT client với auto-reconnect
- ✅ `parser.py` - Webhook event parser
- ✅ `requirements.txt` - Python dependencies

### Docker & Deployment
- ✅ `Dockerfile` - Optimized Python 3.11 slim image
- ✅ `docker-compose.yml` - Full service definition with volumes, health check, logging
- ✅ `appfile.json` - CasaOS AppStore manifest
- ✅ `.env.example` - Environment variables template

### Setup & Installation
- ✅ `setup-casaos.sh` - Linux/Mac setup script
- ✅ `setup-casaos.bat` - Windows setup script
- ✅ `run.sh` - Native Linux/Mac startup script
- ✅ `run.bat` - Native Windows startup script

### Documentation
- ✅ `README.md` - Quick start guide (Vietnamese)
- ✅ `CASAOS-GUIDE.md` - Detailed CasaOS guide
- ✅ `CASAOS-OPTIMIZATION.md` - Performance optimization guide
- ✅ `DEPLOYMENT-CHECKLIST.md` - This file

### Testing
- ✅ `test_app.py` - Unit tests (5/5 PASS)
- ✅ `test_config.py` - Config tests
- ✅ `test_mqtt.py` - MQTT tests

## Pre-Deployment Checklist

### System Requirements
- [ ] CasaOS 0.3.0 or later installed
- [ ] Docker daemon running
- [ ] At least 512MB free RAM
- [ ] At least 500MB free disk space
- [ ] Network connectivity to MQTT broker

### Preparation
- [ ] MQTT broker IP address known
- [ ] MQTT port confirmed (default: 1883)
- [ ] MQTT credentials (if required)
- [ ] Understand webhook URL format
- [ ] Camera model supports webhooks

## Installation Steps

### Step 1: Clone/Download Project
```bash
cd /DATA/AppData
git clone https://github.com/your-org/imou-gateway.git
cd imou-gateway
```

### Step 2: Run Setup Script
**Linux/Mac:**
```bash
bash setup-casaos.sh
```

**Windows:**
```cmd
setup-casaos.bat
```

### Step 3: Configure Environment
```bash
# Edit .env file
nano /DATA/AppData/imou-gateway/.env
```

Required configurations:
```
MQTT_HOST=your-mqtt-broker-ip
MQTT_PORT=1883
MQTT_USERNAME=username (or leave empty)
MQTT_PASSWORD=password (or leave empty)
MQTT_TOPIC_ROOT=imou
```

### Step 4: Deploy Container
```bash
cd /DATA/AppData/imou-gateway
docker-compose up -d
```

### Step 5: Verify Installation
```bash
# Check container status
docker ps | grep imou-gateway

# Check health
curl http://localhost:5000/health

# View logs
docker logs imou-gateway -f
```

## Post-Deployment Verification

### 1. API Endpoints Working
```bash
# Test root endpoint
curl http://localhost:5000/

# Test health check
curl http://localhost:5000/health

# Test events
curl http://localhost:5000/events

# Test statistics
curl http://localhost:5000/stats
```

### 2. MQTT Connection
```bash
# Check logs for MQTT connection
docker logs imou-gateway | grep -i mqtt

# Should show:
# "Connecting to MQTT ..."
# "MQTT connected successfully"
```

### 3. Database Setup
```bash
# Verify database exists
docker exec imou-gateway ls -lh /app/database/

# Check database schema
docker exec imou-gateway sqlite3 /app/database/events.db ".tables"
```

### 4. Log File Generation
```bash
# Verify log file
docker exec imou-gateway ls -lh /app/logs/

# View recent logs
docker exec imou-gateway tail -f /app/logs/imou-gateway.log
```

## Camera Configuration

### Imou Camera Webhook Setup

1. **Access Camera Web Interface**
   - Open browser to: `http://camera-ip`
   - Login with camera credentials

2. **Navigate to Settings**
   - Settings → Network → Advanced

3. **Configure Webhook URL**
   - Webhook URL: `http://casaos-ip:5000/webhook`
   - Method: POST
   - Content-Type: application/json

4. **Test Connection**
   - Click "Test" or "Send Test"
   - Check logs: `docker logs imou-gateway`
   - Should see: "Webhook received" message

5. **Enable Events**
   - Motion Detection: ON
   - Save settings

## CasaOS App Store Installation (Alternative)

1. Open CasaOS Web UI (http://casaos-ip:80)
2. Go to App Store
3. Search for "Imou Gateway"
4. Click "Install"
5. Configure environment variables:
   - MQTT_HOST
   - MQTT_PORT
   - MQTT_USERNAME
   - MQTT_PASSWORD
   - MQTT_TOPIC_ROOT
6. Click "Install" and wait for completion

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs imou-gateway

# Check docker-compose syntax
docker-compose config

# Rebuild image
docker-compose up -d --build
```

### MQTT Connection Failed
```bash
# Verify MQTT is running
docker exec imou-gateway ping -c 1 <MQTT_HOST>

# Test MQTT connectivity
mosquitto_sub -h <MQTT_HOST> -t imou/# -v

# Check credentials
docker logs imou-gateway | grep MQTT
```

### Port 5000 Already in Use
```bash
# Change port in docker-compose.yml
# Find: ports: - "5000:5000"
# Change to: "5001:5000"

docker-compose up -d
```

### Database Issues
```bash
# Check database integrity
docker exec imou-gateway \
  sqlite3 /app/database/events.db "PRAGMA integrity_check;"

# Backup and reset
docker exec imou-gateway \
  cp /app/database/events.db /app/database/events.db.backup
```

### High Memory Usage
```bash
# Check memory usage
docker stats imou-gateway

# Reduce log level
# Edit .env: GATEWAY_LOG_LEVEL=WARNING

# Cleanup old events
curl -X POST http://localhost:5000/events/cleanup?days=7
```

## Performance Optimization

### Enable Debug Logging (Development)
```bash
# Edit /DATA/AppData/imou-gateway/.env
GATEWAY_LOG_LEVEL=DEBUG

docker-compose restart
```

### Disable Debug Logging (Production)
```bash
# Edit .env
GATEWAY_LOG_LEVEL=WARNING

docker-compose restart
```

### Auto-Cleanup Old Events
```bash
# Create cron job to cleanup monthly
# Add to system crontab:
0 2 * * * curl -X POST http://localhost:5000/events/cleanup?days=30
```

### Monitor Resource Usage
```bash
# Watch container stats
docker stats --no-stream imou-gateway

# Set memory limit in docker-compose.yml:
# mem_limit: 256m
# cpus: 0.5
```

## Backup & Recovery

### Backup Database
```bash
# Manual backup
docker exec imou-gateway \
  cp /app/database/events.db /app/database/events.db.$(date +%Y%m%d)

# Automated daily backup
0 0 * * * docker exec imou-gateway \
  cp /app/database/events.db /app/database/events.db.$(date +\%Y\%m\%d)
```

### Restore from Backup
```bash
# Stop container
docker-compose down

# Restore backup
cp /DATA/AppData/imou-gateway/database/events.db.20260704 \
   /DATA/AppData/imou-gateway/database/events.db

# Start container
docker-compose up -d
```

## Upgrade Procedure

### From v2.0.0 to v2.1.0 (Future)
```bash
# 1. Backup current database
cp /DATA/AppData/imou-gateway/database/events.db \
   /DATA/AppData/imou-gateway/database/events.db.backup

# 2. Pull latest code
git pull origin main

# 3. Update docker image
docker-compose down
docker pull your-registry/imou-gateway:latest

# 4. Start new version
docker-compose up -d

# 5. Verify
curl http://localhost:5000/health
```

## Monitoring & Alerts

### Health Check Script
```bash
#!/bin/bash
# check_imou.sh

HEALTH=$(curl -s http://localhost:5000/health)
if echo "$HEALTH" | grep -q '"status":"healthy"'; then
    echo "OK: Imou Gateway is healthy"
    exit 0
else
    echo "CRITICAL: Imou Gateway is not healthy"
    docker logs imou-gateway | tail -20
    exit 1
fi
```

### Add to Crontab for Monitoring
```bash
*/5 * * * * /path/to/check_imou.sh || mail -s "Imou Gateway Alert" admin@example.com
```

## Security Hardening

### 1. Firewall Configuration
```bash
# Only allow local access to port 5000
sudo ufw allow from 192.168.1.0/24 to any port 5000

# Or block all external access
sudo ufw deny from any to any port 5000
```

### 2. MQTT Authentication
```bash
# Use strong MQTT credentials
# Edit .env:
MQTT_USERNAME=imougateway
MQTT_PASSWORD=<strong-password>
```

### 3. Enable API Key for Admin Endpoints
```python
# In app.py, add API key check for cleanup endpoint
api_key = request.args.get('api_key')
if api_key != os.getenv('API_KEY'):
    return jsonify({"error": "Unauthorized"}), 401
```

## Final Checklist

- [ ] CasaOS system ready
- [ ] Docker daemon running
- [ ] MQTT broker configured
- [ ] Environment variables set
- [ ] Container deployed
- [ ] Health check passing
- [ ] Database initialized
- [ ] Logs generating
- [ ] MQTT connection established
- [ ] Camera webhook configured
- [ ] Events being received
- [ ] Database growing (verify)
- [ ] Performance acceptable
- [ ] Monitoring enabled
- [ ] Backups scheduled
- [ ] Documentation reviewed

## Support & Resources

- **GitHub Repository**: https://github.com/your-org/imou-gateway
- **Issue Tracker**: https://github.com/your-org/imou-gateway/issues
- **Wiki**: https://github.com/your-org/imou-gateway/wiki
- **CasaOS Forum**: https://www.casaos.io/
- **Docker Docs**: https://docs.docker.com/
- **MQTT Documentation**: https://mqtt.org/

## Next Steps

1. ✅ Review this checklist
2. ✅ Follow installation steps
3. ✅ Configure camera webhooks
4. ✅ Verify events are flowing
5. ✅ Monitor logs and performance
6. ✅ Schedule maintenance tasks
7. ✅ Setup backups

---

**Status**: READY FOR DEPLOYMENT ✅
**Version**: 2.0.0
**Last Updated**: 2026-07-04
