import shutil
from pathlib import Path

MAX_REPOS_STORED = 5


def cleanup():
    repo_dir = Path("repos")

    repos = sorted(
        repo_dir.iterdir(),
        key=lambda p: p.stat().st_mtime
    )

    if len(repos) <= MAX_REPOS_STORED:
        return

    old_repos = repos[:-MAX_REPOS_STORED]

    for r in old_repos:
        shutil.rmtree(r)
        print("Deleted old repo:", r)
