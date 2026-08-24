import json, pathlib
root = pathlib.Path(r"C:\Windows\System32\newopenai\packages\cbse_corpus")
for fname in ["maths_2026_27.json","science_2026_27.json"]:
    p = root/fname
    data = json.loads(p.read_text(encoding="utf-8"))
    for ch in data["chapters"]:
        title = ch["title"]
        # Build granular progression 5 levels
        ch["granularProgression"] = [
            {
                "level": "L1 — Class 6 Anchor (See & Feel)",
                "desc": f"Everyday analogy for {title}: {ch.get('concept',{}).get('anchor','') if isinstance(ch.get('concept'),dict) else ch.get('concept','')}",
                "visual": "Hand-drawn garden sketch, real object (ladder, swing, rangoli, toy car)",
                "jee": "Intuition before formula — why the idea exists"
            },
            {
                "level": "L2 — NCERT 2026-27 Core (Do & Measure)",
                "desc": f"Board definition + 1st principle: {ch.get('concept',{}).get('ncert','')[:120] if isinstance(ch.get('concept'),dict) else ''}",
                "visual": "Clean diagram with labels, 1 formula, 1 worked NCERT Q",
                "jee": "Board accuracy — step marking as per marking scheme"
            },
            {
                "level": "L3 — Board Mastery (Prove & Explain)",
                "desc": "Full proof with steps, converse, and why each step is allowed (marking scheme).",
                "visual": "Aligned LaTeX proof + 2 alternate methods (factor vs formula)",
                "jee": "Speed vs accuracy trade-off"
            },
            {
                "level": "L4 — RD/RS Aggarwal Engine (Twist & Combine)",
                "desc": "Multi-concept twist: parameters, 3 variables, missing k, HOTS from RD/RS.",
                "visual": "2 diagrams overlaid (e.g., two triangles, two lenses), slider for k",
                "jee": "Bridge to Class XI — slope → calculus, discriminant → nature"
            },
            {
                "level": "L5 — JEE/NEET Frontier (Crack & Create)",
                "desc": f"Frontier use for {title}: from nails (daily) to rockets/NEET (frontier). Previous year JEE/NEET pattern, 30-sec Golden Step, options elimination.",
                "visual": "Frontier simulation: rocket trajectory / nephron filter / maglev lift — interactive, draggable",
                "jee": "JEE 2023/24 PYQ pattern, NEET 2022 assertion, Golden Step + elimination in 30s"
            },
        ]
        # Enhance each MCQ's detailedExplanation to be more granular if not already
        for mcq in ch.get("mcqs",[]):
            if "Granular" not in mcq.get("detailedExplanation",""):
                mcq["detailedExplanation"] = mcq.get("detailedExplanation","") + "\n\n**Granular → Frontier:**\n- *See:* Class 6 analogy\n- *Do:* NCERT 1st principle\n- *Prove:* Board proof with aligned steps\n- *Twist:* RD/RS parameter k\n- *Crack:* JEE PYQ Golden Step (30s) + NEET assertion"
            # Add frontier visualization for L5
            if "visualization" in mcq:
                mcq["visualization"]["visualizationProperties"]["frontier"] = "JEE/NEET — from granular to frontier"
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"{fname}: granular progression added to {len(data['chapters'])} chapters")
print("done")
