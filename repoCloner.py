import subprocess
from pathlib import Path


def repoCloner(repoLink: str) -> str:
    repo_dir = Path("/app/repos")
    repo_dir.mkdir(parents=True, exist_ok=True)

    repo_name = repoLink.rstrip("/").split("/")[-1].replace(".git", "")
    repo_path = repo_dir / repo_name

    print(f"Repo directory : {repo_dir}")
    print(f"Repo path      : {repo_path}")
    print(f"Repo exists    : {repo_path.exists()}")

    if repo_path.exists() and repo_path.is_dir():
        print("Repository already exists. Skipping clone.")
        return str(repo_path)

    print("Running clone command...")

    result = subprocess.run(
        [
            "git",
            "clone",
            "--progress",
            repoLink,
            str(repo_path)
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("Clone finished")
    print("Return Code:", result.returncode)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            f"Git clone failed.\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )

    return str(repo_path)
