from app.modules.ai_moderation.spam import (
    spam_score
)

from app.modules.ai_moderation.toxicity import (
    toxicity_score
)


def total_score(
    text: str
) -> tuple[int, list[str]]:

    spam_points, spam_reasons = spam_score(
        text
    )

    toxic_points, toxic_reasons = toxicity_score(
        text
    )

    return (
        spam_points + toxic_points,
        spam_reasons + toxic_reasons
    )