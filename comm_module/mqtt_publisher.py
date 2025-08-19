import paho.mqtt.client as mqtt
import json
import time

def publish_results(client, topic, detections):
    """
    將檢測結果發佈到 MQTT Broker
    """
    payload = {
        "timestamp": int(time.time()),
        "detections": detections
    }
    client.publish(topic, json.dumps(payload), qos=1)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def main():
    # 使用免費公共 MQTT Broker
    broker_address = "broker.hivemq.com"
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(broker_address, 1883, 60)
    client.loop_start()

    # 模擬生產線處理流程
    import os
    from vision_module.main_vision_script import process_image

    simulated_dir = Path(__file__).parent.parent / 'data' / 'simulated_line'
    for img_file in os.listdir(simulated_dir):
        if img_file.endswith('.jpg'):
            img_path = str(simulated_dir / img_file)
            _, detections = process_image(img_path)
            
            # 發佈結果到工廠儀表板主題
            publish_results(client, "/smart_factory/production_line/results", detections)
            
            # 模擬生產節奏
            time.sleep(1)

    client.loop_stop()
    client.disconnect()

if __name__ == '__main__':
    main()