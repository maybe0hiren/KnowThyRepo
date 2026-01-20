import os
from pathlib import Path
from typing import List, Dict

allowedFiles = {
    ".py", ".js", ".ts", ".cpp", ".h", ".java", ".go", ".rs", "md", ".txt", ".json", ".yaml", ".yml"
}

ignored = {
    ".git", "node_modules", "dist", "build", "__pycache__", ".env", "env", "venv"
}


def detectLanguage(filePath: Path) -> str:
    ext = filePath.suffix.lower()
    return {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".cpp": "cpp",
        ".h": "cpp-header",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".md": "markdown",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".txt": "text"
    }.get(ext, "unknown")


def projectScanner(projectRoot: str) -> List[Dict]:
    projectRoot = Path(projectRoot).resolve()
    scannedFiles = []


    for root, directory, files in os.walk(projectRoot):
        directory[:] = [d for d in directory if d not in ignored] #removing ignored directories
        for fileName in files:
            filePath = Path(root)/fileName
            if filePath.suffix.lower() not in allowedFiles:
                continue
            try:
                with open(filePath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue
            scannedFiles.append({
                "path": str(filePath.relative_to(projectRoot)),
                "language": detectLanguage(filePath),
                "content": content,
                "lineCount": content.count("\n") + 1
            })
    return scannedFiles

if __name__ == "__main__":
    import json

    project_path = "/home/Hiren/Documents/Cache/CloudStorage"
    result = projectScanner(project_path)

    print(f"Scanned {len(result)} files\n")
    print(json.dumps(result[:2], indent=2))

