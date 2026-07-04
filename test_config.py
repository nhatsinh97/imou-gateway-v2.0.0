from config import config

print(config.get("mqtt.host"))

print(config.get("mqtt.port"))

print(config.get("gateway.motion_timeout"))

print(config.get("database.path"))