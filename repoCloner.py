import subprocess
from pathlib import Path


def repoCloner(repoLink: str) -> str:
    repo_dir = Path("repos")
    repo_dir.mkdir(exist_ok=True)
    repo_name = repoLink.rstrip("/").split("/")[-1].replace(".git", "")
    repo_path = repo_dir / repo_name
    if repo_path.exists() and repo_path.is_dir():
        return str(repo_path)
    result = subprocess.run(
        ["git", "clone", repoLink],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=repo_dir,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Git clone failed:\n{result.stdout}")
    return str(repo_path)
