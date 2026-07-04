# MQTT helper with auto-reconnect
import json
import threading
import logging
import time

import paho.mqtt.client as mqtt

from config import config

logger = logging.getLogger(__name__)

class MQTTManager:

    def __init__(self):

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="imou-gateway"
        )

        username = config.get("mqtt.username")
        password = config.get("mqtt.password")

        if username:
            self.client.username_pw_set(
                username,
                password
            )

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe

        # Set auto-reconnect
        self.client.reconnect_delay_set(min_delay=1, max_delay=32)

        self.connected = False
        self.motion_timers = {}
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

    def connect(self):
        """Connect to MQTT broker with retry logic"""
        host = config.get("mqtt.host")
        port = config.get("mqtt.port")

        logger.info(f"Connecting to MQTT {host}:{port}")

        try:
            self.client.connect(
                host,
                port,
                keepalive=60
            )

            # Start the network loop in background thread
            self.client.loop_start()
            
            # Wait for connection to be established (max 10 seconds)
            for i in range(100):
                if self.connected:
                    logger.info("MQTT connected successfully")
                    self.reconnect_attempts = 0
                    return
                time.sleep(0.1)
            
            logger.warning("MQTT connection timeout - will retry")

        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")
            self.reconnect_attempts += 1
            
            if self.reconnect_attempts < self.max_reconnect_attempts:
                logger.info(f"Retrying MQTT connection (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
                threading.Timer(5.0, self.connect).start()
            else:
                logger.error("Max MQTT reconnect attempts reached")

    def disconnect(self):
        """Disconnect from MQTT broker gracefully"""
        try:
            logger.info("Disconnecting from MQTT")
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
        except Exception as e:
            logger.error(f"Error disconnecting MQTT: {e}")

    def on_connect(self, client, userdata, flags, reason_code, properties):
        """Handle MQTT connection"""
        if reason_code == 0:
            self.connected = True
            logger.info("MQTT Connected successfully")
            self.reconnect_attempts = 0
        else:
            self.connected = False
            logger.error(f"MQTT Connection failed with code {reason_code}")

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        """Handle MQTT disconnection"""
        self.connected = False
        
        if reason_code == 0:
            logger.info("MQTT Disconnected normally")
        else:
            logger.warning(f"MQTT Disconnected with code {reason_code}, will attempt reconnect")

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        logger.debug(f"MQTT message received: {msg.topic} = {msg.payload.decode()}")

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        """Handle MQTT subscription response"""
        logger.debug(f"MQTT subscription acknowledged: {mid}")

    def publish(self, topic, payload):
        """Publish message to MQTT topic"""
        if not self.connected:
            logger.warning(f"MQTT not connected, message not published: {topic}")
            return False

        if isinstance(payload, dict):
            payload = json.dumps(
                payload,
                ensure_ascii=False
            )

        try:
            result = self.client.publish(
                topic,
                payload,
                retain=False,
                qos=1
            )
            
            if result.rc != 0:
                logger.warning(f"MQTT publish failed with code {result.rc}: {topic}")
                return False
            
            logger.debug(f"MQTT published to {topic}")
            return True
        except Exception as e:
            logger.error(f"Error publishing MQTT message: {e}")
            return False

    def publish_event(self, event):
        """Publish event to MQTT"""
        root = config.get("mqtt.topic_root")
        return self.publish(
            f"{root}/event",
            event
        )

    def publish_raw(self, raw):
        """Publish raw webhook data to MQTT"""
        root = config.get("mqtt.topic_root")
        return self.publish(
            f"{root}/raw",
            raw
        )

    def publish_motion(self, channel, state):
        """Publish motion detection event"""
        root = config.get("mqtt.topic_root")
        topic = f"{root}/camera/{channel}/motion"
        
        return self.publish(
            topic,
            "ON" if state else "OFF"
        )

    def publish_motion_timeout(self, channel):
        """Publish motion with automatic timeout"""
        timeout = config.get("gateway.motion_timeout")

        if channel in self.motion_timers:
            self.motion_timers[channel].cancel()

        if not self.publish_motion(channel, True):
            logger.warning(f"Failed to publish motion for channel {channel}")
            return

        # Schedule motion off
        timer = threading.Timer(
            timeout,
            lambda: self.publish_motion(channel, False)
        )

        timer.daemon = True
        timer.start()

        self.motion_timers[channel] = timer
        logger.debug(f"Motion timeout scheduled for channel {channel} ({timeout}s)")


mqtt_manager = MQTTManager()
