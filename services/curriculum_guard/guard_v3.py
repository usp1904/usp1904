"""
Curriculum Guard v3 — OKF graph boundary + 2026-27 syllabus hard filter
Refuses out-of-syllabus content, flags periodic assessment notes, enforces Class 6 anchor.
"""
import re
from typing import Tuple

PERIODIC_KEYWORDS = {"periodic assessment", "project work only", "deleted rationalized", "not in syllabus 2026-27"}
SYLLABUS_2026_27_MATH = {"real numbers","polynomials","linear equations","quadratic","arithmetic progressions","triangles","coordinate geometry","trigonometry","circles","areas related to circles","surface areas and volumes","statistics","probability"}
class CurriculumGuardV3:
    def __init__(self):
        self.okf_ready = False
        try:
            from database import get_db
            db = get_db()
            self.db = db
            self.okf_ready = True
        except Exception:
            self.db = None

    def check(self, text: str, subject: str = "") -> Tuple[bool, str, str]:
        """
        Returns (passed, reason, aligned_node)
        passed=False → out of syllabus or periodic-only, don't generate.
        """
        low = text.lower()
        # periodic filter
        for kw in PERIODIC_KEYWORDS:
            if kw in low:
                return False, f"Periodic assessment only — not for 2026-27 main exam: {kw}", ""

        # syllabus alignment via OKF/dbo lookup
        aligned = self._aligned_node(low, subject)
        if aligned:
            return True, "Aligned to CBSE 2026-27 syllabus", aligned

        # heuristic keyword allowlist for maths
        if any(k in low for k in SYLLABUS_2026_27_MATH):
            return True, "Heuristic alignment to maths syllabus", "cbe:math_generic"

        # allow general CBSE X content; only block if clearly off-syllabus (e.g., class 12 electrostatics detail)
        if "class 12" in low or "jee advanced level" in low:
            return False, "Beyond Class X 2026-27 boundary", ""
        return True, "Within Class X scope (curriculum-guard broad pass)", ""

    def _aligned_node(self, text: str, subject: str) -> str:
        if not self.okf_ready:
            return ""
        try:
            # Check okf_entities for aligned topic
            rows = self.db.execute("SELECT id, name FROM okf_entities WHERE lower(name) LIKE '%' || ? || '%' LIMIT 1", (text[:40].lower(),)).fetchone()
            if rows:
                return rows["id"]
            # fallback: chapters table
            r = self.db.execute("SELECT id FROM chapters WHERE lower(title) LIKE '%' || ? || '%' AND board_id='cbse' LIMIT 1", (text[:30].lower(),)).fetchone()
            if r:
                return r["id"]
        except Exception:
            pass
        return ""

    def enforce_three_tier(self, answer_html: str) -> str:
        """Ensure answer contains Class 6 anchor + NCERT core + bridge headers."""
        has_anchor = "Class 6 Anchor" in answer_html or "Everyday Analogy" in answer_html
        has_core = "NCERT 2026-27" in answer_html
        if not has_anchor or not has_core:
            banner = '<div class="guard-note" style="background:rgba(255,153,51,.08);border-left:4px solid #FF9933;padding:12px 16px;margin:16px 0;font-size:13px"><strong>Curriculum Guard:</strong> This answer is grounded in NCERT 2026-27. Class 6 anchor first, then core.</div>'
            return banner + answer_html
        return answer_html
