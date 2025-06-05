import cv2
from ultralytics import YOLO

# 모델 로드 (세그멘테이션용 best.pt)
model = YOLO('last.pt')
# model = YOLO('runs/detect/train/weights/best.pt')

# 웹캠 열기 (0번 카메라)
# cap = cv2.VideoCapture("test.mp4")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ 웹캠을 열 수 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLOv8 예측
    results = model.predict(source=frame, imgsz=640, conf=0.5, save=False, show=False, stream=False)

    # 결과는 리스트로 반환됨 (보통 1개 프레임당 1개)
    for r in results:
        annotated_frame = r.plot()  # 바운딩박스, 마스크, 클래스명 등이 포함된 이미지 생성

    # OpenCV로 출력
    cv2.imshow("YOLOv8n-seg WebCam", annotated_frame)

    # 'q'를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
