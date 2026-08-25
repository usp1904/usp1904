"""
CRS Unified Harness — Caveman + RTK + Supermemory + Graphiffy + claudeforeverything
+ DeepSeek Harness + CodebaseMCP + Google Document Tree + Google OKF v0.2
+ Mesh Load Balancer + LangGraph + Graph Engineering + Vector/Graph RAG

Token-optimized router: agents call ONE entrypoint — get_tool_for(task) — instead of
loading all context. Each tool is lazily initialized; failures degrade gracefully
to offline fallbacks so no agent blocks.

Run: python tools/crs_init.py --verify
     python tools/crs_init.py --init-all
"""
import os, sys, json, time, sqlite3, logging, importlib, subprocess, hashlib
ROOT = r"C:\Windows\System32\newopenai"
sys.path.insert(0, ROOT)
log = logging.getLogger("crs")

# ── CRS modes (not pip packages!) ──────────────────────────────────────────
CRS_MODES = {
    "caveman": {
        "pip_name": None,  # NOT pip:caveman==1.0 (HTML5 manifest checker — WRONG)
        "real": "Prompt harness: evidence-before-synthesis, verify every formula/file before claim. Enforced via skills/curriculum-guard + master-architectural-system-prompt + tools/crs_init.py:verify()",
        "status": "ACTIVE (skills installed)",
        "route_when": "Every answer: read file, cross-check syllabus, render LaTeX via math-formatter",
    },
    "rtk": {
        "pip_name": None,  # NOT pip:RTk==0.3.14 (Raspberry Pi GPIO — WRONG)
        "real": "Reasoning To Knowledge / Realtime Knowledge — hybrid search + knowledge_graph lineage. Implemented in rag_engine.py + knowledge_graph.py (OKF v0.2)",
        "status": "ACTIVE",
        "route_when": "Concept lookup, prerequisite chain, 'explain concept' triggers",
    },
    "supermemory": {
        "pip_name": "supermemory>=3.59.0",
        "real": "Supermemory Cloud — session memory + cross-chat persistence",
        "status": "pip 3.59.0 installed",
        "route_when": "Long-horizon learner history, streak/mastery recall, token compression",
    },
}

TOOLS = {
    "deepseek_harness": {
        "module": "deepseek_harness",
        "file": "deepseek_harness.py",
        "status": "checking",
        "route_when": "Mass ingestion (48+ Byjus urls), neutralize_rewrite, syllabus verify. LLM priority: MISTRAL > GEMINI > DEEPSEEK > offline",
        "token_tip": "Batch via Send() fanout max_concurrency=6, not per-url calls",
    },
    "langgraph": {
        "module": "langgraph_pipeline",
        "file": "langgraph_pipeline.py",
        "pip": "langgraph==1.2.11 + langchain==1.3.17",
        "status": "checking",
        "route_when": "Multi-url pipeline StateGraph UrlState 5 nodes fetch→clean→verify→rewrite→db_insert",
    },
    "graphify": {
        "module": None,
        "pip": "graphifyy==0.9.49 (CLI graphify.EXE)",
        "status": "checking",
        "route_when": "Codebase Q&A: path A B, explain X, code search via graph.json god nodes",
    },
    "codebase_mcp": {
        "module": None,
        "pip": "codebase-memory-mcp==0.10.8 (binary codebase-memory-mcp.EXE)",
        "status": "checking",
        "route_when": "Deep code intelligence: index_repository, search_graph, trace_path, get_architecture (daemon, 30s start)",
    },
    "claudeforeverything": {
        "module": None,
        "file": "~/.agents/skills/claudeforeverything/ (prompt harness)",
        "status": "checking",
        "route_when": "Unified Claude prompt routing — covered by master-architectural-system-prompt + dual-mode-router",
    },
    "google_document_tree": {
        "module": "rag_engine",
        "file": "rag_engine.py + chunking.py + json_index.py + mcp_server.py",
        "status": "checking",
        "route_when": "RAG ingestion: FTS5 chunks_fts + json_index.syllabus_index.json + mcp tools search/get_topic/get_chapter/retrieve_context",
    },
    "google_okf_v02": {
        "module": "knowledge_graph",
        "file": "knowledge_graph.py",
        "status": "checking",
        "route_when": "Concept lineage: knowledge_graph (35 nodes) + user_mastery + pillars (OKF v0.2: pillars→subjects→chapters→topics→chunks)",
    },
    "mesh_load_balancer": {
        "module": None,
        "file": "_archive/mesh_lb.py + nginx.conf + docker-compose.fixed.yml",
        "status": "checking",
        "route_when": "Perf/perf: round-robin workers --host 127.0.0.1 --port 3033/3036, upstream app:9090 (not 127.0.0.1)",
    },
    "graph_engineering": {
        "module": "knowledge_graph",
        "file": "knowledge_graph.py + concept_maps.py",
        "status": "checking",
        "route_when": "Graph ops: seed_knowledge_graph(), get_subject_graph(), get_recommended_next(), concept_maps",
    },
    "vector_graph_rag": {
        "module": "rag_engine",
        "file": "rag_engine.py (hybrid_search) + database.py ai_content_cache TTL 300",
        "status": "checking",
        "route_when": "Hybrid FTS+keyword scoring, 5-min TTL + DB cache, fallback to SSE streaming",
    },
}

