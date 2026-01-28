import os
from pathlib import Path

MAX_FILES = 300
MAX_TOTAL_MB = 50


def validateRepo(repoPath: str):
    repoRoot = Path(repoPath)

    file_count = 0
    total_size = 0

    for root, _, files in os.walk(repoRoot):
        for f in files:
            file_count += 1
            fp = Path(root) / f

            total_size += fp.stat().st_size

            if file_count > MAX_FILES:
                raise RuntimeError("Repo too large (too many files).")

            if total_size > MAX_TOTAL_MB * 1024 * 1024:
                raise RuntimeError("Repo too large (size limit exceeded).")
