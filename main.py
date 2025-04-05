from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import os

app = Flask(__name__)

# MQTT Configuration from Environment Variables
MQTT_BROKER = os.environ.get("MQTT_BROKER")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_USER = os.environ.get("MQTT_USER")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")

# MQTT Client Setup
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.connect(MQTT_BROKER, MQTT_PORT, 60)

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

if __name__ == '__main__':
    # Important for Render deployment
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
