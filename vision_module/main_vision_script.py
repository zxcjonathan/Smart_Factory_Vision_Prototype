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

def process_frame(frame):
    """
    處理單張圖片幀，進行物件檢測
    """
    if frame is None:
        return None, None
        
    results = model(frame)
    
    detections = []
    
    defect_counts = {
        'V_defect': 0,
        'W_defect': 0
    }
    
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
                
                # 根據類別名稱增加計數
                if class_name in defect_counts:
                    defect_counts[class_name] += 1
                
                # 在圖片上繪製框和標籤
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, f'{class_name}: {confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                
                detections.append({
                    "class": class_name,
                    "confidence": confidence,
                    "location": [x1, y1, x2, y2]
                })

    return frame, detections, defect_counts

if __name__ == '__main__':
    # MQTT 設定
    broker_address = "broker.hivemq.com"
    port = 1883
    topic = "smart_factory/defect_count"

    client = mqtt.Client(client_id="vision_module")
    client.connect(broker_address, port)

    # ==================== 在這裡加入視訊串流處理程式碼 ====================
    # 設置視訊源：
    # 0 代表第一個攝影機。如果你有多個攝影機，可以嘗試 1, 2, ...
    # 或者你可以指定一個影片檔案的路徑，例如：video_path = 'my_video.mp4'
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        exit()

    try:
        while True:
            # 從視訊源讀取一幀畫面
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            # 處理當前幀畫面
            # 我們將 frame 傳遞給 process_image 函式
            output_img, detections, defect_counts = process_frame(frame)

            # 取得瑕疵數量並發佈 MQTT 訊息
            # 現在我們將發佈一個包含所有瑕疵數量的 JSON 物件
            
            # 為了方便管理，你可以將總數也加進去
            total_defects = len(detections)
            # 建立一個 Python 字典來存放所有數據
            mqtt_data = {
                'total_defects': total_defects,
                 'V_defect': defect_counts.get('V_defect', 0),
                 'W_defect': defect_counts.get('W_defect', 0)
            }
            
            # 使用 json.dumps() 將字典轉換為 JSON 格式的字串
            payload = json.dumps(mqtt_data)
            
            # 發佈 JSON 字串
            client.publish(topic, payload)
            print(f"MQTT: Published payload: {payload}")
            # 在畫面上顯示即時數據
            # 建立要顯示的文字訊息
            text_v = f"V_defect: {defect_counts.get('V_defect', 0)}"
            text_w = f"W_defect: {defect_counts.get('W_defect', 0)}"
            text_total = f"Total: {total_defects}"

            # 在畫面上繪製文字
            # 參數：圖片、文字、左上角座標、字體、大小、顏色、粗細
            cv2.putText(output_img, text_v, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(output_img, text_w, (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(output_img, text_total, (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            # 視覺化結果
            cv2.imshow('Real-time Detection', output_img)

            # 按下 'q' 鍵退出迴圈
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # 釋放資源並斷開連接
        cap.release()
        cv2.destroyAllWindows()
        client.disconnect()
        print("MQTT: Disconnected from broker.")