"""
OKF v0.2 — Google Open Knowledge Format backbone (VidyaGyaan spec)
Stable @id, controlled @type, relations. Deterministic dedup by canonical @id.
Enterprise: persists to okf_entities / okf_relations (SQLite today, Neo4j/Qdrant tomorrow).
"""
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
import hashlib, re, json

class CBSEEntityType(str, Enum):
    SUBJECT_NODE   = "cbe:SubjectNode"
    CHAPTER        = "cbe:Chapter"
    TOPIC          = "cbe:Topic"
    CONCEPT        = "cbe:Concept"
    FORMULA        = "cbe:Formula"
    THEOREM        = "cbe:Theorem"
    DEFINITION     = "cbe:Definition"
    WORKED_EXAMPLE = "cbe:WorkedExample"
    QUESTION       = "cbe:AssessmentItem"
    PAPER          = "cbe:ExaminationPaper"
    BLOOMS_LEVEL   = "cbe:BloomsLevel"

class RelationType(str, Enum):
    HAS_CHAPTER     = "cbe:hasChapter"
    HAS_TOPIC       = "cbe:hasTopic"
    EXPLAINS        = "cbe:explains"
    PREREQUISITE_OF = "cbe:prerequisiteOf"
    APPLIES_TO      = "cbe:appliesTo"
    ASSESSES        = "cbe:assesses"
    APPEARS_IN      = "cbe:appearsIn"
    DEFINED_IN      = "cbe:definedIn"
    ALIGNED_TO      = "cbe:alignedTo"
    DERIVED_FROM    = "schema:isBasedOn"

def make_cid(*parts: str) -> str:
    norm = "|".join(re.sub(r"[\s,'\"]+", "_", p.lower().strip()) for p in parts if p)
    return f"cbe:{hashlib.sha256(norm.encode()).hexdigest()[:16]}"

class OKFEntity(BaseModel):
    id: str = Field(..., alias="@id")
    type: CBSEEntityType = Field(..., alias="@type")
    name: str
    description: Optional[str] = None
    alternateName: List[str] = Field(default_factory=list)
    inLanguage: str = "en-IN"
    sourceCitation: Optional[Dict] = None
    class Config: populate_by_name = True

class OKFRelation(BaseModel):
    subject: str = Field(..., alias="@id")
    predicate: RelationType
    object: str
    confidence: float = 1.0
    evidence_text: Optional[str] = None
    class Config: populate_by_name = True

class OKFGraph(BaseModel):
    context: str = "https://openknowledge.googleapis.com/v0.2"
    graph_id: str
    class_level: int = 10
    subject: str
    entities: List[OKFEntity] = Field(default_factory=list)
    relations: List[OKFRelation] = Field(default_factory=list)
    source_document: Dict = Field(default_factory=dict)

    def to_jsonld(self) -> dict:
        return {
            "@context": self.context,
            "@graph": [e.model_dump(by_alias=True) for e in self.entities],
            "relations": [r.model_dump(by_alias=True) for r in self.relations],
            "source": self.source_document,
        }

# ── Persistence helpers (SQLite today, Neo4j/Qdrant via feature flag) ──
def persist_graph(graph: OKFGraph, db=None):
    """Upsert entities/relations into okf_entities / okf_relations."""
    if db is None:
        from database import get_db
        db = get_db()
    for e in graph.entities:
        try:
            db.execute(
                "INSERT OR REPLACE INTO okf_entities (id, type, name, description, alternate_names, in_language, source_citation, subject, class_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (e.id, e.type.value, e.name, e.description, json.dumps(e.alternateName), e.inLanguage, json.dumps(e.sourceCitation) if e.sourceCitation else None, graph.subject, graph.class_level)
            )
        except Exception:
            # Postgres path via db.py translation will use %s; fallback to generic
            db.execute(
                "INSERT INTO okf_entities (id, type, name, description, alternate_names, in_language, source_citation, subject, class_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name",
                (e.id, e.type.value, e.name, e.description, json.dumps(e.alternateName), e.inLanguage, json.dumps(e.sourceCitation) if e.sourceCitation else None, graph.subject, graph.class_level)
            )
    for r in graph.relations:
        try:
            db.execute(
                "INSERT OR IGNORE INTO okf_relations (subject, predicate, object, confidence, evidence_text) VALUES (?, ?, ?, ?, ?)",
                (r.subject, r.predicate.value, r.object, r.confidence, r.evidence_text)
            )
        except Exception:
            db.execute(
                "INSERT INTO okf_relations (subject, predicate, object, confidence, evidence_text) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (r.subject, r.predicate.value, r.object, r.confidence, r.evidence_text)
            )

def load_graph(graph_id: str) -> Optional[OKFGraph]:
    from database import get_db
    db = get_db()
    rows = db.execute("SELECT * FROM okf_entities WHERE id = ? OR subject = ?", (graph_id, graph_id)).fetchall() if hasattr(db, 'execute') else []
    # fallback: load by graph_id as subject
    if not rows:
        return None
    entities = [
        OKFEntity(**{
            "@id": r["id"], "@type": r["type"], "name": r["name"],
            "description": r["description"],
            "alternateName": json.loads(r["alternate_names"] or "[]"),
            "inLanguage": r["in_language"],
            "sourceCitation": json.loads(r["source_citation"]) if r["source_citation"] else None,
        }) for r in rows
    ]
    rels = db.execute("SELECT * FROM okf_relations WHERE subject IN (SELECT id FROM okf_entities WHERE subject=?) OR object IN (SELECT id FROM okf_entities WHERE subject=?)", (graph_id, graph_id)).fetchall()
    relations = [
        OKFRelation(**{"@id": r["subject"], "predicate": r["predicate"], "object": r["object"], "confidence": r["confidence"], "evidence_text": r["evidence_text"]})
        for r in rels
    ]
    return OKFGraph(graph_id=graph_id, subject=rows[0]["subject"] if rows else graph_id, entities=entities, relations=relations, source_document={})
