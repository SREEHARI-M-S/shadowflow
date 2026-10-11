from __future__ import annotations

from shadowflow.impact.blast_radius import BlastRadiusReport


def impact_report_markdown(
    changed_files: list[str],
    report: BlastRadiusReport,
) -> str:
    lines = [
        "# ShadowFlow impact report",
        "",
        "## Changed files",
        "",
    ]
    for path in changed_files:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Blast radius",
            "",
            "### Direct",
            "",
        ],
    )
    if report.direct:
        lines.extend(f"- `{name}`" for name in report.direct)
    else:
        lines.append("- _(none)_")
    lines.extend(["", "### Indirect", ""])
    if report.indirect:
        lines.extend(f"- `{name}`" for name in report.indirect)
    else:
        lines.append("- _(none)_")
    lines.extend(
        [
            "",
            f"**Total affected datasets:** {len(report.all_affected)}",
            "",
        ],
    )
    return "\n".join(lines)
