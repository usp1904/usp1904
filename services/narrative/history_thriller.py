"""
HistoryThrillerEngine — cinematic Bahubali/Shivaji style (VidyaGyaan SS-History)
Three-act cinema: Setup → Conflict → Climax → Resolution, with real facts + exam importance.
"""
try:
    from langsmith import traceable
except ImportError:
    def traceable(name=None):
        def deco(fn): return fn
        return deco

class HistoryThrillerEngine:
    style = "cinematic"
    color = "#F59E0B"

    @traceable(name="narrative.history")
    def render(self, topic_title: str, topic_content: str, mode: str = "board") -> dict:
        title = topic_title.strip()
        html = f"""
<div class="narrative history-thriller" data-style="{self.style}">
  <div class="pill pill-gold">HISTORY • CINEMATIC</div>
  <h3>{title} — The Film</h3>
  <p><strong>Act I — Setup:</strong> Year, place, hero. <em>{topic_content[:120]}...</em></p>
  <p><strong>Act II — Conflict:</strong> Who vs whom? Why tension rose. Every date is a plot twist for the exam.</p>
  <p><strong>Act III — Climax:</strong> The moment everything changes — sign it, remember it.</p>
  <div class="callout">
    <div class="callout-title">Real Facts vs Drama</div>
    <div class="callout-text">Cinema makes you feel; facts make you score. Every scene ends with 3 exam bullets + year.</div>
  </div>
  <h4>Exam Importance</h4>
  <ul><li>Why event matters for 2026-27 syllabus (2 marks)</li><li>Map location if asked</li><li>Link to next chapter (continuity)</li></ul>
</div>
"""
        viz = [{"rendererType": "GEOMETRY_2D_PROOF", "syllabusSource": "NCERT_2026_27", "visualizationProperties": {"title": title, "style": "cinematic", "timeline": True}}]
        return {"html": html, "visualizations": viz, "citations": [f"NCERT_2026_27_SS:{title}"]}

class FamilyDramaEngine:
    style = "family_drama"
    color = "#F59E0B"

    @traceable(name="narrative.family")
    def render(self, topic_title: str, topic_content: str, mode: str = "board") -> dict:
        title = topic_title.strip()
        html = f"""
<div class="narrative family-drama" data-style="{self.style}">
  <div class="pill pill-gold">SOCIAL SCIENCE • FAMILY DRAMA</div>
  <h3>Episode: {title}</h3>
  <p><strong>Cast:</strong> Centre, State, Citizen — a family drama where powers = love, duties = arguments.</p>
  <p>{topic_content[:260]}...</p>
  <div class="callout">
    <div class="callout-title">Class 6 Anchor</div>
    <div class="callout-text">Family has parents (Centre) and kids (States). Federalism = who decides bedtime? Power-sharing = remote control.</div>
  </div>
  <h4>Bullet Breakdown (for answer writing)</h4>
  <ul><li>Definition → Example → Why it matters</li><li>Diagram: Centre ↔ State → Citizen</li></ul>
</div>
"""
        viz = [{"rendererType": "GEOMETRY_2D_PROOF", "syllabusSource": "NCERT_2026_27", "visualizationProperties": {"title": title, "style": "family_drama"}}]
        return {"html": html, "visualizations": viz, "citations": [f"NCERT_2026_27_SS:{title}"]}

class MusicSoulEngine:
    style = "soul_music"
    color = "#EC4899"

    @traceable(name="narrative.music")
    def render(self, topic_title: str, topic_content: str, mode: str = "board") -> dict:
        title = topic_title.strip()
        html = f"""
<div class="narrative music-soul" data-style="{self.style}">
  <div class="pill" style="background:rgba(236,72,153,.12);color:#BE185D">ENGLISH/HINDI • SOUL MUSIC</div>
  <h3>{title} — The Song</h3>
  <p><em>"Every poem is a song waiting for your heart."</em></p>
  <p>{topic_content[:260]}...</p>
  <div class="callout">
    <div class="callout-title">Heart Anchor</div>
    <div class="callout-text">Read aloud like a song — rhythm is memory. Where does the poet pause? That's the answer.</div>
  </div>
  <h4>Literary Devices → Marks</h4>
  <ul><li>Metaphor = feeling → 2 marks</li><li>Alliteration = sound → 1 mark</li></ul>
</div>
"""
        viz = [{"rendererType": "CHEM_MOLECULAR_BOND", "syllabusSource": "NCERT_2026_27", "visualizationProperties": {"title": title, "style": "soul"}}]
        return {"html": html, "visualizations": viz, "citations": [f"NCERT_2026_27_EN:{title}"]}
