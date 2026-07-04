# ⚡ MQTT + Home Assistant Quick Setup (5 minutes)

## 1️⃣ Gateway Config (.env hoặc config.json)

```bash
# .env file
MQTT_ENABLED=true
MQTT_HOST=192.168.1.100          # Your Home Assistant IP
MQTT_PORT=1883
MQTT_USERNAME=mosquitto_user      # Set in HA Mosquitto Add-on
MQTT_PASSWORD=mosquitto_password
MQTT_TOPIC_ROOT=imou
```

**Hoặc config.json:**
```json
{
  "mqtt": {
    "enabled": true,
    "host": "192.168.1.100",
    "port": 1883,
    "username": "mosquitto_user",
    "password": "mosquitto_password",
    "topic_root": "imou"
  }
}
```

---

## 2️⃣ Home Assistant Configuration

**Add to `configuration.yaml`:**

```yaml
mqtt:
  broker: localhost
  username: mosquitto_user
  password: mosquitto_password

binary_sensor:
  - platform: mqtt
    name: "Motion Detected"
    state_topic: "imou/camera/1/motion"
    payload_on: "ON"
    payload_off: "OFF"
    device_class: motion

sensor:
  - platform: mqtt
    name: "Camera Event"
    state_topic: "imou/event"
    value_template: "{{ value_json.event_type }}"
    json_attributes:
      - channel
      - timestamp

automation:
  - alias: "Motion Alert"
    trigger:
      platform: mqtt
      topic: "imou/events/motion"
    action:
      - service: notify.mobile_app
        data:
          title: "Motion!"
          message: "Camera {{ trigger.payload_json.channel }}"
```

**Save → Restart Home Assistant**

---

## 3️⃣ Available MQTT Topics

```
# All events (JSON format)
imou/event
imou/events/motion
imou/events/person
imou/events/alarm
imou/events/vehicle

# Per-camera events
imou/camera/1/motion
imou/camera/1/person
imou/camera/1/alarm
imou/camera/2/motion
... (add more channels as needed)

# Raw webhook
imou/raw
```

---

## 4️⃣ Test in Home Assistant

**Developer Tools → MQTT → Subscribe to topic**

Topic: `imou/#`

**Expected output when camera sends event:**

```json
{"channel":1,"event_type":"motion","description":"Motion detected","timestamp":"2026-07-04T21:37:18","id":19}
```

---

## 5️⃣ Entity IDs in Home Assistant

After setup, these entities appear:

- `binary_sensor.motion_detected` - Motion on/off
- `sensor.camera_event` - Last event type
- Automations trigger automatically

---

## ✅ Verify MQTT Connection

**Check logs:**

```bash
# From gateway container or terminal
docker logs imou-gateway | grep MQTT
# or
tail -f logs/app.log | grep MQTT
```

**Should show:**
```
MQTT Connected successfully
MQTT published to imou/events/motion
```

---

## 🎯 Common Use Cases

### Get motion to turn on light
```yaml
automation:
  - trigger:
      platform: mqtt
      topic: "imou/camera/1/motion"
      payload: "ON"
    action:
      service: light.turn_on
      entity_id: light.bedroom
```

### Get person detection to send notification
```yaml
automation:
  - trigger:
      platform: mqtt
      topic: "imou/events/person"
    action:
      service: notify.mobile_app
      data:
        title: "👤 Person Detected!"
        message: "Channel {{ trigger.payload_json.channel }}"
```

### Alarm triggers scene
```yaml
automation:
  - trigger:
      platform: mqtt
      topic: "imou/events/alarm"
    action:
      service: scene.turn_on
      entity_id: scene.alarm_armed
```

---

## ⚠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| No MQTT connection | Check IP, port, username/password in config |
| No entities in HA | Restart Home Assistant after editing config.yaml |
| No events received | Verify camera sends webhook to `/webhook` endpoint |
| Automations not trigger | Check topic name matches exactly, check MQTT debug |

---

## 📖 Full Documentation

See `MQTT-HOME-ASSISTANT.md` for complete guide with advanced examples.

**Ready to go! 🚀**
