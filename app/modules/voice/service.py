# app/modules/voice/service.py

whisper_model = None


def get_model():
    global whisper_model
    if whisper_model is None:
        import whisper
        whisper_model = whisper.load_model("base")
    return whisper_model


def transcribe_audio(file_path: str) -> str:
    model = get_model()
    result = model.transcribe(file_path)
    return result["text"]
