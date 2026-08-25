"""
Orchestrator — routes CBSEState through narrative engines + guard + RAG + visualization.
LangGraph-compatible: each node is a function(state) -> state delta.
"""
from typing import Dict
try:
    from langsmith import traceable
except ImportError:
    def traceable(name=None):
        def deco(fn): return fn
        return deco

from services.narrative.math_theorem import MathTheoremEngine
from services.narrative.science_story import ScienceStoryEngine
from services.narrative.history_thriller import HistoryThrillerEngine, FamilyDramaEngine, MusicSoulEngine
from services.curriculum_guard.guard_v3 import CurriculumGuardV3
from services.graph_engineering.okf_schema import CBSEEntityType

ENGINE_MAP = {
    "MA": MathTheoremEngine(),
    "SC": ScienceStoryEngine(),
    "SS_HISTORY": HistoryThrillerEngine(),
    "SS_POLITICAL": FamilyDramaEngine(),
    "EN": MusicSoulEngine(),
    "HI": MusicSoulEngine(),
}

def infer_engine(subject: str, chapter_title: str = "") -> str:
    s = (subject or "").lower()
    ct = chapter_title.lower()
    if "math" in s or "ma" in s: return "MA"
    if "sci" in s or "sc" in s: return "SC"
    if "hist" in s or "nationalism" in ct or "global" in ct: return "SS_HISTORY"
    if "polit" in s or "federalism" in ct or "democ" in ct: return "SS_POLITICAL"
    if "english" in s or "en" in s: return "EN"
    if "hindi" in s or "hi" in s: return "HI"
    return "MA"

class Orchestrator:
    def __init__(self):
        self.guard = CurriculumGuardV3()

    @traceable(name="orchestrator.route")
    def route(self, state: dict) -> dict:
        subject = state.get("subject") or "MA"
        intent = state.get("intent", "concept")
        query = state.get("messages", [{}])[-1].get("content", "") if isinstance(state.get("messages"), list) else str(state.get("messages",""))
        # Guard check
        passed, reason, aligned = self.guard.check(query, subject)
        state["guard_passed"] = passed
        state["guard_reason"] = reason
        state["aligned_syllabus_node"] = aligned
        if not passed:
            state["draft_answer"] = f'<div class="guard-block"><strong>Out of syllabus (2026-27):</strong> {reason}. Try a Class X topic — e.g., Real Numbers, Life Processes, Nationalism.</div>'
            state["formatted_html"] = state["draft_answer"]
            return state
        # Retrieval (vector+graph RAG via existing rag_engine)
        try:
            from rag_engine import get_engine
            eng = get_engine()
            ctx = eng.retrieve_context(query, max_chunks=5)
            state["retrieved_context"] = ctx
            # vector hits mapping
            hits = eng.hybrid_search(query, limit=5)
            state["vector_hits"] = [{"chunk_id": h["id"], "chapter": h.get("chapter_title",""), "section": h.get("title",""), "page": 1, "score": 0.9 - i*0.05} for i,h in enumerate(hits)]
        except Exception as e:
            state["retrieved_context"] = query
            state["vector_hits"] = []

        # Narrative generation
        engine_key = infer_engine(subject, state.get("retrieved_context","")[:120])
        engine = ENGINE_MAP.get(engine_key, MathTheoremEngine())
        mode = "competitive" if intent == "solve" and state.get("attempt",0) >= 1 else "board"
        # Use retrieved context as topic content; fallback to query
        topic_title = hits[0].get("chapter_title","CBSE Class X") if 'hits' in locals() and hits else query[:60]
        result = engine.render(topic_title, state["retrieved_context"] or query, mode=mode)
        draft = result["html"]
        draft = self.guard.enforce_three_tier(draft)
        state["draft_answer"] = draft
        state["formatted_html"] = draft
        state["visualizations"] = result.get("visualizations", [])
        return state

# Singleton for server.py import
orchestrator = Orchestrator()
