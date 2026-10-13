from shadowflow.impact.blast_radius import BlastRadiusReport
from shadowflow.impact.risk import RiskAssessment, RiskFactor
from shadowflow.report.markdown import impact_report_markdown


def test_impact_report_contains_sections() -> None:
    md = impact_report_markdown(
        ["pipeline/01_clean_users.sql"],
        BlastRadiusReport(direct=["clean_users"], indirect=["enriched_users"]),
        risk=RiskAssessment(
            score=40,
            level="MEDIUM",
            factors=[RiskFactor(points=20, description="test factor")],
        ),
    )
    assert "# ShadowFlow impact report" in md
    assert "clean_users" in md
    assert "enriched_users" in md
    assert "## Risk" in md
