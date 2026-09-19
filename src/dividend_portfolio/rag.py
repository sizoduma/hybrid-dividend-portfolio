"""Small, local, deterministic RAG layer for dated portfolio evidence."""
from __future__ import annotations
import re
import sys
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class EvidenceHit:
    score: int
    path: str
    text: str

def retrieve(question: str, evidence_dir: str | Path, top_k: int = 5) -> list[EvidenceHit]:
    terms = set(re.findall(r"[a-z0-9]{3,}", question.lower()))
    hits = []
    for path in sorted(Path(evidence_dir).rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        score = sum(text.lower().count(term) for term in terms)
        if score:
            hits.append(EvidenceHit(score, str(path), text[:5000]))
    return sorted(hits, key=lambda hit: (-hit.score, hit.path))[:top_k]

def main(argv=None):
    question = " ".join(argv or sys.argv[1:]) or "Which portfolio assumptions require verification?"
    evidence = Path(__file__).resolve().parents[2] / "evidence"
    hits = retrieve(question, evidence)
    if not hits:
        print("No evidence found. Treat the answer as UNKNOWN and add a dated source note.")
    for hit in hits:
        print(f"\n### {hit.path} (score={hit.score})\n{hit.text}")
    print("\nLLM guardrail: cite only retrieved evidence; separate facts, assumptions, and inferences; label gaps UNKNOWN.")

if __name__ == "__main__":
    main()
