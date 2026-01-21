import re
from typing import List, Dict


maxLines = 40

langPatterns = {
    "python": r'^(def |class )',
    "javascript": r'^(function |class |const .*?= ?\(|export )',
    "typescript": r'^(function |class |interface |type |const .*?= ?\(|export )',
    "cpp": r'^(?:[\w:<>,~]+\s+)+[\w:]+::?[\w]+\s*\(.*\)\s*\{',
    "cpp-header": r'^(class |struct )',
    "java": r'^(public |private |protected |class |interface )',
    "go": r'^func ',
    "rust": r'^(fn |struct |enum |impl )'
}

def splitContentByLines(text: str, maxLines: int) -> List[Dict]:
    lines = text.splitlines()
    chunks = []
    
    for i in range(0, len(lines), maxLines):
        chunkLines = lines[i:i + maxLines]
        chunks.append({
            "content": "\n".join(chunkLines),
            "startLine": i + 1,
            "endLine": i + len(chunkLines)
        })
    return chunks

def splitContentByPattern(text: str, pattern: str) -> List[Dict]:
    regex = re.compile(pattern, re.MULTILINE)
    matches = list(regex.finditer(text))

    if not matches:
        return splitContentByLines(text, maxLines)
    
    chunks = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunkTest = text[start:end]
        startLine = text[:start].count("\n") + 1
        endLine = startLine + chunkTest.count("\n")

        chunks.append({
            "content": chunkTest.strip(),
            "startLine": startLine,
            "endLine": endLine
        })
    return chunks

def splitForMarkdown(text: str) -> List[Dict]:
    pattern = r'^#{1,6} '
    return chunk_code_by_pattern(text, pattern)


def chunker(scannedFiles: List[Dict]) -> List[Dist]:
    chunks = []
    chunkID = 0

    for file in scannedFiles:
        path = file["path"]
        lang = file["language"]
        text = file["content"]

        if lang in langPatterns:
            fileChunks = splitContentByPattern(text, langPatterns[lang])
            chunkType = "code"
        elif lang == "markdown":
            fileChunks = splitForMarkdown(text)
            chunkType = "doc"
        elif lang in {"json", "yaml"}:
            fileChunks = [{
                "content": text,
                "startLine": 1,
                "endLine": text.count("\n") + 1
            }]
            chunkType = "config"
        else:
            fileChunks = splitContentByLines(text, maxLines)
            chunkType = "text"
        for c in fileChunks:
            if not c["content"].strip():
                continue

            chunks.append({
                "chunkID": chunkID,
                "path": path,
                "language": lang,
                "chunkType": chunkType,
                "content": c["content"],
                "startLine": c["startLine"],
                "endLine": c["endLine"]
            })

            chunkID += 1
    return chunks
        