"""
Shared LangGraph State — CBSEState (VidyaGyaan spec §03)
One state threaded through every agent. Every mutation is LangSmith-traceable.
"""
from typing import TypedDict, Annotated, Literal, Optional, List
try:
    from langgraph.graph.message import add_messages
except ImportError:
    def add_messages(a,b): return b  # fallback
from langchain_core.messages import BaseMessage

class Citation(TypedDict):
    chunk_id: str
    chapter: str
    section: str
    page: int
    score: float

class GraphHop(TypedDict):
    from_node: str
    relation: str
    to_node: str
    depth: int

class EvalScore(TypedDict):
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    in_syllabus: bool
    bloom_level: str

class CBSEState(TypedDict):
    """Unified state threaded through every LangGraph node."""
    # ── Conversation (super-memory) ──
    messages: Annotated[List[BaseMessage], add_messages]
    user_id: str
    student_class: int
    subject: Optional[str]
    # ── Routing ──
    intent: Literal["concept", "solve", "paper", "summary", "unknown"]
    # ── Retrieval ──
    query_embedding: Optional[List[float]]
    vector_hits: List[Citation]
    graph_hops: List[GraphHop]
    retrieved_context: str
    # ── Generation ──
    draft_answer: str
    formatted_html: str
    visualizations: List[dict]
    # ── Guard ──
    guard_passed: bool
    guard_reason: str
    aligned_syllabus_node: Optional[str]
    # ── Loop engineering ──
    attempt: int
    max_attempts: int
    eval_score: Optional[EvalScore]
    critique: str
    # ── Observability ──
    trace_id: str
    latency_ms: int
