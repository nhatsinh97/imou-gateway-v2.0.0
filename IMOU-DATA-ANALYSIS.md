# Phân tích dữ liệu từ Camera Imou thực

Dữ liệu mới nhất từ /events:

## Event ID 19 (Mới nhất - từ Camera)
```
{
  "channel": 0,
  "description": "",
  "event_type": "1",
  "id": 19,
  "timestamp": "2026-07-04 14:31:18"
}
```

### Phân tích:

1. **Channel: 0** 
   - Imou camera gửi channel = 0 (device-wide event, không phải camera channel)
   - Cần mapping: channel 0 → main channel hoặc device channel

2. **Event_type: "1"**
   - Đây là mã sự kiện từ Imou camera (không phải tên readable)
   - Cần mapping: "1" → event type thực (motion, alarm, etc.)
   - Các mã có thể: 1=motion, 2=person, 3=alarm, vv

3. **Description: "" (trống)**
   - Camera không gửi description
   - Cần tạo description từ event_type

4. **Timestamp: "2026-07-04 14:31:18"**
   - Format: YYYY-MM-DD HH:MM:SS
   - Khác với ISO format mà test gửi

### Pattern từ dữ liệu:
- Channel = 0 (main device)
- Event_type = "1" (mã event)
- Description = "" (trống)
- Timestamp = "2026-07-04 14:31:18" (YYYY-MM-DD HH:MM:SS)

### So sánh với test data:
- Test data: channel=1-2, event_type="motion"/"alarm"
- Real Imou: channel=0, event_type="1"
- Định dạng khác nhau!

## Kết luận:
✓ Camera Imou ĐÃ gửi dữ liệu thực (event ID 19)
✓ Định dạng khác với test data
✓ Cần cập nhật parser để xử lý format Imou thực
