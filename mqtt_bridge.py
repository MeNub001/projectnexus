import paho.mqtt.client as mqtt
import requests
import time

# --- Configuration ---
BROKER_IP = "10.204.132.164"
PORT = 1883
API_URL = "http://127.0.0.1:8000/telemetry"


def on_connect(client, userdata, flags, rc):
    print(f"[SYSTEM] Connected to MQTT Broker with code {rc}")
    # Listen to all topics published by the Data Mule
    client.subscribe("aegis/mule/#")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8").strip()
    print(f"[LIVE SENSOR DATA] {topic} -> {payload}")

    try:
        if topic == "aegis/mule/water":
            if not payload:
                print(f"[WARNING] Received empty water payload. Skipping.")
                return

            water_val = int(payload)
            requests.post(API_URL, json={"sensor": "water", "value": water_val})

        elif topic == "aegis/mule/gas":
            # Extracts numeric digits in case your payload contains text like "ALERT: 500"
            digits = ''.join(filter(str.isdigit, payload))

            if not digits:
                print(f"[WARNING] No numeric digits found in gas payload: '{payload}'. Skipping.")
                return

            gas_val = int(digits)
            requests.post(API_URL, json={"sensor": "gas", "value": gas_val})

    except Exception as e:
        print(f"[API ERROR] Could not sync telemetry: {e}")

# Initialize the MQTT Client (Using Version 1 compatibility)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "AegisDashboardBridge")
client.on_connect = on_connect
client.on_message = on_message

print("Initializing Aegis MQTT-to-Dashboard Bridge...")
try:
    client.connect(BROKER_IP, PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\nBridge disconnected.")
    client.disconnect()