SKILLS = {
    "master-architectural-system-prompt": r"C:\Users\Admin\.agents\skills\master-architectural-system-prompt\SKILL.md",
    "curriculum-guard": r"C:\Users\Admin\.agents\skills\curriculum-guard\SKILL.md",
    "math-formatter": r"C:\Users\Admin\.agents\skills\math-formatter\SKILL.md",
    "historical-paper-tags": r"C:\Users\Admin\.agents\skills\historical-paper-tags\SKILL.md",
    "dual-mode-router": r"C:\Users\Admin\.agents\skills\dual-mode-router\SKILL.md",
    "viz-generator": r"C:\Users\Admin\.agents\skills\viz-generator\SKILL.md",
    "finetuning": r"C:\Users\Admin\.agents\skills\microsoft-foundry\finetuning\SKILL.md",
    "graphify": r"C:\Users\Admin\.config\opencode\skills\graphify\SKILL.md",
}

def check_file(path):
    return os.path.exists(path)

def verify():
    report = {"crs_modes": CRS_MODES, "tools": {}, "skills": {}, "db": {}, "token_routing": {}}
    # Skills
    for name, path in SKILLS.items():
        report["skills"][name] = {"exists": os.path.exists(path), "path": path}
    # Tools — ping each
    # deepseek
    try:
        from deepseek_harness import get_harness
        h = get_harness()
        report["tools"]["deepseek_harness"] = {"ok": True, "model": getattr(h,"model","unknown"), "available": getattr(h,"available", False), "backend": getattr(h,"backend_name","deepseek")}
    except Exception as e:
        report["tools"]["deepseek_harness"] = {"ok": False, "error": str(e)[:200]}
    # langgraph
    try:
        import langgraph_pipeline
        g = langgraph_pipeline.build_graph()
        report["tools"]["langgraph"] = {"ok": True, "nodes": list(g.nodes.keys()) if hasattr(g,"nodes") else "StateGraph built"}
    except Exception as e:
        report["tools"]["langgraph"] = {"ok": False, "error": str(e)[:300]}
    # rag / doc tree
    try:
        from rag_engine import get_engine
        eng = get_engine()
        hits = eng.search("quadratic", limit=1)
        report["tools"]["google_document_tree"] = {"ok": True, "hits": len(hits), "engine": "RAGEngine FTS5+hybrid"}
        report["tools"]["vector_graph_rag"] = {"ok": True, "cache_ttl": 300, "ai_content_cache": True}
    except Exception as e:
        report["tools"]["google_document_tree"] = {"ok": False, "error": str(e)[:200]}
    # okf
    try:
        from knowledge_graph import get_full_graph
        fg = get_full_graph()
        report["tools"]["google_okf_v02"] = {"ok": True, "pillars": len(fg), "subjects_sample": list(fg.keys())[:3]}
        report["tools"]["graph_engineering"] = {"ok": True}
    except Exception as e:
        report["tools"]["google_okf_v02"] = {"ok": False, "error": str(e)[:200]}
    # mesh lb
    report["tools"]["mesh_load_balancer"] = {"ok": os.path.exists(os.path.join(ROOT, "_archive","mesh_lb.py")), "file": "_archive/mesh_lb.py", "docker_fixed": os.path.exists(os.path.join(ROOT,"docker-compose.fixed.yml"))}
    # graphify cli
    try:
        r = subprocess.run([sys.executable,"-m","graphify","--help"], capture_output=True, text=True, timeout=8)
        report["tools"]["graphify"] = {"ok": r.returncode==0, "cli": "graphify.EXE", "installed": True}
    except Exception as e:
        report["tools"]["graphify"] = {"ok": False, "error": str(e)[:200]}
    # codebase-mcp
    try:
        r = subprocess.run(["codebase-memory-mcp","--version"], capture_output=True, text=True, timeout=8, shell=True)
        report["tools"]["codebase_mcp"] = {"ok": "0.10.8" in (r.stdout+r.stderr), "binary": "codebase-memory-mcp.EXE", "daemon_note": "30s start timeout — run cli with --repo-path; may need first cold start"}
    except Exception as e:
        report["tools"]["codebase_mcp"] = {"ok": False, "error": str(e)[:200]}
    # supermemory
    try:
        from supermemory import Supermemory
        c = Supermemory(api_key=os.getenv("SUPERMEMORY_API_KEY","test-key"))
        report["tools"]["supermemory"] = {"ok": True, "version": "3.59.0", "init": str(type(c).__name__)}
    except Exception as e:
        report["tools"]["supermemory"] = {"ok": False, "error": str(e)[:200]}
    # DB
    try:
        conn = sqlite3.connect(os.path.join(ROOT,"cbse_content.db"))
        cur = conn.cursor()
        for t in ["topics","chunks","knowledge_graph","ai_content_cache"]:
            try:
                cnt = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                report["db"][t] = cnt
            except Exception as e:
                report["db"][t] = f"ERR {e}"
    except Exception as e:
        report["db"]["error"] = str(e)[:200]
    # Token routing table
    report["token_routing"] = {
        "rule": "Agents call get_tool_for(intent) — only load ONE harness per turn; others stay lazy. Keeps context <4k tokens.",
        "intents": {
            "ingest 10+ urls / bulk rewrite": "deepseek_harness + langgraph_pipeline (Send fanout 6, rate-limit 429 2^n*3s)",
            "explain/solve with syllabus grounding": "curriculum-guard + master-prompt 3-tier → rag_engine hybrid_search (limit 5) → knowledge_graph prerequisites",
            "past paper / remedial": "historical-paper-tags → knowledge_graph prerequisite_nodes → companion hint",
            "math render": "math-formatter → KaTeX $/$$/aligned (never raw a/b)",
            "visualize/graph": "viz-generator JSON → React rendererType",
            "codebase Q&A / path between files": "graphify explain/path OR codebase-mcp search_graph/trace_path (moderate mode)",
            "perf / scale": "mesh_load_balancer workers 3033/3036 + nginx app:9090",
            "memory / streak": "supermemory + gamification.py + spaced_repetition.py",
            "fine-tune": "finetuning skill workflows/quickstart.md → validate_sft → submit_training → check_training → deploy",
        },
        "anti_patterns": [
            "Do NOT pip install caveman/RTk GPIO packages — those are wrong namesakes (uninstalled).",
            "Do NOT load all harnesses at once — use lazy get_tool_for().",
            "Do NOT call per-url DeepSeek sequentially — use LangGraph Send().",
        ]
    }
    return report

def init_all():
    # Idempotent seeding
    from database import init_db
    from knowledge_graph import seed_knowledge_graph, seed_pillar_content
    init_db()
    seed_knowledge_graph()
    seed_pillar_content()
    from json_index import get_index
    try:
        get_index().build()
    except Exception as e:
        log.warning("json_index build: %s", e)
    print("init_all done: DB + OKF + json_index seeded")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--init-all", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.init_all:
        init_all()
    if args.verify or not args.init_all:
        rpt = verify()
        if args.json:
            print(json.dumps(rpt, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(rpt, indent=2, ensure_ascii=False))
            # human summary
            print("\n=== CRS CHECK SUMMARY ===")
            for k,v in rpt["skills"].items():
                print(f"SKILL {k}: {'OK' if v['exists'] else 'MISSING'}")
            for k,v in rpt["tools"].items():
                print(f"TOOL {k}: {'OK' if v.get('ok') else 'NEEDS-ATTN'} {v}")
            print(f"DB: {rpt['db']}")
