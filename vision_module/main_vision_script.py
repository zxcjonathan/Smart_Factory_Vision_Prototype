import cv2
import torch
from pathlib import Path
import paho.mqtt.client as mqtt
import json

# 使用YOLOv8
from ultralytics import YOLO

# 載入模型
model = YOLO(Path(__file__).parent.parent / 'models' / 'yolo_weights' / 'best.pt')

# 模擬產品和瑕疵品類別
# 這裡我們用COCO數據集中的'cup'和'keyboard'來模擬
CLASS_MAP = {
    0: 'V_defect',    # 根據您的訓練日誌，ID 0 對應 V 類瑕疵
    1: 'W_defect'     # 根據您的訓練日誌，ID 1 對應 W 類瑕疵
}

def process_image(img_path):
    """
    處理單張圖片，進行物件檢測
    """
    img = cv2.imread(img_path)
    if img is None:
        return None, None
        
    results = model(img)
    
    detections = []
    
    # 遍歷檢測結果
    for r in results:
        boxes = r.boxes
        for box in boxes:
            class_id = int(box.cls[0])
            # 這裡的判斷現在會成功
            if class_id in CLASS_MAP:
                # 取得座標、信心分數和類別名稱
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_name = CLASS_MAP[class_id]
                
                # 在圖片上繪製框和標籤
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(img, f'{class_name}: {confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                
                detections.append({
                    "class": class_name,
                    "confidence": confidence,
                    "location": [x1, y1, x2, y2]
                })

    return img, detections

if __name__ == '__main__':
    # ==================== 在這裡加入 MQTT 初始化程式碼 ====================
    # MQTT 設定
    broker_address = "broker.hivemq.com" # 免費公共代理伺服器
    port = 1883
    topic = "smart_factory/defect_count" # 定義發佈主題

    # 創建 MQTT 客戶端
    client = mqtt.Client(client_id="vision_module")
    client.connect(broker_address, port)

    # 測試單張圖片
    img_path = '../data/valid/images/125_0_1_jpg.rf.8232e001d962520fcbab376eac7f104d.jpg'
    output_img, detections = process_image(img_path)
    
    # ==================== 在這裡加入 發佈 MQTT 訊息的程式碼 ====================
    # 取得偵測到的物件數量
    defect_count = len(detections)
    
    # 將數量轉換為字串，並準備發佈
    payload = str(defect_count)
    
    # 發佈訊息
    client.publish(topic, payload)
    print(f"MQTT: Published defect count: {payload} to topic: {topic}")


    if output_img is not None:
        # 將圖片轉換為 BGR 格式，以便 OpenCV 顯示
        output_img_bgr = cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR)

        # 在螢幕上顯示圖片
        cv2.imshow('Detection Result', output_img_bgr)
        print("Detection Result displayed. Press any key to close the window.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Error: Could not process image.")
    
    # ==================== 在這裡加入 斷開 MQTT 連接的程式碼 ====================
    client.disconnect()
    print("MQTT: Disconnected from broker.")