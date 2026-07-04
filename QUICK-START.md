# QUICK START - Imou Gateway on CasaOS

## 5 Minute Setup

### 1. Copy Files to CasaOS
```bash
# SSH into CasaOS
ssh root@casaos-ip

# Create app directory
mkdir -p /DATA/AppData/imou-gateway
cd /DATA/AppData/imou-gateway

# Copy docker-compose.yml and .env.example
# (Or git clone if available)
```

### 2. Create .env Configuration
```bash
# Copy template
cp .env.example .env

# Edit with your MQTT details
nano .env

# Change these values:
# MQTT_HOST=192.168.1.21        (Your MQTT broker IP)
# MQTT_PORT=1883                 (Usually 1883)
# MQTT_USERNAME=                 (Your MQTT username)
# MQTT_PASSWORD=                 (Your MQTT password)
```

### 3. Start the Service
```bash
docker-compose up -d
```

### 4. Verify It's Running
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "mqtt_connected": true,
  "timestamp": "2026-07-04T..."
}
```

### 5. Configure Camera
In your Imou camera settings:
- Webhook URL: `http://casaos-ip:5000/webhook`
- Method: POST
- Click "Test" to verify

## Common Issues & Quick Fixes

### "Connection refused"
```bash
# Check if container is running
docker ps | grep imou-gateway

# If not running, check logs
docker logs imou-gateway
```

### "MQTT connection failed"
```bash
# Verify MQTT broker is reachable
docker exec imou-gateway ping -c 1 192.168.1.21

# Test MQTT manually
docker exec imou-gateway mosquitto_sub -h 192.168.1.21 -t imou/#
```

### "Port 5000 already in use"
```bash
# Change port in docker-compose.yml
# Change: "5000:5000"
# To: "5001:5000"

docker-compose up -d
```

## Check If Events Are Working

```bash
# Get recent events
curl http://localhost:5000/events | jq

# Get statistics
curl http://localhost:5000/stats | jq
```

## View Logs

```bash
# Real-time logs
docker logs imou-gateway -f

# Last 100 lines
docker logs imou-gateway --tail 100
```

## Useful Commands

```bash
# Stop the service
docker-compose down

# Restart
docker-compose restart

# Update to latest version
docker-compose pull
docker-compose up -d

# Remove old data and start fresh
docker-compose down -v
docker-compose up -d

# Backup database
cp /DATA/AppData/imou-gateway/database/events.db \
   /DATA/AppData/imou-gateway/database/events.db.backup

# Cleanup old events
curl -X POST http://localhost:5000/events/cleanup?days=30
```

## Detailed Documentation

- **Full Guide**: See `CASAOS-GUIDE.md`
- **Optimization**: See `CASAOS-OPTIMIZATION.md`
- **Deployment**: See `DEPLOYMENT-CHECKLIST.md`
- **README**: See `README.md`

## Need Help?

1. Check logs: `docker logs imou-gateway -f`
2. Test health: `curl http://localhost:5000/health`
3. Verify MQTT: `docker logs imou-gateway | grep MQTT`
4. GitHub Issues: https://github.com/your-org/imou-gateway/issues

---

That's it! Your Imou Gateway should now be running on CasaOS! 🎉
