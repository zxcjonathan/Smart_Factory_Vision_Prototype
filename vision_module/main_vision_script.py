import cv2
import torch
from pathlib import Path
import json

# 假設使用YOLOv8
from ultralytics import YOLO

# 載入模型
model = YOLO(Path(__file__).parent.parent / 'models' / 'yolo_weights' / 'yolov8n.pt')

# 模擬產品和瑕疵品類別
# 這裡我們用COCO數據集中的'cup'和'keyboard'來模擬
CLASS_MAP = {
    41: 'product_A',  # COCO Class ID for 'cup'
    66: 'defect_B'    # COCO Class ID for 'keyboard'
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
    # 測試單張圖片
    img_path = str(Path(__file__).parent.parent / 'data' / 'simulated_line' / 'sample.jpg')
    output_img, detections = process_image(img_path)
    
    if output_img is not None:
        cv2.imshow('Detection Result', output_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    print(json.dumps(detections, indent=2))