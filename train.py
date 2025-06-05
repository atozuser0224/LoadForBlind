# 3. Segmentation(YOLO) 학습

# 참고: https://docs.ultralytics.com/ko/models/yolov8/
from ultralytics import YOLO

# 사전 학습된 YOLOv8 모델 로드
# model = YOLO('yolov8n.pt') # 속도와 경량성이 중요한 실시간 애플리케이션에 적합한 모델
model = YOLO('yolov8n-seg.pt') # 정확도가 중요한 작업에 적합한 고성능 모델

# 모델 학습 실행
# model.train(data='./config.yaml', epochs=100, imgsz=960, batch=16, task='segment')
# model.train(
#     data='./config.yaml',
#     epochs=100,
#     patience=10,   # 성능 향상이 없으면 10epoch 뒤 중단
#     imgsz=640,
#     batch=16,
#     task='segment'
# )
model.train(
    data='./config.yaml',
    epochs=100,
    patience=10,   # 성능 향상이 없으면 10epoch 뒤 중단
    imgsz=640,
    batch=16
)