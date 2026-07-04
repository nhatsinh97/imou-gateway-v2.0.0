import time

from mqtt_client import mqtt_manager

mqtt_manager.connect()

time.sleep(2)

mqtt_manager.publish_event({
    "camera": "Chuồng gà",
    "event": "motion"
})

mqtt_manager.publish_motion_timeout(0)

time.sleep(35)

mqtt_manager.disconnect()