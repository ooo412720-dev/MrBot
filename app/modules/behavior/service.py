from app.modules.risk.calculator import (
    RiskFactors,
    calculate_risk
)
def classify_user(
    factors: RiskFactors
) -> str:

    risk = calculate_risk(
        factors
    )

    if risk >= 80:
        return "danger"

    if risk >= 50:
        return "suspicious"

    return "safe"