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
    "quadratic": ("Playground swing U-curve touching grass at roots",
                  "Day-to-day: Building a bridge arch — where it meets the ground are roots. Science & Tech: Projectile path in physics — $y = ax^2+bx+c$ predicts landing."),
    "triangles": ("Shadow of a stick — similarity via sun's rays",
                  "Day-to-day: Maps & blueprints use similar triangles to scale. Science & Tech: Optics — similar triangles design camera lenses and satellite dishes."),
    "circles": ("Bicycle wheel — tangent touches at exactly one point",
                 "Day-to-day: Wheel touching road at one point. Science & Tech: Gears and pulleys — tangent drives motion without slipping."),
    "probability": ("Bag of marbles — chance = favourable / total",
                   "Day-to-day: Weather forecast 70% rain. Science & Tech: Genetics — Punnett square, and AI — probability drives predictions."),
    "real_numbers": ("Sharing apples equally — division with remainder",
                     "Day-to-day: Dividing 10 apples among 3 friends. Science & Tech: Cryptography uses HCF/LCM for key generation."),
    "polynomials": ("Stacking boxes — zeroes are where stack touches ground",
                    "Day-to-day: Profit zero points in business. Science & Tech: Signal processing — polynomial roots filter noise."),
}

class MathTheoremEngine:
    style = "theorem_analogy"
    color = "#6366F1"

    def _is_theorem(self, title: str, content: str) -> bool:
        t = (title + " " + content).lower()
        return any(k in t for k in ["theorem", "lemma", "proof", "property", "criterion", "postulate", "axiom", "pythagoras", "thales", "converse"])

    @traceable(name="narrative.math")
    def render(self, topic_title: str, topic_content: str, level: str = "concept", mode: str = "board") -> dict:
        """
        Returns {html, visualizations, citations}
        - Theorem: analogy + day-to-day + science & tech (only where relevant)
        - Non-theorem: concise, no forced analogy
        - Problems: detailed steps only when required (marks>1 or exercise), else concise
        """
        title = topic_title.strip()
        is_theorem = self._is_theorem(title, topic_content)
        # Only pick analogy if theorem and relevant — fallback to generic if no specific key
        analogy_pair = None
        if is_theorem:
            key = next((k for k in THEOREM_ANALOGIES if k in title.lower() or k in topic_content.lower()), None)
            if key:
                analogy_pair = THEOREM_ANALOGIES[key]
            else:
                # Generic theorem fallback — still provide day-to-day + science & tech where it helps
                analogy_pair = (
                    "Building blocks — each part locks to the next, proving the whole",
                    "Day-to-day: Solving a puzzle by proving each piece fits. Science & Tech: Engineering — theorems guarantee bridges and circuits work safely."
                )

        formula = self._extract_formula(topic_content)

        if mode == "competitive":
            # JEE/NEET — concise, Golden Step only where it helps
            if is_theorem and analogy_pair:
                analogy, extension = analogy_pair
                html = f"""
<div class="narrative math-theorem" data-style="{self.style}">
  <div class="pill pill-saffron">MATH • COMPETITIVE MODE</div>
  <h3>{title} — Golden Step</h3>
  <p><strong>Golden Step:</strong> Discriminant $D = b^2 - 4ac$ decides. $D>0$ → 2 real, $D=0$ → 1, $D<0$ → 0 (swing above grass).</p>
  <div class="katex-block">$$ x = \\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}} $$</div>
  <p><strong>Elimination:</strong> Check $b^2$ vs $4ac$ — parity/sign kills 2 options in 10s.</p>
</div>
"""
            else:
                html = f"""
<div class="narrative math-theorem" data-style="{self.style}">
  <div class="pill pill-saffron">MATH • COMPETITIVE MODE</div>
  <h3>{title}</h3>
  <p><strong>Golden Step:</strong> Spot the pattern in $x = \\frac{{-b \\pm \\sqrt{{D}}}}{{2a}}$ and test options.</p>
</div>
"""
        else:
            # Board mode — selective
            if is_theorem and analogy_pair:
                analogy, extension = analogy_pair
                # Day-to-day + Science & Tech only for theorems where it naturally fits
                html = f"""
<div class="narrative math-theorem" data-style="{self.style}">
  <div class="pill pill-saffron">MATHEMATICS • THEOREM</div>
  <h3>{title}</h3>
  <div class="callout">
    <div class="callout-title">Everyday Analogy</div>
    <div class="callout-text">{analogy}.</div>
  </div>
  <div class="callout" style="border-left-color:#138808">
    <div class="callout-title">Day-to-day to Science & Tech</div>
    <div class="callout-text">{extension}</div>
  </div>
  <h4>NCERT 2026-27 Core</h4>
  <p><strong>Given:</strong> $ax^2 + bx + c = 0$ &nbsp; <strong>To Find:</strong> $x$ &nbsp; <strong>Formula:</strong> $x = \\frac{{-b \\pm \\sqrt{{D}}}}{{2a}}$</p>
  <div class="katex-block">
$$\\begin{{aligned}}
ax^2 + bx + c &= 0 \\\\
x &= \\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}}
\\end{{aligned}}$$
  </div>
  <p>$$\\boxed{{\\text{{Answer}} = x = \\frac{{-b \\pm \\sqrt{{D}}}}{{2a}}}}$$</p>
</div>
"""
            else:
                # Non-theorem: concise, no forced analogy
                html = f"""
<div class="narrative math-theorem" data-style="{self.style}">
  <div class="pill pill-saffron">MATHEMATICS</div>
  <h3>{title}</h3>
  <p>{topic_content[:300]}...</p>
  <div class="katex-block">$$ x = \\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}} $$</div>
</div>
"""
        viz = [{
            "rendererType": "COORDINATE_GRAPH",
            "syllabusSource": "NCERT_2026_27",
            "visualizationProperties": {"title": title, "formula": formula, "analogy": analogy_pair[0] if analogy_pair else "", "vertex": "(-b/2a, -D/4a)"}
        }]
        return {"html": html, "visualizations": viz, "citations": [f"NCERT_2026_27_MA:{title}"]}

    def _extract_formula(self, text: str) -> Optional[str]:
        m = re.search(r"x\s*=\s*\\frac[^$]+|ax\^2\s*\+", text)
        return m.group(0)[:120] if m else "x = (-b ± √(b²-4ac))/2a"
