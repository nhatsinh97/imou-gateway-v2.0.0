# Imou Gateway - Home Assistant MQTT Integration Guide

## 📋 Overview

Imou Gateway publish camera events to MQTT topics. Home Assistant subscribe những topics này để trigger automations.

---

## 🔌 MQTT Topics Publish

Gateway publish vào những topics sau:

```
imou/event                          → Raw event data (JSON)
imou/events/motion                  → Motion events
imou/events/person                  → Person detection events
imou/events/alarm                   → Alarm events
imou/events/vehicle                 → Vehicle detection
imou/camera/{channel}/motion        → Motion for specific channel
imou/camera/{channel}/person        → Person for specific channel
imou/camera/{channel}/alarm         → Alarm for specific channel
imou/camera/{channel}/{event_type}  → Any event type for specific channel
imou/raw                            → Raw webhook data
```

---

## 🚀 Setup Home Assistant

### Step 1: Enable MQTT Broker (Home Assistant)

Nếu chưa có MQTT broker, sử dụng Home Assistant Mosquitto Add-on:

**Settings → Add-ons → Add-on Store → Mosquitto Broker → Install → Start**

### Step 2: Configure Home Assistant MQTT

Edit `configuration.yaml`:

```yaml
mqtt:
  broker: localhost
  username: mosquitto_user
  password: mosquitto_password
  discovery: true
  discovery_prefix: homeassistant
```

### Step 3: Configure Imou Gateway

Edit `config.json` (hoặc `.env` file):

```json
{
  "mqtt": {
    "enabled": true,
    "host": "homeassistant-ip",
    "port": 1883,
    "username": "mosquitto_user",
    "password": "mosquitto_password",
    "topic_root": "imou"
  }
}
```

**Hoặc `.env` file:**

```bash
MQTT_ENABLED=true
MQTT_HOST=192.168.1.100  # IP của Home Assistant
MQTT_PORT=1883
MQTT_USERNAME=mosquitto_user
MQTT_PASSWORD=mosquitto_password
MQTT_TOPIC_ROOT=imou
```

---

## 📡 Home Assistant Entities

### Option 1: Binary Sensors (ON/OFF)

```yaml
# configuration.yaml
binary_sensor:
  - platform: mqtt
    name: "Camera Motion Detected"
    state_topic: "imou/camera/1/motion"
    payload_on: "ON"
    payload_off: "OFF"
    device_class: motion
    icon: mdi:motion-sensor

  - platform: mqtt
    name: "Person Detected"
    state_topic: "imou/events/person"
    payload_on: "person"
    device_class: occupancy
    icon: mdi:human
    json_attributes:
      - channel
      - timestamp

  - platform: mqtt
    name: "Alarm Triggered"
    state_topic: "imou/events/alarm"
    payload_on: "alarm"
    device_class: safety
    icon: mdi:alarm-light
    json_attributes:
      - channel
      - description
```

### Option 2: Sensors (Text/JSON)

```yaml
sensor:
  - platform: mqtt
    name: "Last Camera Event"
    state_topic: "imou/event"
    value_template: "{{ value_json.event_type }}"
    json_attributes:
      - channel
      - description
      - timestamp
    icon: mdi:camera

  - platform: mqtt
    name: "Camera 1 Last Event"
    state_topic: "imou/camera/1/motion"
    value_template: "{{ value_json | as_timestamp }}"
    icon: mdi:camera-motion
```

### Option 3: Template Sensors

```yaml
template:
  - trigger:
      platform: mqtt
      topic: "imou/events/motion"
    binary_sensor:
      - name: "Imou Motion"
        state: "{{ trigger.payload_json.event_type == 'motion' }}"
        device_class: motion

  - trigger:
      platform: mqtt
      topic: "imou/events/person"
    binary_sensor:
      - name: "Imou Person"
        state: "{{ trigger.payload_json.event_type == 'person_detection' }}"
        device_class: occupancy
```

---

## 🤖 Automations

### Automation 1: Motion Alert

```yaml
automation:
  - alias: "Camera Motion Detected"
    description: "Alert when motion detected"
    trigger:
      platform: mqtt
      topic: "imou/events/motion"
    action:
      - service: notify.mobile_app
        data:
          title: "Motion Detected!"
          message: "Channel {{ trigger.payload_json.channel }}"

  - alias: "Person Detection Alert"
    trigger:
      platform: mqtt
      topic: "imou/events/person"
    action:
      - service: notify.telegram
        data:
          message: "👤 Person detected on camera {{ trigger.payload_json.channel }}"

  - alias: "Alarm Trigger"
    trigger:
      platform: mqtt
      topic: "imou/events/alarm"
    action:
      - service: light.turn_on
        entity_id: light.living_room
        data:
          brightness: 255
          color_name: red
      - service: notify.mobile_app
        data:
          title: "🚨 ALARM!"
          message: "{{ trigger.payload_json.description }}"
```

### Automation 2: Turn on Light when Motion Detected

