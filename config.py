# Configuration
import json
import os
from pathlib import Path


DEFAULT_CONFIG = {
    "mqtt": {
        "host": "192.168.1.21",
        "port": 1883,
        "username": "",
        "password": "",
        "topic_root": "imou"
    },

    "gateway": {
        "motion_timeout": 30,
        "download_images": False,
        "log_level": "INFO"
    },

    "database": {
        "path": "database/events.db"
    },

    "images": {
        "path": "images"
    }
}


class ConfigManager:

    def __init__(self, filename="config.json"):
        self.filename = filename
        self.data = {}
        self.load()
        self._load_env_overrides()

    def load(self):
        if not os.path.exists(self.filename):
            self.data = DEFAULT_CONFIG.copy()
            self.save()
            return

        with open(self.filename, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def _load_env_overrides(self):
        """Load environment variable overrides for CasaOS/Docker"""
        env_mapping = {
            "mqtt.host": "MQTT_HOST",
            "mqtt.port": "MQTT_PORT",
            "mqtt.username": "MQTT_USERNAME",
            "mqtt.password": "MQTT_PASSWORD",
            "mqtt.topic_root": "MQTT_TOPIC_ROOT",
            "gateway.motion_timeout": "GATEWAY_MOTION_TIMEOUT",
            "gateway.log_level": "GATEWAY_LOG_LEVEL",
            "database.path": "DATABASE_PATH",
            "images.path": "IMAGES_PATH",
        }

        for config_key, env_key in env_mapping.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                # Convert port to int
                if "port" in config_key.lower():
                    env_value = int(env_value)
                # Convert timeout to int
                elif "timeout" in config_key.lower():
                    env_value = int(env_value)
                
                self.set(config_key, env_value)

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(
                self.data,
                f,
                indent=4,
                ensure_ascii=False
            )

    def get(self, key, default=None):
        value = self.data

        for part in key.split("."):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key, value):
        parts = key.split(".")
        data = self.data

        for part in parts[:-1]:
            if part not in data:
                data[part] = {}

            data = data[part]

        data[parts[-1]] = value
        self.save()


config = ConfigManager()
