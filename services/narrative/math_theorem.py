"""
MathTheoremEngine — theorem_analogy narrative (VidyaGyaan MA)
Class 6 anchor → NCERT 2026-27 core → RD Sharma/R.S Aggarwal bridge.
Produces KaTeX + visualization JSON.
"""
from typing import Optional
import re
try:
    from langsmith import traceable
except ImportError:
    def traceable(name=None):
        def deco(fn): return fn
        return deco

THEOREM_ANALOGIES = {
    "quadratic": "Playground swing U-curve touching grass at roots",
    "triangles": "Shadow of a stick — similarity via sun's rays",
    "circles": "Bicycle wheel — tangent touches at exactly one point",
    "probability": "Bag of marbles — chance = favourable / total",
}

class MathTheoremEngine:
    style = "theorem_analogy"
    color = "#6366F1"

    @traceable(name="narrative.math")
    def render(self, topic_title: str, topic_content: str, level: str = "concept", mode: str = "board") -> dict:
        """
        Returns {html, visualizations, citations}
        mode: board (Given/To Find/Formula/Steps + boxed) or competitive (Golden Step + elimination)
        """
        title = topic_title.strip()
        key = next((k for k in THEOREM_ANALOGIES if k in title.lower() or k in topic_content.lower()), "quadratic")
        analogy = THEOREM_ANALOGIES[key]

        # Extract formula if present
        formula = self._extract_formula(topic_content)

        if mode == "competitive":
            # JEE/NEET accelerator: skip intro, Golden Step
            html = f"""
<div class="narrative math-theorem" data-style="{self.style}">
  <div class="pill pill-saffron">MATH • COMPETITIVE MODE</div>
  <h3>{title} — Golden Step</h3>
  <p><strong>Golden Step:</strong> Discriminant $D = b^2 - 4ac$ decides everything. $D>0$ → 2 real roots, $D=0$ → 1, $D<0$ → 0 real (swing flies above grass).</p>
  <div class="katex-block">$$ x = \\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}} $$</div>
  <p><strong>Elimination:</strong> Check $b^2$ vs $4ac$ in options — odd/even, sign, units — kill 2 options in 10s.</p>
  <div class="viz" data-renderer="COORDINATE_GRAPH" data-source="NCERT_2026_27">{{"viz_math": true}}</div>
</div>
"""
        else:
            # Board mode: structured
            html = f"""
<div class="narrative math-theorem" data-style="{self.style}">
  <div class="pill pill-saffron">MATHEMATICS • THEOREM ANALOGY</div>
  <h3>{title}</h3>
  <div class="callout">
    <div class="callout-title">Class 6 Anchor — Everyday Analogy</div>
    <div class="callout-text">{analogy}. Before formulas, see it: two points where swing kisses grass are the answers.</div>
  </div>
  <h4>NCERT 2026-27 Core</h4>
  <p><strong>Given:</strong> $ax^2 + bx + c = 0$ &nbsp; <strong>To Find:</strong> $x$ &nbsp; <strong>Formula:</strong> $x = \\frac{{-b \\pm \\sqrt{{D}}}}{{2a}}$, $D = b^2-4ac$</p>
  <h4>Calculation Steps</h4>
  <div class="katex-block">
$$\\begin{{aligned}}
ax^2 + bx + c &= 0 \\\\
x &= \\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}}
\\end{{aligned}}$$
  </div>
  <p>Vertex (lowest point) $\\left(-\\frac{{b}}{{2a}}, -\\frac{{D}}{{4a}}\\right)$ — RD Sharma extension.</p>
  <p>$$\\boxed{{\\text{{Answer}} = x = \\frac{{-b \\pm \\sqrt{{D}}}}{{2a}}}}$$</p>
</div>
"""
        viz = [{
            "rendererType": "COORDINATE_GRAPH",
            "syllabusSource": "NCERT_2026_27",
            "visualizationProperties": {"title": title, "formula": formula, "analogy": analogy, "vertex": "(-b/2a, -D/4a)"}
        }]
        html = html.replace('{{"viz_math": true}}', f'<script type="application/json" class="viz-data">{__import__("json").dumps(viz[0])}</script>')
        return {"html": html, "visualizations": viz, "citations": [f"NCERT_2026_27_MA:{title}"]}

    def _extract_formula(self, text: str) -> Optional[str]:
        m = re.search(r"x\s*=\s*\\frac[^$]+|ax\^2\s*\+", text)
        return m.group(0)[:120] if m else "x = (-b ± √(b²-4ac))/2a"
