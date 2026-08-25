"""
Graphify: walks Google Document Tree → OKF v0.2 entities, relations, normalization.
Canonical @id dedup. Correlates every chunk to CBSE Class X syllabus.
LangSmith traceable.
"""
import re
from typing import Optional, Dict
import hashlib
try:
    from langsmith import traceable
except ImportError:
    def traceable(name=None):  # type: ignore
        def deco(fn): return fn
        return deco

from .okf_schema import OKFEntity, OKFRelation, OKFGraph, CBSEEntityType, RelationType, make_cid
from .gdt_parser import GDT_Document

AIR_FILLER_RE = re.compile(r"\s+|(?<=\w),(?=\w)|[\u2018\u2019\u201C\u201D'\"]")
def normalize(text: str) -> str:
    text = AIR_FILLER_RE.sub(" ", text).strip().lower()
    return re.sub(r"\s+", " ", text)

HEADING_RE = re.compile(r"^(\d+)\.(\d+)(?:\.(\d+))?\s+(.+)$")

class GraphifyEngine:
    def __init__(self, subject: str, class_no: int = 10, syllabus_chapter_names: list[str] = None):
        self.subject = subject
        self.class_no = class_no
        self.entities: Dict[str, OKFEntity] = {}
        self.relations: list[OKFRelation] = []
        self.subject_root = make_cid("subject", f"class{class_no}", subject)
        self.chapter_ids: Dict[str, str] = {}
        self.syllabus_chapter_names = syllabus_chapter_names or []

    @traceable(name="graphify.run")
    def graphify(self, doc: GDT_Document) -> OKFGraph:
        self._add(OKFEntity(**{
            "@id": self.subject_root, "@type": CBSEEntityType.SUBJECT_NODE,
            "name": f"CBSE Class {self.class_no} {self.subject.title()}",
            "alternateName": [self.subject.title()],
            "inLanguage": "en-IN",
        }))
        current_chapter_id: Optional[str] = None
        current_topic_id: Optional[str] = None
        for page in doc.pages:
            for block in page.blocks:
                for para in block.paragraphs:
                    if not para.text.strip():
                        continue
                    txt = normalize(para.text)
                    if para.type == "HEADING":
                        current_chapter_id, current_topic_id = self._handle_heading(txt, page.page_number)
                    elif para.type == "DEFINITION":
                        self._handle_definition(txt, current_topic_id, page.page_number)
                    elif para.type == "FORMULA":
                        self._handle_formula(txt, current_topic_id, page.page_number)
                    elif para.type in ("PARAGRAPH", "LIST_ITEM"):
                        self._handle_chunk(txt, current_topic_id, page.page_number)
        return OKFGraph(
            graph_id=self.subject_root,
            class_level=self.class_no,
            subject=self.subject,
            entities=list(self.entities.values()),
            relations=self.relations,
            source_document={"url": doc.source_uri, "doc_id": doc.doc_id, "page_count": len(doc.pages)},
        )

    def _handle_heading(self, txt: str, page: int):
        m = HEADING_RE.match(txt)
        if not m:
            return None, None
        major, minor, sub, title_raw = m.groups()
        title = title_raw.strip()
        if minor is None:
            chapter_id = make_cid("chapter", self.subject_root, f"ch{major}", title)
            official = self._match_syllabus(title)
            self._add(OKFEntity(**{
                "@id": chapter_id, "@type": CBSEEntityType.CHAPTER,
                "name": official or title.title(),
                "alternateName": [title] if official else [],
                "sourceCitation": {"page": page, "number": major},
            }))
            self._rel(self.subject_root, RelationType.HAS_CHAPTER, chapter_id)
            self.chapter_ids[major] = chapter_id
            return chapter_id, None
        parent_ch = self.chapter_ids.get(major)
        if not parent_ch:
            return None, None
        topic_id = make_cid("topic", parent_ch, title)
        self._add(OKFEntity(**{
            "@id": topic_id, "@type": CBSEEntityType.TOPIC,
            "name": title.title(),
            "sourceCitation": {"page": page},
        }))
        self._rel(parent_ch, RelationType.HAS_TOPIC, topic_id)
        return parent_ch, topic_id

    def _handle_definition(self, txt: str, topic_id: Optional[str], page: int):
        m = re.match(r"(theorem|definition|note|proof)[:\s]+(.+)", txt, re.I)
        if not m:
            return
        kind, body = m.groups()
        etype = {"theorem": CBSEEntityType.THEOREM, "definition": CBSEEntityType.DEFINITION,
                 "note": CBSEEntityType.CONCEPT, "proof": CBSEEntityType.CONCEPT}.get(kind.lower())
        if not etype:
            return
        cid = make_cid(etype.value.split(":")[1], body)
        self._add(OKFEntity(**{
            "@id": cid, "@type": etype,
            "name": body[:120].title(), "description": body,
            "sourceCitation": {"page": page},
        }))
        if topic_id:
            self._rel(topic_id, RelationType.EXPLAINS, cid)

    def _handle_formula(self, txt: str, topic_id: Optional[str], page: int):
        cid = make_cid("formula", txt)
        self._add(OKFEntity(**{
            "@id": cid, "@type": CBSEEntityType.FORMULA,
            "name": txt[:80], "description": txt,
            "sourceCitation": {"page": page},
        }))
        if topic_id:
            self._rel(topic_id, RelationType.EXPLAINS, cid)

    def _handle_chunk(self, txt: str, topic_id: Optional[str], page: int):
        cid = make_cid("chunk", txt)
        self._add(OKFEntity(**{
            "@id": cid, "@type": CBSEEntityType.CONCEPT,
            "name": txt[:80], "description": txt,
            "sourceCitation": {"page": page},
        }))
        if topic_id:
            self._rel(topic_id, RelationType.EXPLAINS, cid)

    def _add(self, entity: OKFEntity):
        if entity.id not in self.entities:
            self.entities[entity.id] = entity
        else:
            existing = self.entities[entity.id]
            for alt in [entity.name] + entity.alternateName:
                if alt and alt not in existing.alternateName and alt != existing.name:
                    existing.alternateName.append(alt)

    def _rel(self, subj: str, pred: RelationType, obj: str):
        if not any(r.subject == subj and r.predicate == pred and r.object == obj for r in self.relations):
            self.relations.append(OKFRelation(**{"@id": subj, "predicate": pred, "object": obj}))

    def _match_syllabus(self, parsed_title: str) -> Optional[str]:
        from difflib import get_close_matches
        m = get_close_matches(parsed_title, self.syllabus_chapter_names, n=1, cutoff=0.7)
        return m[0] if m else None
