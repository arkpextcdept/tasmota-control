from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt

app = Flask(__name__)

# MQTT Configuration
MQTT_BROKER = "fuji.lmq.cloudamqp.com"
MQTT_PORT = 1883
MQTT_USER = "vgfesutt:vgfesutt"
MQTT_PASSWORD = "4Drb-Y8ryYLa0NoB0clL7Igq3OFETVN9"

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
    app.run(debug=True, port=5000)
