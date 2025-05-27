import whisper

model = whisper.load_model("base")
result = model.transcribe("your_audio_file.wav", language='ko')
print(result["text"])
