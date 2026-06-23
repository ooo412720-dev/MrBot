def recommendation(
    risk_score: int
) -> str:

    if risk_score >= 80:

        return "اقتراح: حظر العضو"

    if risk_score >= 50:

        return "اقتراح: كتم العضو"

    return "لا إجراء"