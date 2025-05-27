import openai
import os

# 1. OpenAI API 키 설정 (환경 변수에서 가져오기)
openai.api_key = os.getenv("OPENAI_API_KEY")

if openai.api_key is None:
    print("오류: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    print("OpenAI API 키를 설정한 후 다시 실행해주세요.")
    print("예시: export OPENAI_API_KEY='sk-YOUR_SECRET_KEY'")
    exit()

# 2. 음성 인식할 오디오 파일 경로 설정
# 이 파일을 파이썬 스크립트와 같은 디렉토리에 두거나, 정확한 전체 경로를 지정하세요.
audio_file_path = "my_voice_message.mp3" # 또는 "my_voice_message.wav" 등

# --- 테스트 오디오 파일 생성 (선택 사항) ---
# 만약 테스트할 오디오 파일이 없다면 pydub으로 간단하게 만들어 볼 수 있습니다.
# 이 부분은 실제 사용 시에는 제거하거나 주석 처리하세요.
try:
    from pydub.generators import Sine
    from pydub import AudioSegment
    if not os.path.exists(audio_file_path):
        print(f"'{audio_file_path}' 파일이 없어 테스트용 오디오 파일을 생성합니다.")
        # 2초 동안 "삐" 소리 생성 (가상의 음성 데이터)
        sine_wave = Sine(800).to_audio_segment(duration=2000)
        # 여기에 짧은 음성을 직접 녹음한 오디오 파일을 넣는 것이 더 좋습니다.
        # 실제 음성 파일이 있다면 이 부분을 건너뛰세요.
        sine_wave.export(audio_file_path, format="mp3")
        print(f"테스트 오디오 파일 '{audio_file_path}' 생성 완료.")
except ImportError:
    print("pydub 라이브러리가 설치되지 않았거나 ffmpeg가 없습니다. 오디오 파일 생성을 건너뜝니다.")
    print("직접 음성 파일을 '{}' 경로에 준비해주세요.".format(audio_file_path))
# -----------------------------------------------

# 오디오 파일 존재 여부 확인
if not os.path.exists(audio_file_path):
    print(f"오류: 오디오 파일 '{audio_file_path}'을(를) 찾을 수 없습니다.")
    print("음성 인식할 오디오 파일을 해당 경로에 놓거나, audio_file_path 변수를 수정해주세요.")
    exit()

def transcribe_audio_with_whisper(file_path):
    """
    지정된 오디오 파일을 OpenAI Whisper 모델을 사용하여 텍스트로 변환합니다.
    """
    print(f"'{file_path}' 파일로 음성 인식을 시작합니다...")
    try:
        with open(file_path, "rb") as audio_file:
            # Whisper 모델 호출
            # model="whisper-1"은 현재 OpenAI의 음성 인식 모델입니다.
            # language="ko"를 추가하여 한국어 음성 인식을 명시할 수 있습니다.
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ko" # 한국어 음성 인식을 위해 'ko'로 지정
            )
        return transcription.text
    except openai.APIError as e:
        print(f"OpenAI API 호출 중 오류 발생: {e}")
        return None
    except FileNotFoundError:
        print(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"음성 인식 중 예상치 못한 오류 발생: {e}")
        return None

if __name__ == "__main__":
    recognized_text = transcribe_audio_with_whisper(audio_file_path)

    if recognized_text:
        print("\n--- 음성 인식 결과 ---")
        print(recognized_text)
    else:
        print("\n음성 인식에 실패했습니다.")

    # 선택 사항: 사용 후 오디오 파일 삭제 (필요에 따라 주석 해제)
    # if os.path.exists(audio_file_path) and "테스트용 오디오 파일을 생성합니다" in globals().get('print_messages', ''):
    #     os.remove(audio_file_path)
    #     print(f"테스트 오디오 파일 '{audio_file_path}' 삭제 완료.")