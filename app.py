from flask import Flask, render_template, jsonify
from flask_cors import CORS
import paho.mqtt.client as mqtt
import json
from collections import deque

app = Flask(__name__, template_folder='dashboard')
CORS(app)

# 用於儲存最新數據的隊列
latest_detections = deque(maxlen=1)

def on_connect(client, userdata, flags, rc):
    client.subscribe("/smart_factory/production_line/results")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload)
        latest_detections.append(data)
    except Exception as e:
        print(f"Error parsing message: {e}")

# 啟動 MQTT 客戶端
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.loop_start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    if latest_detections:
        return jsonify(latest_detections[0])
    return jsonify({})

if __name__ == '__main__':
    app.run(debug=True)