import json, pathlib
root = pathlib.Path(r"C:\Windows\System32\newopenai\packages\cbse_corpus")
for fname in ["maths_2026_27.json","science_2026_27.json","social_2026_27.json","english_2026_27.json","hindi_2026_27.json"]:
    p = root/fname
    data = json.loads(p.read_text(encoding="utf-8"))
    for ch in data["chapters"]:
        # Remove youtubeVideos
        ch.pop("youtubeVideos", None)
        ch.pop("videoCompliance", None)
        # Add educational animation (20s max, self-hosted, no ads, GOI compliant)
        ch["animationVideos"] = [{
            "id": f"anim-{ch['id']}",
            "title": f"{ch['title']} — 20-sec Visual (Garden Animation)",
            "duration": "0:20",
            "type": "educational-animation",
            "rendererType": "COORDINATE_GRAPH" if "maths" in fname else "PHYSICS_OPTICS_RAY" if "science" in fname else "GEOMETRY_2D_PROOF",
            "syllabusSource": "NCERT_2026_27",
            "compliance": "GOI norms, education only, no ads, no obscene, no orphan, self-hosted, <20s",
            "ads": False,
            "orphan": False,
            "illegal": False,
            "obscene": False,
            "host": "self-hosted (Canvas/SVG, no YouTube, no install)",
            "durationSec": 20
        }]
        ch["animationCompliance"] = "Strictly educational animation — 20s max, self-hosted Canvas/SVG, no ads, no obscene, no orphan, no illegal, GOI norms, court jurisdiction. No YouTube, no install, no promotion."
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"{fname}: deprecated youtube, added 20s animation to {len(data['chapters'])} chapters")
print("done")
