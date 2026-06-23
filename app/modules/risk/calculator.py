from dataclasses import dataclass


@dataclass
class RiskFactors:

    warnings: int = 0

    mutes: int = 0

    spam_score: int = 0

    toxicity_score: int = 0

    raid_activity: int = 0


def calculate_risk(
    factors: RiskFactors
) -> int:

    score = 0

    score += factors.warnings * 10

    score += factors.mutes * 20

    score += factors.spam_score

    score += factors.toxicity_score

    score += factors.raid_activity * 30

    return min(score, 100)