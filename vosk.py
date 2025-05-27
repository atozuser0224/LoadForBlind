import os
import sys
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# 모델 경로 설정
model_path = "vosk-model-en-us-daanzu-20200905-lgraph"

# 모델 디렉토리 확인
if not os.path.exists(model_path):
    print("❌ 모델 경로가 존재하지 않습니다. 먼저 다운로드하고 압축 해제하세요.")
    sys.exit(1)

# Vosk 모델 로드
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# 오디오 데이터를 저장할 큐 생성
q = queue.Queue()

# 마이크 입력 콜백
def callback(indata, frames, time, status):
    if status:
        print("⚠️ 상태:", status, file=sys.stderr)
    q.put(bytes(indata))

# 마이크 스트리밍 시작
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("🎙️ 영어로 말하세요... (Ctrl+C로 종료)")
    try:
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                print("📝 인식된 문장:", result)
            else:
                pass  # 중간 결과는 원할 시 출력 가능
    except KeyboardInterrupt:
        print("\n🛑 인식 종료.")
