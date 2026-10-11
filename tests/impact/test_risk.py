from shadowflow.impact.blast_radius import BlastRadiusReport
from shadowflow.impact.risk import assess_blast_radius


def test_high_risk_many_downstream() -> None:
    report = BlastRadiusReport(
        direct=["a"],
        indirect=["b", "c", "d", "e"],
    )
    assessment = assess_blast_radius(report)
    assert assessment.level in {"MEDIUM", "HIGH"}
    assert assessment.score >= 30
