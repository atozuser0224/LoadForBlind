from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
from ultralytics import YOLO
import random

app = Flask(__name__)
model = YOLO("yolov8n.pt")

# 너무 낮으면 오검출 많아지므로 적당히 설정
CONF_THRESH = 0.5

def color_for_class(cls_id: int):
    """클래스 ID 기반으로 일관된 랜덤 색상 생성 (BGR)"""
    rng = random.Random(cls_id)  # cls_id 고정 시 항상 같은 색
    return (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))

def analyze_image(frame):
    # YOLO 추론 (임계값 적용)
    results = model(frame, conf=CONF_THRESH, verbose=False)
    result = results[0]

    detections = []
    h, w = frame.shape[:2]

    # 박스 수집
    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        # 경계 보정
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        detections.append({
            "class_id": cls_id,
            "class_name": model.names.get(cls_id, str(cls_id)),
            "confidence": round(conf, 4),
            "bbox": [x1, y1, x2, y2]  # [x1,y1,x2,y2]
        })

    if not detections:
        return None, frame  # 아무것도 못 찾음

    # 신뢰도 최고 1개만 선택
    top_det = max(detections, key=lambda d: d["confidence"])

    # 그리기
    x1, y1, x2, y2 = top_det["bbox"]
    box_color = color_for_class(top_det["class_id"])
    label = f'{top_det["class_name"]} {top_det["confidence"]:.2f}'
    cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
    cv2.putText(frame, label, (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

    # 반환은 class_name만 name 키로
    return {"name": top_det["class_name"]}, frame

@app.route('/upload', methods=['POST'])
def handle_upload():
    try:
        data = request.get_json()
        base64_image = data.get("imageBase64")

        if not base64_image:
            return jsonify({"error": "imageBase64 is missing"}), 400

        image_bytes = base64.b64decode(base64_image)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"error": "Failed to decode image"}), 400

        top_det, drawn = analyze_image(frame)

        if top_det is None:
            return jsonify({"results": [], "message": "no detections"}), 200

        # 시각화 결과 저장 (원하면 주석 처리 가능)
        cv2.imwrite("image.jpg", drawn)

        return jsonify({"results": [top_det]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Flask HTTP YOLO 서버 실행 중: http://0.0.0.0:5000/upload")
    app.run(host='0.0.0.0', port=5000)
