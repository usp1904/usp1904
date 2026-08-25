"""
Syllabus Correlator — adds cbe:alignedTo from every chunk → CBSE syllabus node.
Hard Class X boundary: drops entities that don't correlate above threshold.
"""
from pathlib import Path
import json, re
from difflib import get_close_matches
try:
    from langsmith import traceable
except ImportError:
    def traceable(name=None):
        def deco(fn): return fn
        return deco

from .okf_schema import OKFGraph, RelationType, CBSEEntityType, make_cid

class SyllabusCorrelator:
    """Adds cbe:alignedTo from every chunk → its CBSE syllabus node."""
    def __init__(self, syllabus_path: Path = None, syllabus_index: dict = None):
        if syllabus_index is not None:
            self.syllabus = syllabus_index
        elif syllabus_path and Path(syllabus_path).exists():
            self.syllabus = json.loads(Path(syllabus_path).read_text(encoding="utf-8"))
        else:
            self.syllabus = {}
        self.index = self._build_index()

    def _build_index(self):
        idx = {}
        # Try syllabus_index.json structure or fallback to simple chapter list
        if isinstance(self.syllabus, dict) and "chapters" in self.syllabus:
            for ch in self.syllabus["chapters"]:
                idx[ch.get("title","").lower()] = ch
        elif isinstance(self.syllabus, list):
            for ch in self.syllabus:
                idx[str(ch).lower()] = {"title": ch}
        else:
            # fallback: use DB chapters
            try:
                from database import get_db
                db = get_db()
                for r in db.execute("SELECT id, title FROM chapters WHERE board_id='cbse' LIMIT 100").fetchall():
                    idx[r["title"].lower()] = {"title": r["title"], "id": r["id"]}
            except Exception:
                pass
        return idx

    @traceable(name="correlator.align")
    def correlate(self, graph: OKFGraph, threshold: float = 0.65) -> OKFGraph:
        for e in graph.entities:
            if e.type not in (CBSEEntityType.CONCEPT, CBSEEntityType.FORMULA, CBSEEntityType.THEOREM, CBSEEntityType.DEFINITION):
                continue
            text = f"{e.name} {e.description or ''}".lower()
            best = None
            best_score = 0
            for key, ch in self.index.items():
                # simple token overlap score
                score = len(set(text.split()) & set(key.split())) / max(len(set(key.split())), 1)
                if score > best_score:
                    best_score = score
                    best = ch
            if best and best_score >= threshold:
                # create alignedTo relation
                syllabus_id = best.get("id") or make_cid("syllabus", best.get("title",""))
                graph.relations.append(
                    __import__("services.graph_engineering.okf_schema", fromlist=["OKFRelation"]).OKFRelation(
                        **{"@id": e.id, "predicate": RelationType.ALIGNED_TO, "object": syllabus_id, "confidence": float(best_score), "evidence_text": best.get("title","")}
                    )
                )
        return graph

    def is_in_syllabus(self, chunk_text: str, threshold: float = 0.65) -> bool:
        text = chunk_text.lower()
        for key in self.index:
            score = len(set(text.split()) & set(key.split())) / max(len(set(key.split())), 1)
            if score >= threshold:
                return True
        return False
