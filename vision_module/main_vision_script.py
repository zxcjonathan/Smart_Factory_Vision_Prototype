import cv2
import time
import json
import paho.mqtt.client as mqtt
from ultralytics import YOLO
import psycopg2 # 新增: 導入 psycopg2 模組

# --- PostgreSQL 數據庫相關設定 ---
# 請將以下變數替換為你自己的 PostgreSQL 數據庫資訊
DB_HOST = "localhost"
DB_NAME = "fabric_defects"
DB_USER = "ai_user"
DB_PASS = "qweasdzxc386"

# 連接數據庫
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor()

    # 創建表格
    # SERIAL: PostgreSQL 中實現自動增長 ID 的數據類型
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS defects (
            id SERIAL PRIMARY KEY,
            timestamp TEXT NOT NULL,
            total_defects INTEGER NOT NULL,
            v_defect INTEGER NOT NULL,
            w_defect INTEGER NOT NULL
        )
    """)
    conn.commit()
    print("數據庫連接成功並準備好表格。")
except psycopg2.Error as e:
    print(f"PostgreSQL 數據庫連接錯誤: {e}")
    # 在這裡，如果數據庫連接失敗，我們直接退出程式
    exit()

# --- MQTT 相關設定 ---
MQTT_BROKER = "mqttgo.io" # 請確認你的 MQTT Broker 地址
MQTT_PORT = 1883
MQTT_TOPIC = "your_mqtt_topic/defects" # 請替換為你的 Topic

# 連接 MQTT
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
print(f"已連接到 MQTT Broker: {MQTT_BROKER}")

# --- YOLOv8 模型載入 ---
# 載入你的最佳模型檔案
model = YOLO('../models/yolo_weights/best.pt')
print("YOLOv8 模型載入成功。")

# --- 視訊串流設定 ---
# 0 代表使用預設的攝像頭，如果你使用 IP Cam 或檔案，請替換路徑
cap = cv2.VideoCapture(0)

# 如果攝像頭無法打開，則退出
if not cap.isOpened():
    print("無法打開攝像頭，請檢查設備。")
    exit()

print("即時檢測系統啟動，按 'q' 鍵退出。")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("無法讀取視訊幀，正在退出...")
            break

        # 進行瑕疵檢測
        results = model(frame)
        
        # 初始化瑕疵計數
        defect_counts = {'V_defect': 0, 'W_defect': 0}

        # 處理檢測結果
        # results[0].boxes.data 包含了所有檢測到的物體資訊
        # cls 屬性是類別索引
        for detection in results[0].boxes.data:
            class_id = int(detection[-1])
            if class_id == 0:  # 假設 'V_defect' 的類別索引為 0
                defect_counts['V_defect'] += 1
            elif class_id == 1:  # 假設 'W_defect' 的類別索引為 1
                defect_counts['W_defect'] += 1

        total_defects = sum(defect_counts.values())

        # --- 數據庫寫入邏輯 (新增部分) ---
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        # 準備要插入的數據
        data_to_insert = (
            timestamp,
            total_defects,
            defect_counts['V_defect'],
            defect_counts['W_defect']
        )
        
        # 插入數據到表格
        # 注意: PostgreSQL 使用 %s 作為佔位符
        cursor.execute("INSERT INTO defects (timestamp, total_defects, v_defect, w_defect) VALUES (%s, %s, %s, %s)", data_to_insert)
        conn.commit()
        
        # 打印確認訊息 (可選)
        print(f"已寫入數據庫: {data_to_insert}")

        # --- MQTT 發佈邏輯 ---
        payload = {
            "total_defects": total_defects,
            "V_defect": defect_counts['V_defect'],
            "W_defect": defect_counts['W_defect'] 
        }
        json_payload = json.dumps(payload)
        client.publish(MQTT_TOPIC, json_payload)
        print(f"MQTT: Published payload: {json_payload}")

        # --- 可視化呈現 ---
        # 在畫面上顯示即時數據
        output_img = results[0].plot() # 繪製邊界框
        cv2.putText(output_img, f"Total: {total_defects}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(output_img, f"V_defect: {defect_counts['V_defect']}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(output_img, f"W_defect: {defect_counts['W_defect']}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        cv2.imshow('Real-time Detection', output_img)

        # 按 'q' 鍵退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # 確保在程式結束時釋放資源
    cap.release()
    cv2.destroyAllWindows()
    client.disconnect()
    if 'conn' in locals() and conn:
        conn.close() # 關閉數據庫連接
    print("程式已結束，資源已釋放。")