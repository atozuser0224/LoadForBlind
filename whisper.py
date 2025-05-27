import openai
import os
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import time
from pydub import AudioSegment # 녹음된 데이터를 pydub으로 변환 (선택 사항, scipy 대신 사용 가능)

# 1. OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

if openai.api_key is None:
    print("OPENAI_API_KEY 환경 변수를 설정해주세요.")
    print("예시: export OPENAI_API_KEY='YOUR_API_KEY'")
    exit()

# 2. 녹음 설정
SAMPLE_RATE = 44100  # 샘플링 레이트 (Hz) - CD 품질
RECORD_SECONDS = 5   # 녹음할 시간 (초)
AUDIO_FILENAME = "recorded_audio.wav" # 녹음될 파일 이름

def record_audio(filename, duration, samplerate):
    """
    마이크로부터 음성을 녹음하여 WAV 파일로 저장합니다.
    """
    print(f"{duration}초 동안 음성 녹음을 시작합니다...")
    print("말씀해주세요...")

    # 기본 마이크 장치 선택 (대부분의 경우 기본값이 노트북 마이크)
    # sd.query_devices()를 사용하여 장치 목록을 확인하고 특정 장치 ID를 지정할 수도 있습니다.
    # 예: sd.default.device = '내장 마이크의 ID'

    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()  # 녹음이 완료될 때까지 기다립니다.

    print("녹음 완료.")
    write(filename, samplerate, audio_data) # WAV 파일로 저장
    print(f"'{filename}' 파일로 저장되었습니다.")
    return filename

def transcribe_audio(file_path):
    """
    주어진 오디오 파일을 위스퍼 AI를 사용하여 텍스트로 변환합니다.
    """
    try:
        with open(file_path, "rb") as audio_file:
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ko" # 한국어 음성 인식을 위해 language 매개변수 추가
            )
        return transcription.text
    except Exception as e:
        return f"음성 인식 중 오류 발생: {e}"

if __name__ == "__main__":
    # 1. 마이크로 음성 녹음
    recorded_file = record_audio(AUDIO_FILENAME, RECORD_SECONDS, SAMPLE_RATE)

    # 2. 녹음된 파일로 음성 인식 수행
    print(f"'{recorded_file}' 파일로 음성 인식 시작...")
    recognized_text = transcribe_audio(recorded_file)

    print("\n--- 인식된 텍스트 ---")
    print(recognized_text)

    # 선택 사항: 녹음된 파일 삭제
    # os.remove(recorded_file)
    # print(f"'{recorded_file}' 파일 삭제 완료.")