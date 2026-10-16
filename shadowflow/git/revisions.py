from __future__ import annotations

import subprocess
from pathlib import Path


def find_git_root(start: Path) -> Path | None:
    path = start.resolve()
    for candidate in [path, *path.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def changed_files(repo: Path, rev_range: str) -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", rev_range],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def parse_rev_range(rev_range: str) -> tuple[str, str]:
    if ".." not in rev_range:
        raise ValueError("Revision range must look like HEAD~1..HEAD")
    base, tip = rev_range.split("..", 1)
    return base.strip(), tip.strip()


def read_file_at_revision(repo: Path, revision: str, rel_path: str) -> str | None:
    rel = rel_path.replace("\\", "/")
    result = subprocess.run(
        ["git", "show", f"{revision}:{rel}"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def sql_overrides_for_change(
    repo: Path,
    project: Path,
    rev_range: str,
    changed_paths: set[str],
) -> tuple[dict[str, str], dict[str, str]]:
    """Build before/after SQL override maps keyed by pipeline SQL filename."""
    base_rev, _tip = parse_rev_range(rev_range)
    try:
        rel_project = project.resolve().relative_to(repo.resolve())
        prefix = str(rel_project).replace("\\", "/")
    except ValueError:
        prefix = ""

    before: dict[str, str] = {}
    after: dict[str, str] = {}
    for path in changed_paths:
        normalized = path.replace("\\", "/")
        if prefix and normalized.startswith(prefix + "/"):
            normalized = normalized[len(prefix) + 1 :]
        if not normalized.endswith(".sql"):
            continue
        basename = Path(normalized).name
        git_path = f"{prefix}/{normalized}" if prefix else normalized
        git_path = git_path.lstrip("/")

        old_sql = read_file_at_revision(repo, base_rev, git_path)
        disk_path = project / normalized
        if old_sql is not None:
            before[basename] = old_sql
        if disk_path.is_file():
            after[basename] = disk_path.read_text(encoding="utf-8")
    return before, after
