"""
ScienceStoryEngine — detective_story narrative (VidyaGyaan SC)
Detective story structure: crime scene → clues → culprit (concept) → lab report.
"""
try:
    from langsmith import traceable
except ImportError:
    def traceable(name=None):
        def deco(fn): return fn
        return deco

class ScienceStoryEngine:
    style = "detective_story"
    color = "#10B981"

    @traceable(name="narrative.science")
    def render(self, topic_title: str, topic_content: str, mode: str = "board") -> dict:
        title = topic_title.strip()
        if mode == "competitive":
            html = f"""
<div class="narrative science-story" data-style="{self.style}">
  <div class="pill pill-leaf">SCIENCE • COMPETITIVE MODE</div>
  <h3>{title} — Lab Report in 30s</h3>
  <p><strong>Golden Step:</strong> Balance atoms like suspects — never lose an atom. $2Mg + O_2 \\to 2MgO$ (2 left, 2 right).</p>
  <p><strong>Elimination:</strong> Check state symbols $(s),(g)$ and $pH$ direction in options — wrong phase = instant kill.</p>
  <div class="katex-block">$$ pH = -\\log[H^+] \\quad | \\quad V = IR $$</div>
</div>
"""
        else:
            html = f"""
<div class="narrative science-story" data-style="{self.style}">
  <div class="pill pill-leaf">SCIENCE • DETECTIVE STORY</div>
  <h3>Case File: {title}</h3>
  <div class="callout">
    <div class="callout-title">Class 6 Anchor — Crime Scene</div>
    <div class="callout-text">Your body is a smart city. Heart = pump, intestines = factories, DNA = blueprint in the safe. Something's missing — let's find the culprit.</div>
  </div>
  <h4>Clues (NCERT 2026-27 Core)</h4>
  <p>{topic_content[:300]}...</p>
  <h4>Lab Report</h4>
  <p><strong>Objective:</strong> See it. &nbsp; <strong>Procedure:</strong> Atom-count. &nbsp; <strong>Observation:</strong> $pH$ tells acidity ($pH<7$ acid, $pH>7$ base).</p>
  <div class="katex-block">$$ \\text{{Snell's Law: }} \\mu_1 \\sin i = \\mu_2 \\sin r $$</div>
  <p><strong>Advanced (NEET/JEE):</strong> Cartesian sign convention — light ray left→right, distances left negative, right positive.</p>
</div>
"""
        viz = [{"rendererType": "CHEM_MOLECULAR_BOND", "syllabusSource": "NCERT_2026_27", "visualizationProperties": {"title": title, "narrative": "detective"}}]
        return {"html": html, "visualizations": viz, "citations": [f"NCERT_2026_27_SC:{title}"]}
