from flask import Flask, request, jsonify, render_template
import paho.mqtt.client as mqtt
import os
import time

app = Flask(__name__)

# MQTT Configuration from Environment Variables
MQTT_BROKER = os.environ.get("MQTT_BROKER")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_USER = os.environ.get("MQTT_USER")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")

# MQTT Client Setup
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
    else:
        print(f"⚠️ Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    print("⚠️ Disconnected from MQTT Broker.")
    while True:
        try:
            print("🔁 Reconnecting to MQTT Broker...")
            client.reconnect()
            print("✅ Reconnected successfully.")
            break
        except Exception as e:
            print(f"❌ Reconnection failed: {e}")
            time.sleep(5)

client.on_connect = on_connect
client.on_disconnect = on_disconnect

# Set credentials and try initial connection
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    print(f"❌ Initial MQTT connection failed: {e}")

client.loop_start()  # Non-blocking

# Route to control any of the 4 switches
@app.route('/switch', methods=['GET'])
def switch():
    switch_num = request.args.get("switch")  # e.g., 1, 2, 3, 4
    action = request.args.get("action")      # e.g., on, off

    if switch_num not in ["1", "2", "3", "4"]:
        return jsonify({"error": "Invalid switch number. Use 1, 2, 3, or 4."}), 400
    if action.lower() not in ["on", "off"]:
        return jsonify({"error": "Invalid action. Use 'on' or 'off'."}), 400

    topic = f"cmnd/tasmota_device_fb/POWER{switch_num}"
    client.publish(topic, action.upper())

    return jsonify({
        "status": f"Switch {switch_num} turned {action.upper()}",
        "topic": topic
    })

# Web UI route
@app.route('/')
def control():
    return render_template('control.html')

# App runner
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render uses PORT env var
    app.run(host='0.0.0.0', port=port)
