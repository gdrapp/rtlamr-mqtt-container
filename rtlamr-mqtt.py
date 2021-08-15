import json
from subprocess import Popen, PIPE
import paho.mqtt.publish as publish
import os
import sys

MQTT_HOST = os.environ.get("MQTT_HOST") or sys.exit("MQTT_HOST environment variable not set")
try:
    MQTT_PORT = int(os.environ.get("MQTT_PORT")) or sys.exit("MQTT_PORT environment variable not set")
except ValueError as e:
    sys.exit("MQTT_PORT environment variable not an number")
MQTT_USERNAME = os.environ.get("MQTT_USERNAME") or sys.exit("MQTT_USERNAME environment variable not set")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD") or sys.exit("MQTT_PASSWORD environment variable not set")
MQTT_BASE_TOPIC = os.environ.get("MQTT_BASE_TOPIC", "rtlamr")
METER_ID = os.environ.get("METER_ID") or sys.exit("METER_ID environment variable not set")

def send_mqtt(topic, payload):
    try:
        print(f"Publishing {payload} to {topic}")
        mqtt_auth = {"username": MQTT_USERNAME, "password": MQTT_PASSWORD}
        publish.single(topic, payload=payload, qos=1, hostname=MQTT_HOST, port=MQTT_PORT, auth=mqtt_auth)
    except Exception as e:
        print(f"MQTT Publish Failed: {e}")

def main():
    print("Starting rtlamr")
    with Popen(["/usr/local/bin/rtlamr", "-server=localhost:1234", f"-filterid={METER_ID}", "-format=json"],stdout=PIPE, bufsize=1, universal_newlines=True) as proc:
        while proc.poll() == None:
            line = proc.stdout.readline()
            if not line:
                break
            data = None
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from rtlamr: {e}")

            if data is not None:
                id = data.get("Message", {}).get("ID")
                if id is not None:
                    topic = f"{MQTT_BASE_TOPIC}/{id}/json"
                    send_mqtt(topic, line)
    print("rtlamr exited")

if __name__ == "__main__":
    main()