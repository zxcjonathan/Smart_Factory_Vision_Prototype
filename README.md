智慧工廠瑕疵檢測系統 (Smart Factory Defect Detection System)
專案介紹
這是一個基於電腦視覺的即時瑕疵檢測系統原型，專為智慧工廠環境設計。本專案利用 YOLOv8 物件偵測模型，自動識別工業編織物上的 V_defect (V型瑕疵) 和 W_defect (W型瑕疵)。

更重要的是，本系統不僅能進行視覺檢測，還能將檢測結果以標準化的 JSON 格式，透過 MQTT 協議即時發佈到智慧工廠的 MES (Manufacturing Execution System) 或其他中央控制系統，實現數據的無縫整合與應用。

核心功能
即時物件偵測：使用 YOLOv8 模型對即時視訊串流進行高效的瑕疵檢測。

多類別瑕疵識別：能夠精確區分並計數不同類型的瑕疵（V_defect、W_defect）。

即時數據可視化：在視訊畫面上顯示當前幀的瑕疵總數及各類別的計數。

MQTT 協議整合：將檢測結果打包成 JSON 格式，發佈至指定 MQTT Topic，實現與工廠自動化系統的即時數據溝通。

技術棧
程式語言：Python

模型框架：PyTorch

電腦視覺：OpenCV

物件偵測模型：YOLOv8

模型訓練平台：Roboflow

訊息傳輸協議：MQTT (Paho-MQTT)

數據格式：JSON

專案成果與效能優化
本專案在模型開發階段，透過 Roboflow 平台對數據集進行了多種增強（Data Augmentation）與處理，成功將模型效能從初步訓練的 mAP50: 0.091 大幅提升至 mAP50: 0.971。

訓練後模型效能:

mAP50 (均值平均精度) : 0.971

Precision (精準率) : 0.94

Recall (召回率) : 0.93

這一顯著的效能提升證明了本模型在工業環境下的可靠性與精確度。

專案展示
即時檢測與數據可視化
系統在即時視訊畫面上成功顯示了檢測到的瑕疵類型和計數。
!(https://placehold.co/800x600/f0f0f0/333333?text=Real-time+Detection+Interface)

MQTT 數據發佈
系統成功將結構化的 JSON 數據發佈到 MQTT Topic，提供給下游系統使用。
!(https://placehold.co/800x600/f0f0f0/333333?text=MQTT+JSON+Payload)

如何運行此專案
環境設置：

確保您的電腦已安裝 Python 3.9 或更高版本。

建議建立一個虛擬環境以管理專案依賴。

安裝依賴包：

在專案根目錄下打開終端機。

執行命令以安裝所有必要的套件：

pip install -r requirements.txt

模型檔案：

下載訓練好的 YOLOv8 模型權重檔案 (best.pt)，並將其放在 models/yolo_weights/ 目錄中。

運行程式：

在終端機中，執行主要腳本：

python main_vision_script.py

程式將自動連接到指定的 MQTT Broker 並開始即時處理視訊串流。

按下鍵盤上的 q 鍵可隨時結束程式。

結論
本專案成功實現了一個功能完整、高精度的智慧工廠瑕疵檢測解決方案，不僅展示了物件偵測模型的實用性，更體現了與現有工業系統整合的能力。這證明了我在電腦視覺、AI 模型優化和系統整合方面的綜合技能。