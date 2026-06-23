def auto_action(
    risk_score: int
):

    if risk_score >= 90:
        return "ban"

    if risk_score >= 70:
        return "mute"

    if risk_score >= 40:
        return "warn"

    return None