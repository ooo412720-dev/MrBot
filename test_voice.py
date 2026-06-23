from app.modules.voice.transcriber import (
    transcribe_audio
)

from app.modules.voice.service import (
    analyze_voice
)


text = transcribe_audio(
    "voice.ogg"
)

analysis = analyze_voice(
    text
)

print(text)

print(analysis)