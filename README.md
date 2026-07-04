# Imou Gateway v2.0.0

Imou Gateway là một dịch vụ kết nối camera Imou với MQTT broker. Nó nhận webhook từ camera, xử lý sự kiện, lưu trữ vào database, và publish lên MQTT.

## Tính năng

- ✅ Kết nối MQTT với auto-reconnect
- ✅ API webhook để nhận sự kiện từ camera
- ✅ Lưu trữ sự kiện vào SQLite database (WAL mode)
- ✅ Health check endpoint
- ✅ API để lấy danh sách sự kiện
- ✅ Thống kê database
- ✅ Cleanup sự kiện cũ
- ✅ Docker support
- ✅ CasaOS integration
- ✅ Graceful shutdown
- ✅ Logging đầy đủ

## Yêu cầu

- Python 3.10+ hoặc Docker/CasaOS
- MQTT Broker (Mosquitto recommended)
- Camera Imou với webhook support

## Cài đặt Nhanh

### 1. CasaOS (Recommended)
```bash
# Mở CasaOS → App Store → Tìm "Imou Gateway" → Install
# Cấu hình MQTT settings
# Hoàn tất!
```

### 2. Docker
```bash
# Clone repository
git clone https://github.com/your-org/imou-gateway.git
cd imou-gateway

# Cấu hình
cp .env.example .env
# Sửa .env với MQTT settings

# Chạy
docker-compose up -d
```

### 3. Native Python
```bash
# Cài dependencies
pip install -r requirements.txt

# Tạo thư mục
mkdir -p database images logs

# Cấu hình
export MQTT_HOST=192.168.1.21
export MQTT_PORT=1883

# Chạy
python app.py
```

## Cấu Hình

### Environment Variables

| Biến | Mặc định | Mô tả |
|------|---------|-------|
| `MQTT_HOST` | `192.168.1.21` | MQTT Broker IP/hostname |
| `MQTT_PORT` | `1883` | MQTT port |
| `MQTT_USERNAME` | (empty) | MQTT username (tuỳ chọn) |
| `MQTT_PASSWORD` | (empty) | MQTT password (tuỳ chọn) |
| `MQTT_TOPIC_ROOT` | `imou` | MQTT topic prefix |
| `GATEWAY_LOG_LEVEL` | `INFO` | Log level: DEBUG, INFO, WARNING, ERROR |
| `GATEWAY_MOTION_TIMEOUT` | `30` | Motion timeout (seconds) |
| `DATABASE_PATH` | `/app/database/events.db` | SQLite path |
| `IMAGES_PATH` | `/app/images` | Images storage path |

### Cấu Hình Camera Imou

1. Đăng nhập vào camera web interface
2. Vào **Settings** → **Network** → **Advanced**
3. Cấu hình **Webhook URL**:
   ```
   http://your-casaos-ip:5000/webhook
   ```
4. Test kết nối

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
# 50 sự kiện gần đây
curl http://localhost:5000/events

# 100 sự kiện
curl "http://localhost:5000/events?limit=100"

# Lọc theo channel
curl "http://localhost:5000/events?channel=1"

# Lọc theo type
curl "http://localhost:5000/events?type=motion"
```

### Statistics
```bash
curl http://localhost:5000/stats
```

### Cleanup Old Events
```bash
# Xóa sự kiện > 30 ngày
curl -X POST "http://localhost:5000/events/cleanup?days=30"
```

## MQTT Topics

- `imou/event` - Processed events
- `imou/raw` - Raw webhook data
- `imou/camera/{channel}/motion` - Motion detection (ON/OFF)

## Troubleshooting

### MQTT không kết nối
1. Kiểm tra `MQTT_HOST` và `MQTT_PORT`
2. Test connection: `mosquitto_sub -h <host> -t imou/#`
3. Xem logs: `docker logs imou-gateway`

### Database lớn
```bash
# Cleanup sự kiện cũ
curl -X POST "http://localhost:5000/events/cleanup?days=7"
```

### Port 5000 đang dùng
Sửa port trong `docker-compose.yml` hoặc `app.py`

## Monitoring

### Logs
```bash
# CasaOS
# My Apps → Imou Gateway → Logs tab

# Docker
docker logs imou-gateway -f

# File
tail -f /DATA/AppData/imou-gateway/logs/imou-gateway.log
```

### Stats
```bash
curl http://localhost:5000/stats | jq
```

## Performance

- Memory: 50-100MB
- CPU: Low (idle most of the time)
- Database: WAL mode for better concurrency
- Auto-reconnect: Yes

## File Structure

```
imou-gateway-v2.0.0/
├── app.py                 # Flask app
├── config.py              # Configuration
├── config.json            # Config file
├── database.py            # Database management
├── mqtt_client.py         # MQTT client
├── parser.py              # Webhook parser
├── requirements.txt       # Dependencies
├── Dockerfile             # Docker image
├── docker-compose.yml     # Docker compose
├── appfile.json           # CasaOS app file
├── .env.example           # Environment example
├── CASAOS-GUIDE.md        # CasaOS guide
└── test_app.py            # Unit tests
```

## Testing

```bash
# Run unit tests
python test_app.py

# Test endpoints
curl http://localhost:5000/health
curl -X POST http://localhost:5000/webhook -H "Content-Type: application/json" \
  -d '{"channel": 1, "type": "motion", "description": "Test"}'
```

## Upgrade

### CasaOS
My Apps → Imou Gateway → ⋯ → Upgrade

### Docker
```bash
docker-compose down
docker pull your-registry/imou-gateway:latest
docker-compose up -d
```

## Support

- GitHub: https://github.com/your-org/imou-gateway
- Issues: https://github.com/your-org/imou-gateway/issues
- Wiki: https://github.com/your-org/imou-gateway/wiki

## Changelog

### v2.0.0
- ✅ Docker & CasaOS support
- ✅ Database WAL optimization
- ✅ Auto-reconnect MQTT
- ✅ Graceful shutdown
- ✅ Event statistics
- ✅ Event cleanup
- ✅ Enhanced logging
- ✅ Environment variables

## License

See LICENSE file.

## github update
git status
git add .
git commit -m "feat: mô tả thay đổi"
git push origin main

## Contributed By

Copilot - GitHub AI Assistant

---

**Documentation**: Xem [CASAOS-GUIDE.md](CASAOS-GUIDE.md) để chi tiết hơn.


