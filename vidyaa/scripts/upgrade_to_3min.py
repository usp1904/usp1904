import json, pathlib
root = pathlib.Path(r"C:\Windows\System32\newopenai/packages/cbse_corpus")
for fname in ["maths_2026_27.json","science_2026_27.json","social_2026_27.json","english_2026_27.json","hindi_2026_27.json"]:
    p = root/fname
    data = json.loads(p.read_text(encoding="utf-8"))
    for ch in data["chapters"]:
        for anim in ch.get("animationVideos",[]):
            anim["duration"] = "3:00"
            anim["durationSec"] = 180
            anim["title"] = anim["title"].replace("20-sec", "3-min").replace("20-sec", "3-min")
            anim["compliance"] = "Industry-leading 3-min movie-like, real-life examples, 3D animations, self-hosted, no ads, GOI"
            anim["description"] = "3-min concept explained: Hook (real life) → Visual 3D animation → Theorem with aligned LaTeX → Worked example with 3 methods → Frontier (daily to rockets) — movie-like, game-like, self-paced"
        # Also update conceptPolished to reflect 3-min style
        for ch2 in data["chapters"]:
            if "conceptPolished" in ch2:
                ch2["conceptPolished"]["unveiling"]["visual"] = "Full-bleed 3-min movie-like lesson: 3D animation + in-air projection + real-life example (e.g., ladder, toy car, rangoli) — self-paced, 12-20 min distilled to 3 min garden version"
                ch2["conceptPolished"]["derivation"]["visual"] = "Split-screen 3-min: left 3D garden builds step-by-step, right LaTeX proof highlights on hover — 3-min distilled"
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"{fname}: upgraded to 3-min movie-like")

# Update index.html to reflect 3-min
import pathlib as pl
idx = pl.Path(r"C:\Windows\System32\newopenai/index.html")
t = idx.read_text(encoding="utf-8")
t = t.replace("20-sec Garden Animation", "3-min Garden Animation")
t = t.replace("20s • self-hosted • no ads", "3:00 • self-hosted • no ads")
t = t.replace("20s garden animation", "3-min garden animation")
t = t.replace("20-sec Visual", "3-min Visual")
t = t.replace("Play 20-sec Visual", "▶ Play 3-min Visual")
t = t.replace("Replay 20-sec Visual", "↻ Replay 3-min Visual")
t = t.replace("20s • self-hosted • no ads", "3:00 • self-hosted • no ads")
t = t.replace("20s max", "3:00 max")
t = t.replace("20s, no ads", "3:00, no ads")
idx.write_text(t, encoding="utf-8")
print("index updated to 3-min")
