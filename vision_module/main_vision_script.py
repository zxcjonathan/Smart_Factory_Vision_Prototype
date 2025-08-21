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

# ... (省略之前的程式碼)

if __name__ == '__main__':
    # MQTT 設定
    broker_address = "broker.hivemq.com"
    port = 1883
    topic = "smart_factory/defect_count"

    client = mqtt.Client(client_id="vision_module")
    client.connect(broker_address, port)

    # 圖片列表，可以加入更多圖片進行測試
    image_list = [
        '125_0_1_jpg.rf.8232e001d962520fcbab376eac7f104d.jpg',
        '127_0_2_jpg.rf.7405f2c7974b1dc708b118e377c7fca7.jpg',
        '136_0_2_jpg.rf.9d1a65cfa0f8ae097b2fcdf78ce89151.jpg',
        '155_0_0_jpg.rf.205ef007f8eadc837a914912d8ddfb11.jpg',
        '162_0_0_jpg.rf.5473ab941ab6043729a77a50c4332bed.jpg'
    ]

    for image_file in image_list:
        img_path = Path('../data/valid/images') / image_file

        # 處理圖片
        output_img, detections = process_image(img_path)

        # 取得瑕疵數量並發佈 MQTT 訊息
        defect_count = len(detections)
        payload = str(defect_count)
        client.publish(topic, payload)
        print(f"MQTT: Published defect count: {payload} for {image_file}")

        # 視覺化結果
        if output_img is not None:
            # 將圖片轉換為 BGR 格式，以便 OpenCV 顯示
            output_img_bgr = cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR)
            cv2.imshow('Detection Result', output_img_bgr)
            cv2.waitKey(5000) # 顯示 1 秒後繼續

    # 迴圈結束後，關閉所有視窗並斷開連接
    cv2.destroyAllWindows()
    client.disconnect()
    print("MQTT: Disconnected from broker.")