from app.modules.voice.transcriber import (
    transcribe_audio
)

from app.modules.ai_moderation.service import (
    total_score
)


def scan_voice(
    audio_file: str
):

    text = transcribe_audio(
        audio_file
    )

    score, reasons = total_score(
        text
    )

    return {
        "text": text,
        "score": score,
        "reasons": reasons
    }