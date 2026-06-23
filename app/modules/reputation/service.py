def update_reputation(
    current: int,
    risk_score: int
) -> int:

    if risk_score >= 80:

        return current - 20

    if risk_score >= 50:

        return current - 10

    return current + 1