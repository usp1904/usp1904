"""
Two-stage dedup: (1) canonical @id exact dedup (already in GraphifyEngine._add)
(2) embedding near-dedup via cosine > threshold.
"""
import numpy as np
from typing import Callable
try:
    from langsmith import traceable
except ImportError:
    def traceable(name=None):
        def deco(fn): return fn
        return deco

from .okf_schema import OKFGraph, CBSEEntityType

class SemanticDeduplicator:
    """Two-stage: canonical @id exact dedup + embedding near-dedup."""
    def __init__(self, embed_fn: Callable[[str], list[float]], threshold: float = 0.92):
        self.embed_fn = embed_fn
        self.threshold = threshold

    @traceable(name="dedup.semantic")
    def dedup(self, graph: OKFGraph) -> OKFGraph:
        for etype in CBSEEntityType:
            ents = [e for e in graph.entities if e.type == etype]
            if len(ents) < 2:
                continue
            texts = [f"{e.name} {e.description or ''}" for e in ents]
            embs = np.array([self.embed_fn(t) for t in texts])
            norms = np.linalg.norm(embs, axis=1, keepdims=True)
            embs = embs / (norms + 1e-9)
            sims = embs @ embs.T
            merge_map = {}
            for i in range(len(ents)):
                if ents[i].id in merge_map:
                    continue
                for j in range(i + 1, len(ents)):
                    if sims[i][j] > self.threshold:
                        merge_map[ents[j].id] = ents[i].id
                        for alt in [ents[j].name] + ents[j].alternateName:
                            if alt not in ents[i].alternateName and alt != ents[i].name:
                                ents[i].alternateName.append(alt)
            for r in graph.relations:
                if r.subject in merge_map:
                    r.subject = merge_map[r.subject]
                if r.object in merge_map:
                    r.object = merge_map[r.object]
            graph.entities = [e for e in graph.entities if e.id not in merge_map]
        return graph
