# Imou PaaS Cloud Format Support

## Overview

Updated parser to support **Imou PaaS (Cloud)** webhook format in addition to local device format.

**Status:** ✅ **Fully Supported**

---

## Format Comparison

### Local Device Format (Original)
```json
{
  "channel": 0,
  "event_type": "1",           // Numeric code
  "description": "Motion detected",
  "timestamp": "2026-07-04 14:31:18"
}
```

### PaaS Cloud Format (New)
```json
{
  "type": 120,                 // Numeric code (120, 10039, etc.)
  "labelType": "humanAlarm",   // Event category
  "msgType": "human",          // Message type (human, smdHuman, etc.)
  "cid": 0,                    // Channel ID
  "cname": "Camera Name",      // Channel name
  "did": "9M0776CPCGF08E9",   // Device ID
  "dname": "Device Name",      // Device name
  "time": 1783201662,          // Unix epoch (seconds)
  "utcTime": 1783176462,       // UTC epoch
  "picUrl": [...],             // Picture URLs
  "deviceType": "IPC"          // Device type (IPC, NVR, etc.)
}
```

---

## Event Code Mapping

### Local Format (String Codes)

| Code | Event Type | Description |
|------|-----------|-------------|
| "1" | motion | Motion detection |
| "2" | person_detection | Person detected |
| "3" | alarm | Alarm triggered |
| "4" | face_detection | Face detection |
| "5" | vehicle_detection | Vehicle detected |
| "6" | sound_detection | Abnormal sound |
| "7" | tampering | Tampering detected |
| "8" | line_crossing | Line crossing |
| "9" | intrusion | Intrusion detection |
| "10" | parking | Parking detection |

### PaaS Format (Numeric Codes)

| Type | Event Type | Description |
|------|-----------|-------------|
| 120 | person_detection | Human detection (IPC) |
| 10039 | person_detection | Smart detection human (NVR) |

### labelType/msgType Mapping

| Value | Event Type |
|-------|-----------|
| humanAlarm, human, smdHuman | person_detection |
| motionAlarm, motion, mdAlarm | motion |
| vehicleAlarm, vehicle | vehicle_detection |
| faceAlarm, face | face_detection |
| soundAlarm, sound | sound_detection |

---

## Timestamp Handling

Parser automatically detects and converts timestamps:

### Unix Epoch (PaaS Format)
```
Input:  1783201662
Output: 2026-07-04T21:47:42
```

### String Format (Local Format)
```
Input:  "2026-07-04 14:31:18"
Output: "2026-07-04T14:31:18"
```

### ISO Format
```
Input:  "2026-07-04T14:31:18"
Output: "2026-07-04T14:31:18"
```

---

## Channel Extraction

Parser supports multiple channel field names:

```python
# Priority order
channel = data.get('channel')  # Local format
        or data.get('chn')    # Alternative local
        or data.get('cid')    # PaaS format
        or 0                  # Default
```

**Note:** Channel 0 is automatically mapped to Channel 1 for consistency.

---

## Device Information

Parser extracts device info with fallbacks:

```python
device_id = data.get('device_id')      # Custom
          or data.get('deviceId')      # Standard
          or data.get('did')           # PaaS (device ID)
          or 'unknown'

device_name = data.get('device_name')   # Custom
            or data.get('deviceName')   # Standard
            or data.get('dname')        # PaaS (device name)
            or ''
```

---

## Description Auto-Generation

For PaaS format, descriptions are built from available fields:

```
labelType + cname = "humanAlarm on Cong"
cname + event_type = "Cong - Person Detection"
event_type only = "Person Detection"
```

---

## Test Results

✅ **3/3 tests passed:**

1. **IPC Human Detection (type 120)**
   - Input: type=120, labelType=humanAlarm, cid=0
   - Output: type=person_detection, channel=1, ts=2026-07-04T21:47:42

2. **NVR Human Detection (type 10039)**
   - Input: type=10039, msgType=smdHuman, cid=3
   - Output: type=person_detection, channel=3, ts=2026-07-04T21:47:43

3. **Local Motion (type "1")**
   - Input: type="1", channel=1, timestamp string
   - Output: type=motion, channel=1, ts=2026-07-04T14:31:18

---

## API Endpoints (No Changes)

```
POST /webhook          → Receive both local and PaaS formats
POST /imou            → Receive both local and PaaS formats
GET  /events          → Retrieved stored events
GET  /stats           → View statistics
GET  /health          → Health check
```

---

## MQTT Publishing

Events are published to MQTT topics:

```
imou/event                           → All events (JSON)
imou/events/person_detection         → Person detection events
imou/events/motion                   → Motion events
imou/camera/{channel}/person_detection → Per-channel events
imou/camera/{channel}/motion
```

---

## Upgrading

**No code changes required for users.** The parser:
- ✅ Auto-detects format (local or PaaS)
- ✅ Auto-converts timestamps
- ✅ Handles all field name variations
- ✅ Maintains backward compatibility

---

## Troubleshooting

### Unknown Event Type
- Check event code in logs
- Add mapping to `IMOU_EVENT_CODE_MAP` or `IMOU_PAAS_TYPE_MAP`

### Timestamp Parse Error
- Supported formats listed in `normalize_timestamp()`
- Falls back to current time if parsing fails

### Channel Issues
- Check `cid` or `channel` field in webhook
- Channel 0 automatically maps to 1

---

## References

- Local format: Real Imou device webhooks
- PaaS format: Imou cloud/app webhooks (accessType: 'PaaS')
- Documentation: See app logs for detailed parsing info

Last updated: 2026-07-04
