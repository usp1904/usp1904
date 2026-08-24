import json, pathlib
root = pathlib.Path(r"C:\Windows\System32\newopenai\packages\cbse_corpus")
for fname in ["social_2026_27.json","english_2026_27.json","hindi_2026_27.json"]:
    p = root/fname
    data = json.loads(p.read_text(encoding="utf-8"))
    for ch in data["chapters"]:
        title = ch["title"]
        # Build granular progression tailored to subject
        if "social" in fname:
            ch["granularProgression"] = [
                {"level":"L1 — Daily Routine (See & Feel)","desc":f"Daily analogy for {title}: family kitchen, market, school assembly — see the idea at home.","visual":"Home sketch: family sharing duties, market scene","jee":"Why this matters at home before textbook"},
                {"level":"L2 — NCERT Core (Do & Connect)","desc":"Board definition + 1st principle — why this event/rule exists, with dates/articles.","visual":"Timeline with 2-3 key dates, map with pins","jee":"Board keywords — mark fetchers"},
                {"level":"L3 — Story Proof (Narrate & Explain)","desc":"Full story with cause→event→impact, bullet chain, no rote.","visual":"Baahubali/family-drama storyboard, 3 beats","jee":"Essay linkages — history to civics"},
                {"level":"L4 — Twist & Compare (Debate & Analyse)","desc":"Compare 2 cases (Belgium vs Sri Lanka, renewable vs non-renewable), HOTS twist.","visual":"Split-screen compare, slider between cases","jee":"Analytical writing — UPSC bridge"},
                {"level":"L5 — Frontier (Constitution → Rockets)","desc":f"Frontier: {title} → from house rule to Constitution to G20/ISRO city planning — building rockets needs resource planning, power sharing, development indices.","visual":"Frontier simulation: Constitution → rocket mission control, resource map → satellite","jee":"From daily routine to frontier — building rockets needs social systems"},
            ]
        elif "english" in fname:
            ch["granularProgression"] = [
                {"level":"L1 — Daily Routine","desc":f"Daily feeling for {title}: a crow, a song, a mood — like morning tea.","visual":"Mood sketch: crow + snow + sun","jee":"Feel before meaning"},
                {"level":"L2 — NCERT Core","desc":"Poem/prose literal meaning, poet, theme, 1st device (alliteration, metaphor).","visual":"Annotated stanza with devices highlighted","jee":"Board — theme + device"},
                {"level":"L3 — Deeper Meaning","desc":"Why poet wrote, 2 interpretations, personal connect.","visual":"Two paths diagram: literal vs symbolic","jee":"Critical appreciation"},
                {"level":"L4 — Music Pair","desc":"Pair with song (Here Comes the Sun) — why this song fits this poem.","visual":"Headphones + notes, lyrics side-by-side","jee":"Intertextual — English to life"},
                {"level":"L5 — Frontier","desc":f"Frontier: {title} → from feeling sad to writing your own song/poem — from daily mood to creating art that heals, like rockets need stories.","visual":"Create: your verse + AI music, frontier where language builds rockets (communication)","jee":"From daily routine to frontier — building rockets needs stories"},
            ]
        else: # hindi
            ch["granularProgression"] = [
                {"level":"L1 — Daily Routine","desc":f"Daily use of {title}: doha at home, proverb at market.","visual":"Home scene: dadi telling doha","jee":"Culture before textbook"},
                {"level":"L2 — NCERT Core","desc":"Shabdarth, bhavarth, kavi parichay.","visual":"Word map with Hindi + English","jee":"Board — arth"},
                {"level":"L3 — Bhav Vistaar","desc":"Full bhav, 2 vyakhyas, why this kavita matters today.","visual":"Storyboard: village → city","jee":"Deeper meaning"},
                {"level":"L4 — Tulna","desc":"Compare 2 kavitas, HOTS twist — same theme, different style.","visual":"Split verse compare","jee":"Analytical Hindi"},
                {"level":"L5 — Frontier","desc":f"Frontier: {title} → from daily bolchal to writing your own doha — from routine to creating culture, like rockets need language.","visual":"Create: your doha + frontier where Hindi builds rockets (ISRO Hindi outreach)","jee":"From daily to frontier — building rockets needs mother tongue"},
            ]
        # also ensure mcqs have granular note if missing (english/hindi may not have mcqs)
        for mcq in ch.get("mcqs",[]):
            if "Granular" not in mcq.get("detailedExplanation",""):
                mcq["detailedExplanation"] = mcq.get("detailedExplanation","") + "\n\n**Granular → Frontier:** See daily routine → Do NCERT → Prove story → Twist compare → Crack frontier (rockets need this subject)"
            if "visualization" not in mcq:
                mcq["visualization"] = {"rendererType":"GEOMETRY_2D_PROOF","syllabusSource":"NCERT_2026_27","visualizationProperties":{"concept":title}}
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"{fname}: granular added to {len(data['chapters'])} chapters")

print("done")
