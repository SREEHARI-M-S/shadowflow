from __future__ import annotations

from pydantic import BaseModel, Field

from shadowflow.impact.blast_radius import BlastRadiusReport


class RiskFactor(BaseModel):
    points: int
    description: str


class RiskAssessment(BaseModel):
    score: int = Field(ge=0)
    level: str
    factors: list[RiskFactor] = Field(default_factory=list)


def assess_blast_radius(report: BlastRadiusReport) -> RiskAssessment:
    factors: list[RiskFactor] = []
    score = 0

    if report.direct:
        points = 20
        score += points
        factors.append(
            RiskFactor(
                points=points,
                description=f"{len(report.direct)} dataset(s) directly changed",
            ),
        )

    downstream = len(report.indirect)
    if downstream:
        points = min(40, 10 * downstream)
        score += points
        factors.append(
            RiskFactor(
                points=points,
                description=f"{downstream} downstream dataset(s) affected",
            ),
        )

    total = len(report.all_affected)
    if total >= 5:
        points = 15
        score += points
        factors.append(RiskFactor(points=points, description="large blast radius (5+ datasets)"))

    level = "LOW"
    if score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MEDIUM"

    return RiskAssessment(score=score, level=level, factors=factors)