```yaml
automation:
  - alias: "Motion Light On"
    trigger:
      platform: mqtt
      topic: "imou/camera/1/motion"
      payload: "ON"
    action:
      - service: light.turn_on
        entity_id: light.bedroom
        data:
          brightness: 200

  - alias: "Motion Light Off Delayed"
    trigger:
      platform: state
      entity_id: binary_sensor.camera_motion_detected
      to: "off"
      for:
        minutes: 5
    action:
      - service: light.turn_off
        entity_id: light.bedroom
```

### Automation 3: Recording on Person Detection

```yaml
automation:
  - alias: "Record on Person Detection"
    trigger:
      platform: mqtt
      topic: "imou/events/person"
    action:
      - service: camera.record
        target:
          entity_id: camera.imou_ch1
```

---

## 📊 Dashboard/Lovelace

### Card 1: Motion Status

```yaml
type: entities
entities:
  - entity: binary_sensor.camera_motion_detected
    name: Motion
  - entity: binary_sensor.person_detected
    name: Person
  - entity: binary_sensor.alarm_triggered
    name: Alarm
title: Camera Status
```

### Card 2: Event History

```yaml
type: custom:mini-graph-card
entity: sensor.last_camera_event
name: Camera Events
unit: 
show:
  extrema: true
  average: false
  graph: line
```

### Card 3: Picture Card with Motion Alert

```yaml
type: picture-glance
entities:
  - binary_sensor.camera_motion_detected
  - binary_sensor.person_detected
image: /api/camera_proxy/camera.imou
```

---

## 🧪 Test MQTT Connection

### Từ Home Assistant Terminal:

```bash
# Test MQTT connection
mosquitto_sub -h localhost -u mosquitto_user -P mosquitto_password -t "imou/#"
```

### Từ Imou Gateway Terminal:

```bash
# Send test event
mosquitto_pub -h 192.168.1.100 -u mosquitto_user -P mosquitto_password \
  -t "imou/events/motion" \
  -m '{"channel":1,"event_type":"motion","description":"Test motion","timestamp":"2026-07-04T21:37:00"}'
```

---

## 📋 Event Payload Format

Khi event được publish, nó có format JSON sau:

```json
{
  "channel": 1,
  "event_type": "motion",
  "description": "Motion detected on channel 1",
  "timestamp": "2026-07-04T21:37:18",
  "id": 19,
  "gateway_id": "imou-gateway-001"
}
```

Các loại `event_type`:
- `motion` - Motion detection
- `person_detection` - Person detected
- `alarm` - Alarm triggered
- `vehicle` - Vehicle detected
- `other` - Other events

---

## 🔧 Troubleshooting

### MQTT Not Connected

**Error:** `MQTT not connected, message not published`

**Fix:**
1. Verify broker IP/Port in `config.json`
2. Check username/password correct
3. Verify firewall allows port 1883
4. Check Home Assistant MQTT add-on is running

```bash
# Check MQTT broker status
mosquitto_sub -h localhost -t '$SYS/broker/clients/connected'
```

### No Events Published

**Error:** No messages in `imou/#` topic

**Fix:**
1. Verify MQTT enabled in config
2. Check camera sending webhooks to `/webhook` endpoint
3. View logs: `docker logs imou-gateway`
4. Verify event is saved to database

### Events Not Triggering Automation

**Error:** Automation not triggered by MQTT events

**Fix:**
1. Check automation is enabled in Home Assistant
2. Verify correct topic name
3. Check payload format matches
4. View Home Assistant logs for errors

---

## 📚 Example Complete Setup

### Full Home Assistant configuration.yaml

```yaml
homeassistant:
  name: Home
  latitude: 0
  longitude: 0
  elevation: 0
  unit_system: metric
  time_zone: UTC

mqtt:
  broker: localhost
  username: mosquitto_user
  password: mosquitto_password
  discovery: true

binary_sensor:
  - platform: mqtt
    name: "Imou Motion"
    state_topic: "imou/camera/1/motion"
    payload_on: "ON"
    payload_off: "OFF"
    device_class: motion
    icon: mdi:motion-sensor

  - platform: mqtt
    name: "Imou Person"
    state_topic: "imou/events/person"
    device_class: occupancy

sensor:
  - platform: mqtt
    name: "Imou Last Event"
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
          message: "Channel {{ trigger.payload_json.channel }}"
```

---

## ✅ Verification

Sau khi setup, verify:

1. ✅ MQTT broker running
2. ✅ Imou Gateway connected to MQTT
3. ✅ Home Assistant MQTT entities show up
4. ✅ Camera sends webhook event
5. ✅ Event appears in MQTT topic
6. ✅ Home Assistant entities update
7. ✅ Automations trigger

**Kiểm tra Dashboard → Developer Tools → MQTT → Listen to topic → `imou/#`**

Bạn sẽ thấy events real-time khi có sự kiện từ camera!

---

## 🎯 Next Steps

1. **Deploy Gateway** trên CasaOS
2. **Configure MQTT broker** (Mosquitto)
3. **Add MQTT config** vào Home Assistant
4. **Create entities** trong Home Assistant
5. **Test** bằng cách generate events từ camera
6. **Create automations** cho các use cases của bạn

Hoàn tất setup này sẽ cho phép Home Assistant nhận real-time notifications từ camera Imou của bạn! 🎉
