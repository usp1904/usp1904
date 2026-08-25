commit 40ea05923ef485b2c7c1e8fb93ed2d22cfc0db35
Merge: f54a0dd 570709b 2de5014
Author: vidyaa <vidyaa@bharatshiksha.local>
Date:   Tue Aug 25 21:08:46 2026 +0530

    On main: restore-point-pre-vidya-20260825-210826-full

diff --cc Agents.md
index 0ff988b,0ff988b,0000000..86c3d5e
mode 100644,100644,000000..100644
--- a/Agents.md
+++ b/Agents.md
@@@@ -1,30 -1,30 -1,0 +1,158 @@@@
-- # Agents
+++# AGENTS.md ΓÇö OpenCode Guide for this Repo
  +
-- ## AI Tutor (`ai_tutor.py`)
-- Question-based learning agent that generates conceptual questions, evaluates student answers, and provides remedial content for weak areas.
+++## Agent Operating Contract ΓÇö Non-Negotiable (applies to every turn)
  +
-- - Generates questions: definition, formula, example, comparison, application, analysis
-- - Templates extract key concepts from topic content (bold terms, formulas)
-- - Self-assessment workflow with XP rewards
-- - Tracks sessions, answers, and progress per topic
+++1. **No over-engineering when the task is simple** ΓÇö do the minimal correct change. Don't add abstractions, refactors, or extra files unless the task explicitly requires it. Prefer `edit` over `write`.
+++2. **No running assumptions when confused** ΓÇö if intent, scope, or file target is ambiguous, STOP and ask via `question` tool. Do not guess board/subject/chapter IDs, env values, or API contracts.
+++3. **No random code changes outside the task** ΓÇö touch only files the user asked for. Never "clean up" neighboring code, rename, or reformat beyond the diff.
+++4. **Always double-check before calling it done** ΓÇö verify by reading the edited region, running the relevant command (`python test_unit.py`, `curl /health`, `python tools/crs_init.py --verify`), and confirming no preservation constraint was violated. If fix is unclear, ask rather than guess.
  +
-- ## RAG Engine (`rag_engine.py`)
-- Retrieval-Augmented Generation engine for semantic search across educational content.
+++**Prompt optimization:** keep prompts compact and token-aware ΓÇö load ONE harness per intent via `tools/crs_init.py:get_tool_for(intent)` (see `## Tool & Skill Routing` below). Never bulk-load all context.
  +
-- - Full-text search via SQLite FTS5
-- - Context retrieval for explain/solve pipelines
-- - Feed chunks to LLM for grounded answers
+++## Tool & Skill Routing ΓÇö Optimize the Right Tool at the Right Time
  +
-- ## MCP Server (`mcp_server.py`)
-- Model Context Protocol server exposing tools, resources, and prompts for AI integration.
+++Agents MUST consult `tools/crs_init.py --verify` and `.opencode/crs.json` before choosing a harness. Verbatim mapping:
  +
-- - Tools: search, get_topic, get_chapter, explain, solve, retrieve_context
-- - Prompts: study_guide, practice_session
-- - Communicates via stdio using JSON-RPC 2.0
+++| Intent | Right tool (lazy-load only this) |
+++|---|---|
+++| ingest 10+ URLs / bulk rewrite | `deepseek_harness.py` + `langgraph_pipeline.py` `Send` fanout 6 |
+++| explain / solve with syllabus grounding | `curriculum-guard` 3-tier ΓåÆ `rag_engine.py:hybrid_search(limit=5)` ΓåÆ `knowledge_graph.py` prerequisites |
+++| past paper / remedial | `historical-paper-tags` `prerequisite_nodes` + companion hint ΓåÆ `knowledge_graph.py:get_mastery()` |
+++| math render | `math-formatter` ΓåÆ KaTeX `$`/`$$`/`aligned` in `templates/base.html:51-53` |
+++| visualize / graph | `viz-generator` JSON `rendererType` ΓåÆ React |
+++| codebase Q&A / path between files | `graphify` (`path`/`explain`) OR `codebase-memory-mcp` `search_graph`/`trace_path` (moderate mode) |
+++| perf / scale | `mesh_lb` (`_archive/mesh_lb.py`) workers `3033/3036` + `nginx` `app:9090` |
+++| memory / streak | `supermemory 3.59.0` + `gamification.py` + `spaced_repetition.py` |
+++| fine-tune | `finetuning` skill `workflows/quickstart.md` ΓåÆ `validate_sft` ΓåÆ `submit_training` |
+++| noisy shell output | `tools/noise_gate.py` via `.opencode/plugins/noise-gate.js` ΓÇö auto filters installs/builds/tests to errors+summary; short commands passthrough |
  +
-- ## LLM Client (`llm_client.py`)
-- Unified LLM client supporting multiple backends.
+++**Active skills (all installed, leverage via triggers):** `master-architectural-system-prompt`, `curriculum-guard`, `math-formatter`, `historical-paper-tags`, `dual-mode-router`, `viz-generator`, `finetuning`, `graphify` (`/.opencode/plugins/graphify.js`). If user forgets a trigger, AGENT must still apply the relevant skill ΓÇö never skip, outcome would be unoptimized.
  +
-- - Priority: Claude API > Ollama > generic OpenAI-compatible server > local llama.cpp -> fallback
-- - Methods: `query()`, `explain_topic()`, `solve_problem()`
-- - Singleton via `get_client()`
+++**CRS modes:** `Caveman` (evidence-before-synthesis), `RTK` (hybrid search + OKF lineage), `Supermemory` (cross-session) are prompt harnesses, not pip packages. Wrong pips `caveman 1.0` / `RTk 0.3.14` were uninstalled ΓÇö do not reinstall.
+++
+++**Hook ΓÇö Noise Gate:** `.opencode/plugins/noise-gate.js` rewrites noisy `bash` commands (`pip install`, `npm build`, `pytest`, etc.) to `tools/noise_gate.py` so only `errors/failures/final summary` return to context. Short commands (<60 lines / <5KB) are left alone. Full logs stay at `$env:TEMP\opencode_noise_*.log`. See before/after in this doc footer.
+++
+++**Free Claude Code:** `claude.exe 2.1.245` at `C:\Users\Admin\.local\bin\claude.exe` (native, `claude update` channel `latest`). Keep in sync: `claude update` or `npm i -g @anthropic-ai/claude-code@latest`.
+++
+++## Entrypoints ΓÇö Don't Guess
+++
+++- **Primary:** `server.py` = FastAPI (`server:app`). `lifespan` inits DB + `get_client()` + `get_rag_engine()` + `get_index().build()`. Middleware: `CORSMiddleware *`, `GZipMiddleware`, `TrustedHostMiddleware`, `security.*`. Templates: `templates/base.html` via Jinja2.
+++- **Legacy:** `app.py` = `ThreadingHTTPServer` + `CBSEHandler`. Kept for `test_e2e.py` default (`http://localhost:9090`) but not used in dev (3033/3036). Prefer `server.py`.
+++- **MCP:** `mcp_server.py` stdio JSON-RPC tools: `search`, `get_topic`, `get_chapter`, `explain`, `solve`, `retrieve_context`.
+++- **Workers:** `mesh_lb` (`_archive/mesh_lb.py`) round-robin proxy for perf tests; not default dev server.
+++
+++## Commands ΓÇö Exact
+++
+++```bash
+++# Dev (current live ports)
+++python -m uvicorn server:app --host 127.0.0.1 --port 3033 --reload
+++python -m uvicorn server:app --host 127.0.0.1 --port 3036 --reload
+++# Any port: --host 0.0.0.0 to expose LAN (needs firewall)
+++
+++# Legacy / CI default
+++python app.py  # or: MODE=app ./start.sh  ΓåÆ 0.0.0.0:9090
+++
+++# DB
+++python db_seeder.py          # full reseed (also auto-seeds if topics==0 in lifespan)
+++python tools/sync_db.py --verify          # host Γåö volume (/app/data) check
+++python tools/sync_db.py --from-host       # push host cbse_content.db ΓåÆ Docker volume
+++
+++# Indexes (must rebuild after chunk/topic edits)
+++python -c "import sys; sys.path.insert(0,'.'); from json_index import get_index; get_index().build()"
+++# FTS: db.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')") ΓÇö auto via triggers
+++
+++# Tests ΓÇö note port mismatch!
+++python test_unit.py -v                          # no server needed (mocks fastapi)
+++python test_e2e.py --url http://127.0.0.1:3033  # default 9090 will fail on dev
+++python test_perf.py                             # expects BASE=http://localhost:9090, edit if testing 3033
+++flake8 . --select E9,F63,F7,F82  # CI lint step
+++
+++# Bulk URL ingest (48 Byjus + vast)
+++curl -X POST http://127.0.0.1:3033/api/ingest/urls -d '{"use_file":true}' -H "Content-Type: application/json"
+++# or: python -c "from langgraph_pipeline import run_pipeline; run_pipeline(urls)"
+++```
+++
+++## Architecture ΓÇö Non-Obvious
+++
+++- **DB abstraction `db.py` ΓåÆ `database.py`:** `DATABASE_URL` switches `sqlite:///cbse_content.db` (dev, WAL+SHM) Γåö `postgresql://` (Neon/prod). `db.py` translates `?`ΓåÆ`%s`, `INSERT OR REPLACE`ΓåÆ`ON CONFLICT`, FTS5ΓåÆ`tsvector`, `datetime('now')`ΓåÆ`CURRENT_TIMESTAMP`. Thread-local SQLite conn with `PRAGMA journal_mode=WAL; cache_size=-8000; busy_timeout=5000`.
+++- **Content hierarchy:** `boards(3) ΓåÆ subjects(36) ΓåÆ books ΓåÆ chapters(285) ΓåÆ topics(1222) ΓåÆ chunks(5295) + problems(4623)` ΓÇö `chunking.py:insert_*` + FTS5 virtual `chunks_fts` with triggers `chunks_ai/ad/au`.
+++- **Caching:** `syllabus_index.json` auto-deleted on `INSERT/UPDATE topics|chapters|chunks|problems` (`db.py:_invalidate_syllabus_cache`, `database.py:init_db`). `rag_engine.py` + `search` have 5-min TTL + `ai_content_cache` table. Invalidate if counts stale.
+++- **Monorepo boundary:** `vidyaa/` is separate Vite UI (not served by FastAPI); root serves only CBSE Class X companion.
+++- **LLM priority `llm_client.py`:** `MISTRAL_API_KEY` (mistral-large-latest 128k) > `GEMINI_API_KEY` > `DEEPSEEK_API_KEY` (`deepseek_harness.py`, 128k) ΓåÆ offline fallback `[AI Offline Mode]`. `get_client()` singleton; `config.yaml` is reference only, env vars win.
+++- **Docker gotchas:** `nginx.conf` upstream **must** be `app:9090` not `127.0.0.1` (nginx container's own loopback ΓåÆ 502). `docker-compose.yml` previously bound `.:/app` (breaks WAL on Windows); fixed variant `docker-compose.fixed.yml` uses `cbse_data:/app/data` + explicit `0.0.0.0:${PORT}` + `enable_ipv6: false` + `networks.cbse_net 10.20.30.0/24`. CI `.github/workflows/ci.yml` runs `ubuntu-latest` py 3.10-3.12, `test_unit.py` only + `app.py` for E2E (not `server:app`).
+++
+++## MathFormatter Skill ΓÇö Mandatory for All Math Content
+++
+++**Skill:** `~/.agents/skills/math-formatter/SKILL.md` ΓÇö triggers: `formula`, `calculate`, `render equations`, `math syntax`, `equations`.
+++
+++**Rendering stack:** `templates/base.html:51-53` loads KaTeX 0.16.8 + `auto-render` with delimiters `$$ΓÇª$$` display, `$ΓÇª$` inline, `\(...\)` inline. Never ship raw `/` fractions or Unicode math ΓÇö always LaTeX.
+++
+++**Rules (verbatim from skill):**
+++
+++- Inline: every variable/number/ratio in single `$ΓÇª$` ΓÇö e.g., `$a$`, `$x^2$`, `$\theta = 45^\circ$`, `$\Delta ABC$`, `$\frac{a}{b}$`.
+++- Block: complex/long proofs in double `$$ΓÇª$$` centered ΓÇö e.g., `$$ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} $$`.
+++- Multi-line: `aligned` environment, equals aligned:
+++  ```
+++  $$
+++  \begin{aligned}
+++  (x + 3)(x - 2) &= 0 \\
+++  x^2 + x - 6 &= 0
+++  \end{aligned}
+++  $$
+++  ```
+++- Fractions: `\frac{numerator}{denominator}`, never `a/b`. Geometry: `\triangle`, `\parallel`, `\angle`. Units: `$\boxed{\text{Answer} = 42\ \text{cm}}$`.
+++- Match NCERT 2026-27 / R.D. Sharma / R.S. Aggarwal notation exactly. Don't mix plaintext math + LaTeX.
+++
+++**Where formulas live & break:**
+++
+++- `app.py:render_math()` does superscript/subscript `str.maketrans` (`┬▓ΓåÆ^2`, `ΓéÇΓåÆ_0`, `ΓêÜ(ΓÇª)ΓåÆsqrt(ΓÇª)`) ΓÇö legacy, conflicts with KaTeX. Prefer LaTeX directly; avoid double-translating.
+++- `ai_services.py:generate_local_*_fallback()` returns HTML with inline styles ΓÇö ensure any math inside is LaTeX-wrapped so KaTeX `renderMathInElement` picks it up on `DOMContentLoaded`.
+++- `question_bank.py` + `chunks`/`problems` often store `x┬▓ - 3`, `ΓêÜ3`, `┬╜` ΓÇö must convert to ` $x^2 - 3$`, ` $\sqrt{3}$`, ` $\frac{1}{2}$` before rendering or in `format_content()`.
+++
+++## Math Validation ΓÇö Required Before Commit
+++
+++Validate **every** formula/numeric model against canonical sources (no guessing):
+++
+++1. **Cross-check** syllabus `Syllabus_2026-27/CBSE/Class_10/*.pdf` + NCERT textbook (board `CBSE`, not AP/TS state). For Class 6 baselines + R.D. Sharma extensions.
+++2. **Check types:** definitions, theorems, proofs, worked examples, diagram labels ΓÇö all must be syllabus-aligned 2026-27. Flag `Needs verification` if uncertain; never invent.
+++3. **Run:** `verify_ingestion_harness.py` + `python -c "from chunking import search_chunks; search_chunks('quadratic')"` to confirm FTS and LaTeX not broken.
+++4. **Visual check:** open `http://127.0.0.1:3033/topic/<id>` or `/search?q=quadratic` ΓÇö KaTeX must render, no raw `^`, `/`, or `ΓêÜ` visible. Test both `3033` and `3036` live ports.
+++
+++## Testing & Style Quirks
+++
+++- `test_unit.py` mocks `fastapi` etc. ΓÇö real server not needed. `test_e2e.py` hits live HTTP; fails if wrong `--url`.
+++- `test_perf.py` hardcodes `BASE=http://localhost:9090` ΓÇö edit constant when testing mesh LB.
+++- `mesh_lb.py` needs `WORKER_COUNT`/`BASE_PORT`/`LB_PORT` env; workers run `server.py` per port, round-robin. Use for stress/perf (`locust`/`ab`) via `python _archive/mesh_lb.py`.
+++- No `opencode.json` at root ΓÇö use CLI flags / env. Pre-commit not configured.
+++
+++## References
+++
+++- Skill files: `~/.agents/skills/math-formatter/`, `curriculum-guard`, `dual-mode-router` (Board vs JEE shortcuts).
+++- Trusted docs: `Syllabus_2026-27/CBSE/Class_10/`, `config.yaml` (env overrides), `database.py:SCHEMA_SQL` (ground truth schema).
+++
+++## Hook ΓÇö Before / After (Noise Gate)
+++
+++**Before (noisy, fills context):**
+++```
+++pip install fastapi uvicorn
+++  Collecting fastapi ... Downloading ... Progress ΓûêΓûêΓûêΓûêΓûêΓûê 12% ... Installing ... 84 lines of spam ...
+++pytest
+++  Progress ... 80 downloading lines ... 84 lines total
+++```
+++
+++**After (hook rewrites to `tools/noise_gate.py`):**
+++```
+++[noise-gate] filtered 84 -> 4 lines (4% kept) | source: $env:TEMP\opencode_noise_xxx.log
+++ERROR: Could not find a version that satisfies requirement bad-pkg==9.9.9
+++FAILED test_unit.py::test_edge FAILED
+++Traceback (most recent call last): File test_edge.py line 99
+++============================== 80 passed, 1 failed, 1 error in 4.12s ==============================
+++[noise-gate] dropped 80 noisy lines (progress/install spam). Full log: $env:TEMP\opencode_noise_xxx.log
+++```
+++
+++**Short commands passthrough untouched (<60 lines / <5KB):**
+++```
+++[noise-gate] passthrough (short output) | 52 lines ΓÇö full output shown verbatim
+++```
+++
+++Full logs always preserved at `*.log`; hook never touches non-noisy commands.
diff --cc cbse_content.db
index 7f6a1dc,7f6a1dc,0000000..599dfd5
mode 100644,100644,000000..100644
Binary files differ
diff --cc cbse_content.db-shm
index 8477603,8477603,0000000..a4b9062
mode 100644,100644,000000..100644
Binary files differ
diff --cc cbse_content.db-wal
index a24efb4,a24efb4,0000000..4e0dc52
mode 100644,100644,000000..100644
Binary files differ
diff --cc config.yaml
index 5f6824a,5f6824a,0000000..0b17792
mode 100644,100644,000000..100644
--- a/config.yaml
+++ b/config.yaml
@@@@ -1,4 -1,4 -1,0 +1,16 @@@@
  +model:
  +  provider: mistral  # Change from local/cpu to mistral api
  +  name: mistral-large-latest  # This has a large 128K context window
  +  api_key: "ollamakey"
+++
+++deepseek:
+++  api_key: "${DEEPSEEK_API_KEY}"  # set env DEEPSEEK_API_KEY to enable DeepSeek harness
+++  model: deepseek-chat   # or deepseek-reasoner for hard challenges
+++  concurrency: 6
+++  timeout: 45
+++
+++langgraph:
+++  checkpoint: memory
+++  max_concurrency: 6
+++  batch_pause_ms: 400
+++  retries: 3
diff --cc database.py
index 90fb4c2,90fb4c2,0000000..7ad8322
mode 100644,100644,000000..100644
--- a/database.py
+++ b/database.py
@@@@ -1,337 -1,337 -1,0 +1,342 @@@@
  +"""Database layer ΓÇö delegates to db.py abstraction (SQLite or PostgreSQL/Neon).
  +
  +Set DATABASE_URL to switch backends:
  +  sqlite:///cbse_content.db    ΓåÆ SQLite (local dev, default)
  +  postgresql://user:pass@host/db  ΓåÆ PostgreSQL / Neon (production)
  +"""
  +import os
  +import json
  +import logging
  +from db import get_db, DatabaseError as DbError
  +
  +log = logging.getLogger("cbse.db")
  +
  +DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "cbse_content.db"))
  +SCHEMA_SQL = """
  +CREATE TABLE IF NOT EXISTS boards (
  +    id TEXT PRIMARY KEY,
  +    name TEXT NOT NULL,
  +    description TEXT,
  +    ncert_url TEXT
  +);
  +
  +CREATE TABLE IF NOT EXISTS subjects (
  +    id TEXT PRIMARY KEY,
  +    board_id TEXT NOT NULL,
  +    name TEXT NOT NULL,
  +    code TEXT,
  +    description TEXT,
  +    ncert_url TEXT,
  +    class TEXT DEFAULT 'X'
  +);
  +
  +CREATE TABLE IF NOT EXISTS books (
  +    id TEXT PRIMARY KEY,
  +    subject_id TEXT NOT NULL,
  +    name TEXT NOT NULL,
  +    code TEXT,
  +    ncert_url TEXT
  +);
  +
  +CREATE TABLE IF NOT EXISTS chapters (
  +    id TEXT PRIMARY KEY,
  +    book_id TEXT,
  +    subject_id TEXT NOT NULL,
  +    board_id TEXT NOT NULL,
  +    num INTEGER NOT NULL,
  +    title TEXT NOT NULL
  +);
  +
  +CREATE TABLE IF NOT EXISTS topics (
  +    id TEXT PRIMARY KEY,
  +    chapter_id TEXT NOT NULL,
  +    num INTEGER,
  +    title TEXT NOT NULL,
  +    content TEXT
  +);
  +
  +CREATE TABLE IF NOT EXISTS chunks (
  +    id TEXT PRIMARY KEY,
  +    topic_id TEXT,
  +    chapter_id TEXT,
  +    parent_id TEXT,
  +    level INTEGER NOT NULL,
  +    title TEXT,
  +    content TEXT NOT NULL,
  +    content_type TEXT DEFAULT 'text',
  +    seq INTEGER
  +);
  +
  +CREATE TABLE IF NOT EXISTS problems (
  +    id TEXT PRIMARY KEY,
  +    topic_id TEXT,
  +    chapter_id TEXT NOT NULL,
  +    problem_text TEXT NOT NULL,
  +    solution_text TEXT,
  +    problem_type TEXT,
  +    seq INTEGER
  +);
  +
  +CREATE TABLE IF NOT EXISTS content_meta (
  +    key TEXT PRIMARY KEY,
  +    value TEXT
  +);
  +
  +CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
  +    title,
  +    content,
  +    content='chunks'
  +);
  +
  +CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
  +    INSERT INTO chunks_fts(rowid, title, content) VALUES (new.rowid, new.title, new.content);
  +END;
  +
  +CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
  +    INSERT INTO chunks_fts(chunks_fts, rowid, title, content) VALUES('delete', old.rowid, old.title, old.content);
  +END;
  +
  +CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
  +    INSERT INTO chunks_fts(chunks_fts, rowid, title, content) VALUES('delete', old.rowid, old.title, old.content);
  +    INSERT INTO chunks_fts(rowid, title, content) VALUES (new.rowid, new.title, new.content);
  +END;
  +
  +CREATE TABLE IF NOT EXISTS learner (
  +    id INTEGER PRIMARY KEY,
  +    name TEXT DEFAULT 'Learner',
  +    email TEXT,
  +    password_hash TEXT,
  +    xp INTEGER DEFAULT 0,
  +    level INTEGER DEFAULT 1,
  +    streak INTEGER DEFAULT 0,
  +    longest_streak INTEGER DEFAULT 0,
  +    last_active TEXT,
  +    lives INTEGER DEFAULT 5,
  +    max_lives INTEGER DEFAULT 5,
  +    last_life_refill TEXT,
  +    total_xp_earned INTEGER DEFAULT 0,
  +    topics_completed INTEGER DEFAULT 0,
  +    quizzes_taken INTEGER DEFAULT 0,
  +    quiz_correct INTEGER DEFAULT 0,
  +    quiz_total INTEGER DEFAULT 0,
  +    mock_exams_taken INTEGER DEFAULT 0
  +);
  +
  +CREATE TABLE IF NOT EXISTS sessions (
  +    token TEXT PRIMARY KEY,
  +    learner_id INTEGER DEFAULT 1,
  +    created_at TEXT DEFAULT (datetime('now','localtime')),
  +    expires_at TEXT DEFAULT (datetime('now','localtime', '+7 days'))
  +);
  +
  +CREATE TABLE IF NOT EXISTS xp_events (
  +    id INTEGER PRIMARY KEY AUTOINCREMENT,
  +    xp INTEGER NOT NULL,
  +    reason TEXT NOT NULL,
  +    detail TEXT,
  +    chapter_id TEXT,
  +    topic_id TEXT,
  +    created_at TEXT DEFAULT (datetime('now','localtime'))
  +);
  +
  +CREATE TABLE IF NOT EXISTS learning_progress (
  +    id INTEGER PRIMARY KEY AUTOINCREMENT,
  +    chapter_id TEXT NOT NULL,
  +    topic_id TEXT,
  +    status TEXT DEFAULT 'locked',
  +    xp_earned INTEGER DEFAULT 0,
  +    time_spent INTEGER DEFAULT 0,
  +    last_accessed TEXT,
  +    completions INTEGER DEFAULT 0,
  +    quiz_score REAL,
  +    UNIQUE(chapter_id, topic_id)
  +);
  +
  +CREATE TABLE IF NOT EXISTS lifeline_log (
  +    id INTEGER PRIMARY KEY AUTOINCREMENT,
  +    lifeline_type TEXT NOT NULL,
  +    chapter_id TEXT,
  +    topic_id TEXT,
  +    xp_cost INTEGER DEFAULT 5,
  +    used_at TEXT DEFAULT (datetime('now','localtime'))
  +);
  +
  +CREATE TABLE IF NOT EXISTS daily_challenges (
  +    challenge_date TEXT PRIMARY KEY,
  +    board_id TEXT,
  +    subject_id TEXT,
  +    type_id TEXT,
  +    question_ids TEXT,
  +    bonus_xp INTEGER DEFAULT 0,
  +    completed INTEGER DEFAULT 0,
  +    score INTEGER DEFAULT 0,
  +    total INTEGER DEFAULT 0,
  +    xp_earned INTEGER DEFAULT 0
  +);
  +
  +CREATE TABLE IF NOT EXISTS monitoring_pins (
  +    pin TEXT PRIMARY KEY,
  +    learner_id INTEGER DEFAULT 1,
  +    created_at TEXT DEFAULT (datetime('now','localtime')),
  +    expires_at TEXT,
  +    is_active INTEGER DEFAULT 1
  +);
  +
  +CREATE TABLE IF NOT EXISTS concept_views (
  +    id INTEGER PRIMARY KEY AUTOINCREMENT,
  +    topic_id TEXT,
  +    viewed_at TEXT DEFAULT (datetime('now','localtime'))
  +);
  +
  +CREATE TABLE IF NOT EXISTS content_pillars (
  +    id TEXT PRIMARY KEY,
  +    name TEXT NOT NULL,
  +    icon TEXT,
  +    description TEXT,
  +    color TEXT,
  +    sort_order INTEGER DEFAULT 0
  +);
  +
  +CREATE TABLE IF NOT EXISTS pillar_content (
  +    id INTEGER PRIMARY KEY AUTOINCREMENT,
  +    pillar_id TEXT NOT NULL,
  +    content_type TEXT NOT NULL,
  +    content_id TEXT NOT NULL,
  +    label TEXT,
  +    sort_order INTEGER DEFAULT 0,
  +    UNIQUE(pillar_id, content_type, content_id)
  +);
  +
  +CREATE TABLE IF NOT EXISTS knowledge_graph (
  +    id TEXT PRIMARY KEY,
  +    subject_id TEXT,
  +    chapter_id TEXT,
  +    topic_id TEXT,
  +    concept_name TEXT NOT NULL,
  +    difficulty INTEGER DEFAULT 1,
  +    parent_concept_id TEXT,
  +    description TEXT
  +);
  +
  +CREATE TABLE IF NOT EXISTS user_mastery (
  +    id INTEGER PRIMARY KEY AUTOINCREMENT,
  +    concept_id TEXT NOT NULL,
  +    learner_id INTEGER DEFAULT 1,
  +    mastery_level REAL DEFAULT 0.0,
  +    attempts INTEGER DEFAULT 0,
  +    correct INTEGER DEFAULT 0,
  +    total INTEGER DEFAULT 0,
  +    last_practiced TEXT,
  +    streak INTEGER DEFAULT 0,
  +    UNIQUE(concept_id, learner_id)
  +);
  +
  +CREATE TABLE IF NOT EXISTS ai_content_cache (
  +    cache_key TEXT PRIMARY KEY,
  +    result_json TEXT,
  +    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  +);
  +"""
  +
  +
  +def get_conn():
  +    """Return a database handle (backward-compatible with existing code).
  +
  +    Returns the db.Database singleton which provides execute/query/insert
  +    methods and dict-like Row objects (row['col'] or row.col).
  +    """
  +    return get_db()
  +
  +
  +def get_db():
  +    from db import get_db as _get_db
  +    return _get_db()
  +
  +
  +def init_db():
  +    db = get_db()
  +    db.executescript(SCHEMA_SQL)
  +
  +    # Safety ALTER TABLE for subjects table
  +    try:
  +        db.execute("ALTER TABLE subjects ADD COLUMN class TEXT DEFAULT 'X'")
  +    except Exception as e:
  +        log.debug("Column class already exists in subjects: %s", e)
  +
  +    # central indices for query optimization
  +    indexes = [
  +        "CREATE INDEX IF NOT EXISTS idx_chapters_subject ON chapters(subject_id)",
  +        "CREATE INDEX IF NOT EXISTS idx_chapters_board ON chapters(board_id)",
  +        "CREATE INDEX IF NOT EXISTS idx_topics_chapter ON topics(chapter_id)",
  +        "CREATE INDEX IF NOT EXISTS idx_chunks_topic ON chunks(topic_id)",
  +        "CREATE INDEX IF NOT EXISTS idx_chunks_chapter ON chunks(chapter_id)",
  +        "CREATE INDEX IF NOT EXISTS idx_problems_chapter ON problems(chapter_id)",
  +        "CREATE INDEX IF NOT EXISTS idx_problems_topic ON problems(topic_id)"
  +    ]
  +    for idx_sql in indexes:
  +        try:
  +            db.execute(idx_sql)
  +        except Exception as e:
  +            log.warning("Failed to create index (%s): %s", idx_sql, e)
  +
  +    for col in ("email", "password_hash"):
  +        try:
  +            db.execute(f"ALTER TABLE learner ADD COLUMN {col} TEXT")
  +        except Exception as e:
  +            log.debug("Column %s already exists: %s", col, e)
  +
  +    try:
  +        db.execute("INSERT INTO learner (id, name, xp, level, streak, lives, max_lives, last_active, last_life_refill) "
  +                    "VALUES (1, 'Learner', 0, 1, 0, 5, 5, date('now','localtime'), datetime('now','localtime')) "
  +                    "ON CONFLICT (id) DO NOTHING")
  +    except Exception as e:
  +        try:
  +            db.execute("INSERT OR IGNORE INTO learner (id, name, xp, level, streak, lives, max_lives, last_active, last_life_refill) "
  +                        "VALUES (1, 'Learner', 0, 1, 0, 5, 5, date('now','localtime'), datetime('now','localtime'))")
  +        except Exception as e2:
  +            log.warning("Failed to insert default learner: %s / %s", e, e2)
  +
  +    try:
  +        db.execute("INSERT OR IGNORE INTO content_meta (key, value) VALUES ('schema_version', '2.0')")
  +        db.execute("INSERT OR IGNORE INTO content_meta (key, value) VALUES ('total_chunks', '0')")
  +        db.execute("INSERT OR IGNORE INTO content_meta (key, value) VALUES ('last_indexed', '')")
  +    except Exception as e:
  +        log.warning("Failed to insert content_meta: %s", e)
  +
  +    from db import rebuild_fts as _rebuild_fts
  +    _rebuild_fts(db)
  +
  +    try:
  +        from badges import init_badges_table
  +        init_badges_table()
  +    except Exception as e:
  +        log.warning("Badges table init skipped: %s", e)
  +    try:
  +        from mock_exam import init_exam_tables
  +        init_exam_tables()
  +    except Exception as e:
  +        log.warning("Exam tables init skipped: %s", e)
  +    try:
  +        from spaced_repetition import init_review_tables
  +        init_review_tables()
  +    except Exception as e:
  +        log.warning("Review tables init skipped: %s", e)
+++    try:
+++        from enterprise.enterprise_schema import init_enterprise_schema
+++        init_enterprise_schema()
+++    except Exception as e:
+++        log.warning("Enterprise schema init skipped: %s", e)
  +
  +    # Invalidate syllabus cache
  +    try:
  +        import os
  +        cache_file = os.path.join(os.path.dirname(__file__), "syllabus_index.json")
  +        if os.path.exists(cache_file):
  +            os.remove(cache_file)
  +    except Exception as e:
  +        log.warning("Failed to invalidate syllabus cache: %s", e)
  +
  +
  +def close():
  +    db = get_db()
  +    db.close()
diff --cc server.py
index b0aa30c,b0aa30c,0000000..b0959b5
mode 100644,100644,000000..100644
--- a/server.py
+++ b/server.py
@@@@ -1,3416 -1,3416 -1,0 +1,3594 @@@@
  +"""FastAPI production server ΓÇö replaces ThreadingHTTPServer.
  +
  +Supports:
  +  - Async AI calls (non-blocking LLM queries)
  +  - Connection pooling (PostgreSQL/Neon) via db.py
  +  - CORS, rate limiting, health checks
  +  - Background task processing
  +  - Static file serving
  +  - Gradually replaces CBSEHandler routes
  +
  +Usage:
  +  DATABASE_URL=postgresql://user:pass@host/db uvicorn server:app --host 0.0.0.0 --port 9090 --workers 4
  +  DATABASE_URL=sqlite:///cbse_content.db uvicorn server:app --host 0.0.0.0 --port 9090 --reload
  +"""
  +import sys
  +import os
  +sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
  +import json
  +import re
  +import html as htmlmod
  +import hashlib
  +import random
  +import logging
  +import functools
  +import time
  +import uuid
  +import urllib.parse
  +from typing import Optional
  +import asyncio
  +from contextlib import asynccontextmanager
  +
  +from fastapi import FastAPI, Request, Response, Query, HTTPException, Depends
  +from json_index import get_index
  +from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, PlainTextResponse
  +from fastapi.middleware.cors import CORSMiddleware
  +from fastapi.middleware.gzip import GZipMiddleware
  +from fastapi.middleware.trustedhost import TrustedHostMiddleware
  +from pydantic import BaseModel, Field
  +
  +from fastapi.templating import Jinja2Templates
  +
  +templates = Jinja2Templates(directory="templates")
  +
  +from database import get_db, init_db, SCHEMA_SQL
  +from data import ALL_BOARDS, SUBJECTS
  +from chunking import get_chapter_tree, get_topic_with_context, search_chunks
  +from json_index import get_index
  +from rag_engine import get_engine as get_rag_engine
  +from llm_client import get_client
  +import ai_tutor
  +import interactives
  +import ai_services
  +import content_enricher
  +import gamification
  +import auth
  +import security
  +
  +from auth import require_user, get_current_user, signup, login, logout, is_configured
  +
  +log = logging.getLogger("cbse")
  +logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
  +
  +RATE_LIMIT_WINDOW = 60
  +RATE_LIMIT_MAX = 120
  +_RATE_LIMIT_MAX_ENTRIES = 10000
  +_rate_limit_store = {}
  +_RAW_HTML_VARS = {"board_name", "content", "extra_css", "description", "title"}
  +
  +DB = None
  +RAG = None
  +SEARCH_IDX = None
  +LLM = None
  +
  +
  +# ΓöÇΓöÇΓöÇ Rate Limiter ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
  +
  +def _rate_limit_cleanup():
  +    now_window = int(time.time() / RATE_LIMIT_WINDOW)
  +    cutoff = now_window - 2
  +    keys_to_delete = [k for k in _rate_limit_store if int(k.split(":")[-1]) < cutoff]
  +    for k in keys_to_delete:
  +        del _rate_limit_store[k]
  +    if len(_rate_limit_store) > _RATE_LIMIT_MAX_ENTRIES:
  +        sorted_keys = sorted(_rate_limit_store.keys(), key=lambda k: int(k.split(":")[-1]))
  +        for k in sorted_keys[:len(sorted_keys) - _RATE_LIMIT_MAX_ENTRIES]:
  +            del _rate_limit_store[k]
  +
  +def rate_limit(requests_per_min: int = 60):
  +    def decorator(func):
  +        @functools.wraps(func)
  +        async def wrapper(request: Request, *args, **kwargs):
  +            if len(_rate_limit_store) > _RATE_LIMIT_MAX_ENTRIES * 1.5:
  +                _rate_limit_cleanup()
  +            ip = request.client.host if request.client else "unknown"
  +            now = time.time()
  +            window = int(now / RATE_LIMIT_WINDOW)
  +            key = f"{ip}:{window}"
  +            count = _rate_limit_store.get(key, 0)
  +            if count >= requests_per_min:
  +                raise HTTPException(status_code=429, detail="Rate limit exceeded")
  +            _rate_limit_store[key] = count + 1
  +            return await func(request, *args, **kwargs)
  +        return wrapper
  +    return decorator
  +
  +
  +# ΓöÇΓöÇΓöÇ Helpers ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
  +
  +def esc_js(s):
  +    if s is None:
  +        return ""
  +    return str(s).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "").replace('"', '&quot;')
  +
  +
  +def _render(title="AI Study Companion for class V - Class XII", content="", extra_css="", body_class="", board_name="", description="", user=None) -> str:
  +    xp = "0"
  +    try:
  +        if DB and DB.table_exists("learner"):
  +            learner = DB.query_one("SELECT xp FROM learner WHERE id=1")
  +            if learner:
  +                xp = str(learner.get("xp", 0))
  +    except Exception:
  +        pass
  +
  +    template = templates.get_template("base.html")
  +    return template.render(
  +        title=title,
  +        description=description or "AI Study Companion for class V - Class XII with AI tutor, quizzes, interactive tools",
  +        content=content,
  +        extra_css=extra_css,
  +        body_class=body_class,
  +        board_name=board_name,
  +        xp=xp,
  +        user=user,
  +        auth_configured=is_configured(),
  +    )
  +
  +
  +def _safe_img_src(m):
  +    alt = m.group(1)
  +    src = m.group(2)
  +    if src.startswith("http://") or src.startswith("https://") or src.startswith("data:image/"):
  +        return f'<img src="{htmlmod.escape(src)}" alt="{htmlmod.escape(alt)}" style="max-width:100%;border-radius:6px;">'
  +    return f'<a href="{htmlmod.escape(src)}" rel="nofollow">{htmlmod.escape(alt)}</a>'
  +
  +def format_content(text):
  +    """Format AI/content text into safe HTML. Handles markdown-like syntax."""
  +    if not text:
  +        return ""
  +    text = str(text)
  +    text = htmlmod.escape(text)
  +    text = re.sub(r"\$\$(.*?)\$\$", r'<span class="math">\(\1\)</span>', text, flags=re.DOTALL)
  +    text = re.sub(r"!\[(.*?)\]\((.*?)\)", _safe_img_src, text)
  +    lines = text.split("\n")
  +    html_parts = []
  +    in_ol = False
  +    in_ul = False
  +    for line in lines:
  +        if re.match(r"^\d+[.)]\s", line):
  +            if not in_ol:
  +                if in_ul: html_parts.append("</ul>"); in_ul = False
  +                html_parts.append("<ol>"); in_ol = True
  +            html_parts.append(f"<li>{re.sub(r'^\d+[.)]\s', '', line)}</li>")
  +        elif re.match(r"^[-*]\s", line):
  +            if not in_ul:
  +                if in_ol: html_parts.append("</ol>"); in_ol = False
  +                html_parts.append("<ul>"); in_ul = True
  +            html_parts.append(f"<li>{re.sub(r'^[-*]\s', '', line)}</li>")
  +        elif re.match(r"^#{1,3}\s", line):
  +            if in_ol: html_parts.append("</ol>"); in_ol = False
  +            if in_ul: html_parts.append("</ul>"); in_ul = False
  +            html_parts.append(f"<h3>{re.sub(r'^#+\s', '', line)}</h3>")
  +        elif line.strip():
  +            if in_ol: html_parts.append("</ol>"); in_ol = False
  +            if in_ul: html_parts.append("</ul>"); in_ul = False
  +            html_parts.append(f"<p>{line}</p>")
  +        else:
  +            if in_ol: html_parts.append("</ol>"); in_ol = False
  +            if in_ul: html_parts.append("</ul>"); in_ul = False
  +    if in_ol: html_parts.append("</ol>")
  +    if in_ul: html_parts.append("</ul>")
  +    result = "".join(html_parts)
  +    return result
  +
  +
  +def _build_breadcrumb(items):
  +    """Build breadcrumb HTML from list of (label, url) tuples."""
  +    parts = []
  +    for label, url in items:
  +        if url:
  +            parts.append(f'<a href="{url}">{htmlmod.escape(label)}</a>')
  +        else:
  +            parts.append(htmlmod.escape(label))
  +    return '<span class="sep">ΓÇ║</span>'.join(parts)
  +
  +
  +def _get_topics(conn, chapter_id):
  +    return conn.query("SELECT * FROM topics WHERE chapter_id = ? ORDER BY num, title", (chapter_id,))
  +
  +
  +def _pomelli_hero_svg():
  +    """PomelliAI-generated SVG hero banner for the home page."""
  +    return '''<svg viewBox="0 0 900 120" style="width:100%;max-width:900px;height:auto;margin:0 auto 1rem;display:block;" xmlns="http://www.w3.org/2000/svg">
  +  <defs>
  +    <linearGradient id="hg" x1="0%" y1="0%" x2="100%" y2="100%">
  +      <stop offset="0%" stop-color="#4a90d9" stop-opacity="0.12"/>
  +      <stop offset="50%" stop-color="#2ecc71" stop-opacity="0.08"/>
  +      <stop offset="100%" stop-color="#9b59b6" stop-opacity="0.12"/>
  +    </linearGradient>
  +    <linearGradient id="bar1" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#4a90d9"/><stop offset="100%" stop-color="#357abd"/></linearGradient>
  +    <linearGradient id="bar2" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2ecc71"/><stop offset="100%" stop-color="#27ae60"/></linearGradient>
  +    <linearGradient id="bar3" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#9b59b6"/><stop offset="100%" stop-color="#8e44ad"/></linearGradient>
  +  </defs>
  +  <rect width="900" height="120" fill="url(#hg)" rx="16"/>
  +  <g opacity="0.6">
  +    <rect x="40" y="70" width="24" height="40" rx="4" fill="url(#bar1)"><animate attributeName="height" values="40;50;30;40" dur="3s" repeatCount="indefinite"/><animate attributeName="y" values="70;60;80;70" dur="3s" repeatCount="indefinite"/></rect>
  +    <rect x="74" y="55" width="24" height="55" rx="4" fill="url(#bar2)"><animate attributeName="height" values="55;65;45;55" dur="3.5s" repeatCount="indefinite"/><animate attributeName="y" values="55;45;65;55" dur="3.5s" repeatCount="indefinite"/></rect>
  +    <rect x="108" y="60" width="24" height="50" rx="4" fill="url(#bar3)"><animate attributeName="height" values="50;40;60;50" dur="2.8s" repeatCount="indefinite"/><animate attributeName="y" values="60;70;50;60" dur="2.8s" repeatCount="indefinite"/></rect>
  +    <rect x="142" y="45" width="24" height="65" rx="4" fill="url(#bar1)"><animate attributeName="height" values="65;55;70;65" dur="3.2s" repeatCount="indefinite"/><animate attributeName="y" values="45;55;40;45" dur="3.2s" repeatCount="indefinite"/></rect>
  +    <rect x="176" y="65" width="24" height="45" rx="4" fill="url(#bar2)"><animate attributeName="height" values="45;55;35;45" dur="2.5s" repeatCount="indefinite"/><animate attributeName="y" values="65;55;75;65" dur="2.5s" repeatCount="indefinite"/></rect>
  +    <rect x="210" y="50" width="24" height="60" rx="4" fill="url(#bar3)"><animate attributeName="height" values="60;50;70;60" dur="3.7s" repeatCount="indefinite"/><animate attributeName="y" values="50;60;40;50" dur="3.7s" repeatCount="indefinite"/></rect>
  +    <rect x="244" y="40" width="24" height="70" rx="4" fill="url(#bar1)"><animate attributeName="height" values="70;60;75;70" dur="2.9s" repeatCount="indefinite"/></rect>
  +  </g>
  +  <circle cx="380" cy="55" r="20" fill="#4a90d9" opacity="0.15"><animate attributeName="r" values="20;25;18;20" dur="4s" repeatCount="indefinite"/></circle>
  +  <circle cx="420" cy="70" r="14" fill="#2ecc71" opacity="0.12"><animate attributeName="r" values="14;18;12;14" dur="3.5s" repeatCount="indefinite"/></circle>
  +  <circle cx="450" cy="45" r="10" fill="#9b59b6" opacity="0.15"><animate attributeName="r" values="10;14;8;10" dur="3s" repeatCount="indefinite"/></circle>
  +  <text x="530" y="55" font-family="sans-serif" font-size="20" font-weight="700" fill="#1a1a2e">AI Study Companion</text>
  +  <text x="530" y="82" font-family="sans-serif" font-size="13" fill="#666">CBSE ┬╖ AP Board ┬╖ TS Board ┬╖ Class VΓÇôXII</text>
  +  <text x="530" y="100" font-family="sans-serif" font-size="11" fill="#999">English ┬╖ αñ╣αñ┐αñ¿αÑìαñªαÑÇ ┬╖ α░ñα▒åα░▓α▒üα░ùα▒ü</text>
  +  <g transform="translate(700,20)" opacity="0.3">
  +    <path d="M30 30 L70 30 L90 60 L50 60 Z" fill="#4a90d9"/>
  +    <path d="M10 60 L50 60 L70 90 L30 90 Z" fill="#2ecc71"/>
  +    <path d="M50 60 L90 60 L110 90 L70 90 Z" fill="#9b59b6"/>
  +  </g>
  +</svg>'''
  +
  +
  +def _get_chapters(conn, subject_id):
  +    return conn.query("SELECT * FROM chapters WHERE subject_id = ? ORDER BY num", (subject_id,))
  +
  +
  +# ΓöÇΓöÇΓöÇ Lifespan ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
  +
  +@asynccontextmanager
  +async def lifespan(app: FastAPI):
  +    global DB, RAG, LLM
  +    log.info("FastAPI server starting...")
  +    DB = get_db()
  +    try:
  +        LLM = get_client()
  +    except Exception as e:
  +        log.warning("LLM init failed (non-fatal): %s", e)
  +    try:
  +        RAG = get_rag_engine()
  +    except Exception as e:
  +        log.warning("RAG engine init failed (non-fatal): %s", e)
  +    try:
  +        get_index()
  +    except Exception as e:
  +        log.warning("JsonIndex init failed (non-fatal): %s", e)
  +    init_db()
  +    try:
  +        # Force update board names to ensure dropdowns are immediately updated
  +        DB.execute("UPDATE boards SET name = 'CBSE' WHERE id = 'cbse'")
  +        DB.execute("UPDATE boards SET name = 'State board of AP' WHERE id = 'ap'")
  +        DB.execute("UPDATE boards SET name = 'Telangana Board' WHERE id = 'ts'")
  +        DB.commit()
  +    except Exception as e:
  +        log.warning("Failed to force update board names: %s", e)
  +
  +    # Auto-seed check for stateless in-memory or empty databases
  +    try:
  +        topic_count = DB.query_one("SELECT COUNT(*) as cnt FROM topics")["cnt"]
  +    except Exception:
  +        topic_count = 0
  +
  +    if topic_count == 0:
  +        log.info("Database is empty. Running db_seeder to populate content...")
  +        try:
  +            import db_seeder
  +            db_seeder.seed_database_full()
  +            # Force rebuild index after seeding
  +            get_index().build()
  +        except Exception as e:
  +            log.warning("Auto-seeding failed: %s", e)
  +
  +    log.info("Database: %s", "PostgreSQL/Neon" if DB.is_postgresql else "SQLite")
  +    log.info("LLM: %s (%s)", getattr(LLM, 'backend_name', 'N/A') if LLM else "N/A",
  +             getattr(LLM, 'model_name', 'N/A') if LLM else "N/A")
  +    yield
  +    log.info("Server shutting down.")
  +
  +
  +# ΓöÇΓöÇΓöÇ FastAPI App ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
  +
  +app = FastAPI(
  +    title="AI Study Companion",
  +    version="3.0.0",
  +    lifespan=lifespan,
  +    docs_url="/docs" if os.environ.get("ENV") == "dev" else None,
  +    redoc_url=None,
  +)
  +
  +app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
  +app.add_middleware(GZipMiddleware, minimum_size=500)
  +app.add_middleware(TrustedHostMiddleware, allowed_hosts=os.environ.get("ALLOWED_HOSTS", "*").split(","))
  +app.add_middleware(security.SecurityHeadersMiddleware)
  +app.add_middleware(security.CSRFSafeMiddleware)
  +
  +
+++
+++# ΓöÇΓöÇΓöÇ LangGraph + DeepSeek Ingestion ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
+++from pydantic import BaseModel as _PydanticBase
+++class IngestRequest(_PydanticBase):
+++    urls: list[str] = []
+++    use_file: bool = False  # if true, reads D:\\StudyMaterials.txt byjus urls
+++    max_concurrency: int = 6
+++    provider: str = "deepseek"  # deepseek | mistral | offline
+++
+++@app.post("/api/ingest/urls")
+++async def api_ingest_urls(req: IngestRequest, request: Request):
+++    """LangGraph + DeepSeek harness for multiple URLs / vast content.
+++    Handles: fetch (httpx, retry 429), clean, DeepSeek neutralize_rewrite, verify 2026-27, chunk validate, DB insert, FTS+index rebuild.
+++    Concurrency batched, rate-limit aware. Returns stats."""
+++    import time, asyncio
+++    urls = req.urls or []
+++    if req.use_file:
+++        try:
+++            with open(r"D:\StudyMaterials.txt", encoding="utf-8", errors="replace") as f:
+++                file_urls = [l.strip() for l in f if "byjus.com" in l.lower()]
+++                # dedup
+++                seen=set()
+++                uniq=[]
+++                for u in file_urls:
+++                    if u not in seen:
+++                        seen.add(u); uniq.append(u)
+++                urls = uniq
+++        except Exception as e:
+++            raise HTTPException(status_code=500, detail=f"Failed to read D:/StudyMaterials.txt: {e}")
+++    if not urls:
+++        raise HTTPException(status_code=400, detail="No URLs provided. Use urls:[...] or use_file:true")
+++    # offload blocking LangGraph to threadpool
+++    def _run():
+++        try:
+++            from langgraph_pipeline import run_pipeline
+++            return run_pipeline(urls, max_concurrency=req.max_concurrency)
+++        except Exception as e:
+++            import traceback
+++            return {"error": str(e), "traceback": traceback.format_exc()[:3000], "ingested":0}
+++    loop = asyncio.get_event_loop()
+++    stats = await loop.run_in_executor(None, _run)
+++    if "error" in stats:
+++        return JSONResponse({"status":"error", **stats}, status_code=500)
+++    return {"status":"ok", "provider": req.provider, "total": len(urls), **stats}
+++
+++@app.get("/api/ingest/status")
+++async def api_ingest_status():
+++    try:
+++        db = get_db()
+++        keys = ["langgraph_deepseek_last_run","byjus_supplementary_ingested_2026_27","syllabus_year","quiz_alignment_2026_27"]
+++        out={}
+++        for k in keys:
+++            row=db.query_one("SELECT value FROM content_meta WHERE key=?", (k,))
+++            out[k]=row["value"][:800] if row and row["value"] else None
+++        sup_cnt=db.query_one("SELECT COUNT(*) as cnt FROM chunks WHERE content_type='supplementary'")
+++        out["supplementary_chunks"]=sup_cnt["cnt"] if sup_cnt else 0
+++        sup_t=db.query_one("SELECT COUNT(*) as cnt FROM topics WHERE title LIKE '%Supplementary%'")
+++        out["supplementary_topics"]=sup_t["cnt"] if sup_t else 0
+++        out["deepseek_available"]=False
+++        try:
+++            from deepseek_harness import get_harness
+++            out["deepseek_available"]=get_harness().available
+++            out["deepseek_backend"]=get_harness().backend_name
+++        except: pass
+++        return out
+++    except Exception as e:
+++        return {"error": str(e)}
+++
+++@app.get("/api/ingest/deepseek-test")
+++async def api_deepseek_test(q: str = "Explain Real Numbers FTA"):
+++    try:
+++        from deepseek_harness import get_harness
+++        h=get_harness()
+++        if not h.available:
+++            return {"available": False, "message": "Set DEEPSEEK_API_KEY env to enable. Fallback active.", "sample": h.neutralize_rewrite("Test Real Numbers content about Euclid's lemma a=bq+r", "Real Numbers", "Mathematics")[:800]}
+++        res=h.query(q, system_prompt="You are a CBSE expert. Answer concisely.", max_tokens=256)
+++        return {"available": True, "backend": h.backend_name, "model": h.model, "result": res[:2000]}
+++    except Exception as e:
+++        return {"error": str(e)}
+++
+++
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +# HEALTH & STATUS
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +
  +@app.get("/health")
  +async def health():
  +    db_status = "N/A"
  +    try:
  +        if DB:
  +            DB.query_one("SELECT 1")
  +            db_status = f"{DB.backend} (connected)"
  +    except Exception:
  +        db_status = f"{DB.backend if DB else 'N/A'} (unreachable)"
  +    return {"status": "ok" if "connected" in db_status else "degraded",
  +            "db": db_status,
  +            "llm": getattr(LLM, 'backend_name', 'N/A') if LLM else "N/A",
  +            "model": getattr(LLM, 'model_name', 'N/A') if LLM else "N/A",
  +            "boards": len(ALL_BOARDS)}
  +
  +
  +@app.get("/api/admin/reseed-db")
  +async def admin_reseed_db():
  +    import db_seeder
  +    try:
  +        stats = db_seeder.seed_database_full()
  +        # Force reload of JSON index in memory
  +        from json_index import get_index
  +        idx = get_index()
  +        idx.build()
  +        return {"status": "success", "message": "Database seeded and solved successfully", "stats": stats}
  +    except Exception as e:
  +        return {"status": "error", "message": str(e)}
  +
  +
  +@app.get("/api/admin/db-status")
  +async def db_status_endpoint():
  +    conn = DB
  +    stats = {}
  +    try:
  +        stats["boards"] = [dict(r) for r in conn.query("SELECT id, name FROM boards")]
  +        stats["subjects"] = [dict(r) for r in conn.query("SELECT id, board_id, name FROM subjects")]
  +        stats["chapters_count"] = conn.query_one("SELECT COUNT(*) as cnt FROM chapters")["cnt"]
  +        stats["topics_count"] = conn.query_one("SELECT COUNT(*) as cnt FROM topics")["cnt"]
  +        stats["chunks_count"] = conn.query_one("SELECT COUNT(*) as cnt FROM chunks")["cnt"]
  +        stats["problems_count"] = conn.query_one("SELECT COUNT(*) as cnt FROM problems")["cnt"]
  +        
  +        # Count problems by subject
  +        problems_by_subject = conn.query("""
  +            SELECT s.name as subject_name, COUNT(p.id) as cnt
  +            FROM problems p
  +            JOIN chapters c ON p.chapter_id = c.id
  +            JOIN subjects s ON c.subject_id = s.id
  +            GROUP BY s.name
  +        """)
  +        stats["problems_by_subject"] = [dict(r) for r in problems_by_subject]
  +
  +        # Check for empty/placeholder solutions
  +        unsolved_count = conn.query_one("""
  +            SELECT COUNT(*) as cnt
  +            FROM problems
  +            WHERE solution_text IS NULL 
  +               OR solution_text = '' 
  +               OR LOWER(solution_text) LIKE '%placeholder%' 
  +               OR LOWER(solution_text) LIKE '%lorem ipsum%'
  +        """)["cnt"]
  +        stats["unsolved_count"] = unsolved_count
  +        
  +        # Sample unsolved problems
  +        sample_unsolved = conn.query("""
  +            SELECT p.id, p.problem_text, p.solution_text, s.name as subject_name
  +            FROM problems p
  +            JOIN chapters c ON p.chapter_id = c.id
  +            JOIN subjects s ON c.subject_id = s.id
  +            WHERE p.solution_text IS NULL 
  +               OR p.solution_text = '' 
  +               OR LOWER(p.solution_text) LIKE '%placeholder%' 
  +               OR LOWER(p.solution_text) LIKE '%lorem ipsum%'
  +            LIMIT 5
  +        """)
  +        stats["sample_unsolved"] = [dict(r) for r in sample_unsolved]
  +
  +    except Exception as e:
  +        stats["error"] = str(e)
  +    return stats
  +
  +
  +@app.get("/api/ai/status")
  +async def ai_status():
  +    if not LLM:
  +        return {"status": "unavailable", "message": "No LLM backend configured"}
  +    return LLM.get_status()
  +
  +
  +@app.get("/test-import")
  +async def test_import_endpoint():
  +    import sys, os, traceback
  +    _archive_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_archive")
  +    exists = os.path.exists(_archive_dir)
  +    sys.path.insert(0, _archive_dir)
  +    
  +    output = []
  +    output.append(f"Archive dir exists: {exists}")
  +    output.append(f"sys.path: {sys.path}")
  +    
  +    try:
  +        from _archive.enrich_all import PHASE1_SUBJECTS
  +        output.append("SUCCESS importing enrich_all!")
  +    except Exception as e:
  +        output.append(f"ERROR: {e}")
  +        output.append(traceback.format_exc())
  +        
  +    return {"output": "\n".join(output)}
  +
  +
  +@app.get("/trigger-reseed")
  +async def trigger_reseed_endpoint():
  +    import sys, os, traceback
  +    for k in list(sys.modules.keys()):
  +        if "db_seeder" in k or "_archive" in k or "scraper" in k:
  +            del sys.modules[k]
  +    try:
  +        import db_seeder
  +        stats = db_seeder.seed_database_full()
  +        return {"status": "success", "stats": stats}
  +    except Exception as e:
  +        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}
  +
  +
  +@app.get("/api/admin/restart")
  +async def admin_restart():
  +    import os, shutil, signal
  +    # Clean __pycache__ folders
  +    base_dir = os.path.dirname(os.path.abspath(__file__))
  +    for root, dirs, files in os.walk(base_dir):
  +        for d in dirs:
  +            if d == "__pycache__":
  +                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
  +        for f in files:
  +            if f.endswith(".pyc") or f.endswith(".pyo"):
  +                try:
  +                    os.remove(os.path.join(root, f))
  +                except Exception:
  +                    pass
  +    try:
  +        os.system("pkill -9 -f uvicorn")
  +    except Exception:
  +        pass
  +    try:
  +        os.kill(os.getppid(), signal.SIGKILL)
  +    except Exception:
  +        pass
  +    os._exit(0)
  +
  +
  +@app.get("/api/audit/data")
  +async def api_audit_data():
  +    import json, os, re as _re
  +    data = {}
  +    data['config_sources'] = {'os_environ_get': 26, 'hardcoded_urls': 1, 'hardcoded_data': 5, 'hardcoded_schema': 1, 'cli_args': 2, 'hardcoded_security': 1}
  +    data['modalities'] = {'text_generation': 12, 'svg_diagrams': 3, 'mermaid_js': 1, 'html_canvas': 10, 'video_embed': 3, 'audio_tts': 2, 'youtube_api': 1, 'image_gen': 0, 'audio_gen': 0, 'video_gen': 0}
  +    data['system_prompts'] = {'Napkin Diagram': 1, 'Presentation': 1, 'Paraphrase': 1, 'Research': 1, 'Literature': 1, 'SVG': 1, 'Story': 1, 'Gemma4': 1, 'MetaAI': 1, 'NotebookLM': 1, 'Enricher': 3, 'Tutor': 1}
  +    data['schema_validation'] = {'pydantic_models': 2, 'query_params_validated': 32, 'form_no_model': 5, 'missing': 20}
  +    data['async_vs_sync'] = {'async_functions': 85, 'sync_functions': 63, 'async_io_threaded': 20, 'sync_io_not_threaded': 12, 'async_database': 0}
  +    data['async_breakdown'] = {'page_routes': 30, 'api_endpoints': 32, 'auth': 7, 'middleware': 2, 'utility': 3, 'legacy_shim': 1}
  +    data['caching'] = {'in_memory_ttl': 2, 'in_memory_not_ttl': 2, 'db_backed': 1, 'file_based': 1, 'no_cache': 12}
  +    data['cache_risk'] = {'memory_leak': 2, 'hash_stability': 1, 'no_migrations': 1, 'ttl_only': 2, 'well_managed': 2}
  +    data['perf'] = {'health': 2, 'home': 21, 'board': 2, 'chapter': 5, 'topic': 4, 'api_status': 1, 'api_search': 5}
  +    data['routes'] = {'pages': 50, 'api': 32, 'ai_api': 19, 'ai_pages': 13, 'legacy': 1, 'static': 1}
  +    data['error_handling'] = {'try_except': 45, 'http_exceptions': 8, 'not_found': 18, 'fallbacks': 6, 'rate_limited': 24, 'unprotected': 8}
  +    return data
  +
  +
  +@app.get("/audit-dashboard", response_class=HTMLResponse)
  +async def audit_dashboard():
  +    try:
  +        with open("templates/audit.html") as f:
  +            return HTMLResponse(f.read())
  +    except Exception:
  +        return HTMLResponse("<h1>Audit Dashboard</h1><p>Template not found</p>")
  +
  +
  +@app.get("/api/view_logs")
  +async def view_logs():
  +    import glob
  +    log_content = ""
  +    log_files = ["/tmp/server.log", "server.log", "app.log"]
  +    found_file = None
  +    for lf in log_files:
  +        if os.path.exists(lf):
  +            found_file = lf
  +            break
  +    if not found_file:
  +        all_logs = glob.glob("/tmp/*.log") + glob.glob("*.log")
  +        if all_logs:
  +            found_file = all_logs[0]
  +            
  +    if found_file:
  +        try:
  +            with open(found_file, "r", encoding="utf-8", errors="replace") as f:
  +                log_content = f.read()[-8000:]
  +            return {"file": found_file, "logs": log_content}
  +        except Exception as e:
  +            return {"error": f"Failed to read {found_file}: {e}"}
  +    return {"error": "No log files found", "searched": log_files}
  +
  +
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +# PROFILE & PROGRESS (protected)
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +
  +
  +@app.get("/profile", response_class=HTMLResponse)
  +async def profile_page(user: Optional[dict] = Depends(get_current_user)):
  +    if not user:
  +        return _render(
  +            title="Profile ΓÇö AI Study Companion",
  +            content=f"""
  +            <div class="card" style="text-align:center;padding:3rem 2rem;">
  +                <h2>≡ƒöÆ Profile</h2>
  +                <p style="margin:1rem 0;color:#666;">Sign in to view your profile, progress, and achievements.</p>
  +                <a href="/login" class="btn-primary" style="display:inline-block;padding:0.8rem 2rem;background:var(--accent);color:#fff;border-radius:8px;text-decoration:none;">Sign In</a>
  +                <span style="margin:0 0.5rem">or</span>
  +                <a href="/register" style="color:var(--accent);">Create Account</a>
  +            </div>
  +            """,
  +        )
  +    return _render(
  +        title=f"Profile ΓÇö {user['username']} | AI Study Companion",
  +        content=f"""
  +        <div class="card">
  +            <h2>≡ƒæñ {user['username']}</h2>
  +            <p>Email: {user['email']}</p>
  +            <p>User ID: {user['id']}</p>
  +        </div>
  +        """,
  +    )
  +
  +
  +@app.get("/progress", response_class=HTMLResponse)
  +async def progress_page(user: dict = Depends(require_user)):
  +    return _render(
  +        title="My Progress | AI Study Companion",
  +        content="""
  +        <div class="card">
  +            <h2>≡ƒôè Learning Progress</h2>
  +            <p>Progress tracking coming soon.</p>
  +        </div>
  +        """,
  +    )
  +
  +
  +@app.get("/leaderboard", response_class=HTMLResponse)
  +async def leaderboard_page(user: dict = Depends(get_current_user)):
  +    try:
  +        learners = DB.query("SELECT username, xp, level FROM learner ORDER BY xp DESC LIMIT 50") if DB else []
  +    except Exception:
  +        learners = []
  +    rows = "".join(
  +        f"<tr><td>{i+1}</td><td>{l['username']}</td><td>{l['xp']}</td><td>{l['level']}</td></tr>"
  +        for i, l in enumerate(learners)
  +    )
  +    return _render(
  +        title="Leaderboard | AI Study Companion",
  +        content=f"""
  +        <div class="card">
  +            <h2>≡ƒÅå Leaderboard</h2>
  +            <table class="data-table"><tr><th>#</th><th>User</th><th>XP</th><th>Level</th></tr>{rows}</table>
  +        </div>
  +        """,
  +    )
  +
  +
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +# AUTH (Supabase JWT)
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +
  +from pydantic import BaseModel
  +
  +
  +class AuthSignup(BaseModel):
  +    email: str
  +    password: str
  +    username: str = ""
  +
  +
  +@app.get("/login", response_class=HTMLResponse)
  +async def login_page():
  +    return _render(
  +        title="Login | AI Study Companion",
  +        content="""
  +        <div class="card" style="max-width:400px;margin:2rem auto;">
  +            <h2>≡ƒöÉ Login</h2>
  +            <form id="login-form" onsubmit="return doLogin(event)">
  +                <div class="form-group">
  +                    <label for="email">Email</label>
  +                    <input type="email" id="email" name="email" required class="form-input" placeholder="your@email.com">
  +                </div>
  +                <div class="form-group">
  +                    <label for="password">Password</label>
  +                    <input type="password" id="password" name="password" required class="form-input" placeholder="ΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇó">
  +                </div>
  +                <button type="submit" class="btn btn-primary" style="width:100%;">Login</button>
  +                <p style="text-align:center;margin-top:1rem;">Don't have an account? <a href="/signup">Sign up</a></p>
  +            </form>
  +            <div id="login-error" style="color:var(--error);display:none;"></div>
  +        </div>
  +        <script>
  +        async function doLogin(e){
  +            e.preventDefault();
  +            const email=document.getElementById('email').value;
  +            const password=document.getElementById('password').value;
  +            try{
  +                const r=await fetch('/api/auth/login',{
  +                    method:'POST',
  +                    headers:{'Content-Type':'application/json'},
  +                    body:JSON.stringify({email,password})
  +                });
  +                const d=await r.json();
  +                if(d.success){window.location.href='/profile';}
  +                else{document.getElementById('login-error').style.display='block';
  +                     document.getElementById('login-error').textContent=d.detail||'Login failed';}
  +            }catch(e){
  +                document.getElementById('login-error').style.display='block';
  +                document.getElementById('login-error').textContent='Network error';
  +            }
  +            return false;
  +        }
  +        </script>
  +        """,
  +    )
  +
  +
  +@app.get("/signup", response_class=HTMLResponse)
  +async def signup_page():
  +    return _render(
  +        title="Sign Up | AI Study Companion",
  +        content="""
  +        <div class="card" style="max-width:400px;margin:2rem auto;">
  +            <h2>≡ƒô¥ Create Account</h2>
  +            <form id="signup-form" onsubmit="return doSignup(event)">
  +                <div class="form-group">
  +                    <label for="su-email">Email</label>
  +                    <input type="email" id="su-email" name="email" required class="form-input">
  +                </div>
  +                <div class="form-group">
  +                    <label for="su-username">Username</label>
  +                    <input type="text" id="su-username" name="username" class="form-input" placeholder="optional">
  +                </div>
  +                <div class="form-group">
  +                    <label for="su-password">Password</label>
  +                    <input type="password" id="su-password" name="password" required class="form-input" minlength="6">
  +                </div>
  +                <button type="submit" class="btn btn-primary" style="width:100%;">Create Account</button>
  +                <p style="text-align:center;margin-top:1rem;">Already have an account? <a href="/login">Login</a></p>
  +            </form>
  +            <div id="signup-error" style="color:var(--error);display:none;"></div>
  +            <div id="signup-success" style="color:var(--success);display:none;"></div>
  +        </div>
  +        <script>
  +        async function doSignup(e){
  +            e.preventDefault();
  +            const email=document.getElementById('su-email').value;
  +            const username=document.getElementById('su-username').value;
  +            const password=document.getElementById('su-password').value;
  +            try{
  +                const r=await fetch('/api/auth/signup',{
  +                    method:'POST',
  +                    headers:{'Content-Type':'application/json'},
  +                    body:JSON.stringify({email,password,username})
  +                });
  +                const d=await r.json();
  +                if(d.success){
  +                    document.getElementById('signup-success').style.display='block';
  +                    document.getElementById('signup-success').textContent='Account created! Redirecting...';
  +                    setTimeout(()=>window.location.href='/login',1500);
  +                }else{
  +                    document.getElementById('signup-error').style.display='block';
  +                    document.getElementById('signup-error').textContent=JSON.stringify(d.detail||d);
  +                }
  +            }catch(e){
  +                document.getElementById('signup-error').style.display='block';
  +                document.getElementById('signup-error').textContent='Network error';
  +            }
  +            return false;
  +        }
  +        </script>
  +        """,
  +    )
  +
  +
  +class AuthLogin(BaseModel):
  +    email: str
  +    password: str
  +
  +
  +@app.get("/api/auth/config")
  +async def auth_config():
  +    """Tell the frontend whether auth is available."""
  +    return {"configured": is_configured()}
  +
  +
  +@app.post("/api/auth/signup")
  +async def api_signup(data: AuthSignup, request: Request):
  +    """Register a new user."""
  +    return await signup(data.email, data.password, data.username)
  +
  +
  +@app.post("/api/auth/login")
  +async def api_login(data: AuthLogin, request: Request):
  +    """Authenticate and return JWT."""
  +    result = await login(data.email, data.password)
  +    response = JSONResponse(content=result)
  +    if result.get("access_token"):
  +        response.set_cookie(
  +            key="access_token",
  +            value=result["access_token"],
  +            httponly=True,
  +            secure=True,
  +            samesite="lax",
  +            max_age=86400 * 7,
  +        )
  +    return response
  +
  +
  +@app.post("/api/auth/logout")
  +async def api_logout(request: Request):
  +    """Revoke session."""
  +    token = request.cookies.get("access_token", "")
  +    auth_header = request.headers.get("Authorization", "")
  +    if auth_header.startswith("Bearer "):
  +        token = auth_header[7:]
  +    await logout(token)
  +    response = JSONResponse({"success": True})
  +    response.delete_cookie("access_token")
  +    return response
  +
  +
  +@app.get("/api/auth/me")
  +async def api_auth_me(user: dict = Depends(get_current_user)):
  +    """Return current user info or 401."""
  +    if not user:
  +        raise HTTPException(status_code=401, detail="Not authenticated")
  +    return {"authenticated": True, "user": user}
  +
  +
  +@app.get("/style.css")
  +async def style_css():
  +    if os.path.exists("style.css"):
  +        return FileResponse("style.css")
  +    from app import CSS
  +    return Response(content=CSS, media_type="text/css")
  +
+++@app.get("/style_vidya.css")
+++async def style_vidya_css():
+++    p = "style_vidya.css"
+++    if os.path.exists(p):
+++        return FileResponse(p, media_type="text/css")
+++    return Response(content="/* vidya tokens missing */", media_type="text/css")
+++
  +
  +@app.get("/manifest.json")
  +async def manifest_json():
  +    if os.path.exists("manifest.json"):
  +        return FileResponse("manifest.json")
  +    manifest = {
--         "name": "Class X Education Platform",
--         "short_name": "Class X Edu",
--         "description": "CBSE, AP & TS Board Class X study platform",
+++        "name": "VidyaGyaan ΓÇö CBSE Class X (2026-27) AI Companion",
+++        "short_name": "VidyaGyaan",
+++        "description": "Enterprise CBSE Class X AI companion ΓÇö NCERT 2026-27 verified, 5 narrative engines, streaks, offline PWA",
  +        "start_url": "/",
  +        "display": "standalone",
--         "background_color": "#f0f2f5",
--         "theme_color": "#1a1a2e",
+++        "background_color": "#FFFDF7",
+++        "theme_color": "#FF9933",
  +        "orientation": "any",
+++        "icons": [{"src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>\U0001f4da</text></svg>", "sizes": "192x192", "type": "image/svg+xml"}],
+++        "categories": ["education"],
+++        "lang": "en-IN"
  +    }
  +    return JSONResponse(content=manifest)
  +
+++# ΓöÇΓöÇΓöÇ VidyaGyaan Enterprise APIs (additive, never breaks existing) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
+++# Observability init (LangSmith) ΓÇö import early so traces capture everything
+++try:
+++    import services.observability.langsmith_setup  # noqa: F401 ΓÇö init on import
+++except Exception:
+++    pass
+++
+++@app.get("/api/vg/health")
+++async def vg_health():
+++    try:
+++        db = get_db()
+++        enterprise_ok = True
+++        try:
+++            db.query_one("SELECT COUNT(*) as c FROM okf_entities")
+++        except Exception:
+++            enterprise_ok = False
+++        return {"status": "ok", "enterprise": enterprise_ok, "curriculum_guard": "v3", "narratives": ["theorem_analogy","detective_story","cinematic","family_drama","soul_music"], "okf": "v0.2", "gdt": "Google Document Tree"}
+++    except Exception as e:
+++        return {"status": "degraded", "error": str(e)[:300]}
+++
+++@app.post("/api/vg/guard/check")
+++async def vg_guard_check(request: Request):
+++    try:
+++        body = await request.json()
+++        text = body.get("text","")
+++        subject = body.get("subject","")
+++        from services.curriculum_guard.guard_v3 import CurriculumGuardV3
+++        g = CurriculumGuardV3()
+++        passed, reason, aligned = g.check(text, subject)
+++        return {"passed": passed, "reason": reason, "aligned_node": aligned}
+++    except Exception as e:
+++        raise HTTPException(status_code=400, detail=str(e))
+++
+++@app.post("/api/vg/narrative")
+++async def vg_narrative(request: Request):
+++    try:
+++        body = await request.json()
+++        title = body.get("title","CBSE Topic")
+++        content = body.get("content","")
+++        subject = body.get("subject","MA")
+++        mode = body.get("mode","board")
+++        from agents.orchestrator import orchestrator
+++        st = {"messages": [{"content": content}], "subject": subject, "intent": "concept" if mode=="board" else "solve", "attempt": 0}
+++        # Use orchestrator for full flow, or direct engine
+++        if not content:
+++            content = title
+++        # Direct engine path for speed
+++        from agents.orchestrator import infer_engine, ENGINE_MAP
+++        key = infer_engine(subject, content)
+++        engine = ENGINE_MAP.get(key)
+++        result = engine.render(title, content, mode=mode)
+++        # Guard enforce
+++        from services.curriculum_guard.guard_v3 import CurriculumGuardV3
+++        g = CurriculumGuardV3()
+++        html = g.enforce_three_tier(result["html"])
+++        return {"html": html, "visualizations": result["visualizations"], "engine": key, "subject": subject}
+++    except Exception as e:
+++        raise HTTPException(status_code=400, detail=str(e))
+++
+++@app.get("/api/vg/okf/{graph_id}")
+++async def vg_okf(graph_id: str):
+++    try:
+++        from services.graph_engineering.okf_schema import load_graph
+++        g = load_graph(graph_id)
+++        if not g:
+++            return {"error": "graph not found", "graph_id": graph_id}
+++        return g.to_jsonld()
+++    except Exception as e:
+++        return {"error": str(e)[:400]}
+++
+++@app.get("/api/vg/enterpriseschema")
+++async def vg_schema():
+++    try:
+++        db = get_db()
+++        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'okf_%' OR name IN ('students','theorems','experiments','history_scenes','social_episodes','streaks','daily_quests')").fetchall()] if hasattr(db.execute, '__call__') else []
+++        # fallback count
+++        counts = {}
+++        for t in ["okf_entities","okf_relations","students","theorems","experiments","history_scenes","social_episodes","streaks","daily_quests"]:
+++            try:
+++                row = db.query_one(f"SELECT COUNT(*) as c FROM {t}")
+++                counts[t] = row["c"] if row else 0
+++            except Exception:
+++                counts[t] = "missing"
+++        return {"tables": counts, "spec": "VidyaGyaan AY 2026-27"}
+++    except Exception as e:
+++        return {"error": str(e)[:400]}
+++
  +
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +# PAGE ROUTES
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +
  +@app.get("/", response_class=HTMLResponse)
  +async def home():
  +    idx = get_index()
  +    board_tree = idx.get_all_boards_tree()
  +    languages = idx.get_languages()
  +    classes = idx.get_classes()
  +
  +    board_options = ""
  +    for b in board_tree:
  +        board_options += f'<option value="{b["id"]}">{b["name"]}</option>\n'
  +
  +    lang_options = ""
  +    for l in languages:
  +        sel = ' selected' if l == 'English' else ''
  +        lang_options += f'<option value="{l}"{sel}>{l}</option>\n'
  +
  +    class_options = ""
  +    for c in classes:
  +        sel = ' selected' if c == 'X' else ''
  +        class_options += f'<option value="{c}"{sel}>Class {c}</option>\n'
  +
  +    tables = ""
  +    for b in board_tree:
  +        rows = ""
  +        for s in b.get("subjects", []):
  +            subj_url = f"/board/{b['id']}/{s['id']}"
  +            lang = s.get("language", "English")
  +            cls = s.get("class", "X")
  +            rows += f"""<tr data-subject="{s['id']}" data-board="{b['id']}" data-lang="{lang}" data-class="{cls}">
  +                <td><a href="{subj_url}">{s['name']}</a></td>
  +                <td>{lang}</td>
  +                <td>{cls}</td>
  +                <td>{s.get('chapter_count', 0)}</td>
  +                <td>{s.get('topic_count', 0)}</td>
  +                <td><a href="{subj_url}" class="tts-btn" style="padding:0.3rem 0.8rem;font-size:0.78rem;">Browse</a></td>
  +            </tr>"""
  +        if not rows:
  +            continue
  +        tables += f"""<div class="section board-table" data-board="{b['id']}">
  +            <h2>≡ƒôÿ {b['name']}</h2>
  +            <div style="overflow-x:auto;">
  +            <table class="data-table">
  +                <thead><tr><th>Subject</th><th>Language</th><th>Class</th><th>Chapters</th><th>Topics</th><th></th></tr></thead>
  +                <tbody>{rows}</tbody>
  +            </table>
  +            </div>
  +        </div>"""
  +
  +    medium_opts = '<option value="">All Mediums</option><option value="English">English</option><option value="Hindi">αñ╣αñ┐αñ¿αÑìαñªαÑÇ (Hindi)</option><option value="Telugu">α░ñα▒åα░▓α▒üα░ùα▒ü (Telugu)</option><option value="Tamil">α«ñα««α«┐α«┤α»ì (Tamil)</option><option value="Kannada">α▓òα▓¿α│ìα▓¿α▓í (Kannada)</option><option value="Bengali">αª¼αª╛αªéαª▓αª╛ (Bengali)</option><option value="Marathi">αñ«αñ░αñ╛αñáαÑÇ (Marathi)</option><option value="Gujarati">α¬ùα½üα¬£α¬░α¬╛α¬ñα½Ç (Gujarati)</option><option value="Malayalam">α┤«α┤▓α┤»α┤╛α┤│α┤é (Malayalam)</option><option value="Odia">α¼ôα¼íα¼╝α¼┐α¼å (Odia)</option><option value="Punjabi">α¿¬α⌐░α¿£α¿╛α¿¼α⌐Ç (Punjabi)</option><option value="Assamese">αªàαª╕αª«αºÇαª»αª╝αª╛ (Assamese)</option><option value="Urdu">╪º╪▒╪»┘ê (Urdu)</option>'
  +    subject_opts = '<option value="">All Subjects</option>'
  +    seen_subjects = set()
  +    for b in board_tree:
  +        for s in b.get("subjects", []):
  +            sid = s['id']
  +            if sid not in seen_subjects:
  +                seen_subjects.add(sid)
  +                subject_opts += f'<option value="{sid}">{s["name"]}</option>\n'
  +    filter_panel = f"""<div class="filter-panel" style="display:flex;gap:0.8rem;flex-wrap:wrap;align-items:flex-end;margin-bottom:1.25rem;padding:1rem 1.25rem;background:var(--card-bg);border-radius:12px;border:1px solid var(--border);">
  +        <div><label for="fb" style="display:block;font-size:0.78rem;font-weight:600;color:var(--text-muted);margin-bottom:0.25rem;">Board</label>
  +        <select id="fb" onchange="filterHome()" style="padding:0.45rem 0.7rem;border:1px solid var(--border);border-radius:6px;font-size:0.82rem;"><option value="">All Boards</option>{board_options}</select></div>
  +        <div><label for="fm" style="display:block;font-size:0.78rem;font-weight:600;color:var(--text-muted);margin-bottom:0.25rem;">Medium</label>
  +        <select id="fm" onchange="filterHome()" style="padding:0.45rem 0.7rem;border:1px solid var(--border);border-radius:6px;font-size:0.82rem;">{medium_opts}</select></div>
  +        <div><label for="fc" style="display:block;font-size:0.78rem;font-weight:600;color:var(--text-muted);margin-bottom:0.25rem;">Class</label>
  +        <select id="fc" onchange="filterHome()" style="padding:0.45rem 0.7rem;border:1px solid var(--border);border-radius:6px;font-size:0.82rem;"><option value="">All Classes</option>{class_options}</select></div>
  +        <div><label for="fs" style="display:block;font-size:0.78rem;font-weight:600;color:var(--text-muted);margin-bottom:0.25rem;">Subject</label>
  +        <select id="fs" onchange="filterHome()" style="padding:0.45rem 0.7rem;border:1px solid var(--border);border-radius:6px;font-size:0.82rem;">{subject_opts}</select></div>
  +        <div><button onclick="clearFilters()" style="padding:0.45rem 0.9rem;background:var(--accent);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.82rem;font-weight:600;">Apply</button>
  +        <button onclick="resetFilters()" style="padding:0.45rem 0.9rem;background:var(--bg);border:1px solid var(--border);border-radius:6px;cursor:pointer;font-size:0.82rem;">Reset</button></div>
  +        <div style="font-size:0.78rem;color:var(--text-muted);padding:0.25rem 0;"><span id="filter-count">loading...</span></div>
  +    </div>
  +    <script>
  +    function filterHome() {{
  +        var bv = document.getElementById('fb').value;
  +        var mv = document.getElementById('fm').value;
  +        var cv = document.getElementById('fc').value;
  +        var sv = document.getElementById('fs').value;
  +        document.querySelectorAll('.board-table').forEach(function(t) {{
  +            var visibleRows = 0;
  +            t.querySelectorAll('tbody tr').forEach(function(r) {{
  +                var show = (!bv || r.dataset.board === bv) && (!mv || r.dataset.lang === mv) && (!cv || r.dataset.class === cv) && (!sv || r.dataset.subject === sv);
  +                r.style.display = show ? '' : 'none';
  +                if (show) visibleRows++;
  +            }});
  +            t.style.display = visibleRows > 0 ? 'block' : 'none';
  +        }});
  +        // Update visible count
  +        var total = 0, vis = 0;
  +        document.querySelectorAll('tbody tr').forEach(function(r) {{ total++; if(r.style.display!=='none') vis++; }});
  +        var el = document.getElementById('filter-count');
  +        if(el) el.textContent = vis + ' of ' + total + ' subjects';
  +    }}
  +    function clearFilters() {{ filterHome(); }}
  +    function resetFilters() {{
  +        document.getElementById('fb').value = '';
  +        document.getElementById('fm').value = '';
  +        document.getElementById('fc').value = '';
  +        document.getElementById('fs').value = '';
  +        filterHome();
  +    }}
  +    window.addEventListener('DOMContentLoaded', filterHome);
  +    </script>"""
  +
  +    pomelli_hero = _pomelli_hero_svg()
  +    content = f"""<div class="section">{pomelli_hero}
  +<h2>≡ƒôÜ AI Study Companion</h2>
  +<p style="color:#666;margin-bottom:1rem;">Multiple boards ┬╖ Indian languages ┬╖ Class VΓÇôXII ┬╖ AI-powered learning</p>
  +<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1rem;">
  +<a href="/search" class="tts-btn">≡ƒöì Search Topics</a>
  +<a href="/exams" class="tts-btn">≡ƒÅå Mock Exams</a>
  +<a href="/profile" class="tts-btn">≡ƒæñ Profile</a>
  +<a href="/ai" class="tts-btn">≡ƒñû AI Studio</a>
  +</div></div>{filter_panel}
  +<div id="home-tables">{tables}</div>"""
  +    return HTMLResponse(_render(title="AI Study Companion - Home", content=content))
  +
  +
  +@app.get("/search", response_class=HTMLResponse)
  +async def search_page(request: Request):
  +    q = request.query_params.get("q", "")
  +    board = request.query_params.get("board", "")
  +    subject = request.query_params.get("subject", "")
  +
  +    idx = get_index()
  +    board_tree = idx.get_all_boards_tree()
  +
  +    board_opts = '<option value="">All Boards</option>'
  +    subj_opts = '<option value="">All Subjects</option>'
  +    for b in board_tree:
  +        sel = ' selected' if b['id'] == board else ''
  +        board_opts += f'<option value="{b["id"]}"{sel}>{b["name"]}</option>'
  +        for s in b.get("subjects", []):
  +            sel2 = ' selected' if s['id'] == subject else ''
  +            subj_opts += f'<option value="{s["id"]}" data-board="{b["id"]}"{sel2}>{s["name"]}</option>'
  +
  +    results_html = ""
  +    if q:
  +        try:
  +            results = idx.search(q, board=board if board else None, subject=subject if subject else None, limit=20)
  +        except Exception:
  +            results = []
  +        if results:
  +            results_html = '<div style="overflow-x:auto;"><table class="data-table"><thead><tr><th>Topic</th><th>Chapter</th><th>Score</th><th></th></tr></thead><tbody>'
  +            for r in results:
  +                topic_url = f"/topic/{r.get('id','')}"
  +                results_html += f"""<tr>
--                     <td><a href="{topic_url}">{htmlmod.escape(r.get('title',''))}</a></td>
--                     <td style="color:var(--text-muted);font-size:0.85rem;">{htmlmod.escape(r.get('chapter_title',''))}</td>
+++                    <td><a href="{topic_url}">{htmlmod.escape(r.get('title') or '')}</a></td>
+++                    <td style="color:var(--text-muted);font-size:0.85rem;">{htmlmod.escape(r.get('chapter_title') or '')}</td>
  +                    <td style="color:var(--text-muted);font-size:0.8rem;">{r.get('score', 0)}</td>
  +                    <td><a href="{topic_url}" class="tts-btn" style="padding:0.2rem 0.6rem;font-size:0.75rem;">Open</a></td>
  +                </tr>"""
  +            results_html += '</tbody></table></div>'
  +        else:
  +            results_html = '<p style="padding:1rem;color:#666;">No results found. Try different keywords or filters.</p>'
  +    else:
  +        results_html = '<p style="padding:1rem;color:#666;">Enter a search term above to find topics across all boards.</p>'
  +
  +    content = f"""<div class="breadcrumb">{_build_breadcrumb([("Home", "/"), ("Search", None)])}</div>
  +<div class="section">
  +<h2>≡ƒöì Search Topics</h2>
  +<form method="get" action="/search" class="search-form">
  +    <input type="text" name="q" value="{htmlmod.escape(q)}" placeholder="Search topics, formulas, concepts..." style="flex:1;min-width:200px;padding:0.7rem;border:2px solid var(--border);border-radius:8px;font-size:0.9rem;">
  +    <select name="board" id="search-board">
  +        {board_opts}
  +    </select>
  +    <select name="subject" id="search-subject">
  +        {subj_opts}
  +    </select>
  +    <button type="submit" class="tts-btn">Search</button>
  +</form>
  +</div>
  +<div class="section">
  +{results_html}
  +</div>"""
  +    return HTMLResponse(_render(title=f"Search: {q}" if q else "Search - AI Study Companion", content=content))
  +
  +
  +@app.get("/tutor", response_class=HTMLResponse)
  +async def tutor_hub():
  +    conn = DB
  +    rows = ""
  +    if conn.table_exists("subjects"):
  +        subjects = conn.query(
  +            "SELECT DISTINCT s.id, s.name, s.board_id FROM subjects s "
  +            "JOIN chapters c ON c.subject_id = s.id "
  +            "JOIN topics t ON t.chapter_id = c.id "
  +            "WHERE t.id IS NOT NULL "
  +            "ORDER BY s.board_id, s.name"
  +        )
  +        subject_ids = [s["id"] for s in subjects]
  +        all_chapters = {}
  +        if subject_ids:
  +            placeholders = ",".join(["?"] * len(subject_ids))
  +            rows_data = conn.query(
  +                f"SELECT c.id, c.num, c.title, c.subject_id FROM chapters c "
  +                f"JOIN topics t ON t.chapter_id = c.id "
  +                f"WHERE c.subject_id IN ({placeholders}) GROUP BY c.id ORDER BY c.num",
  +                subject_ids
  +            )
  +            for r in rows_data:
  +                all_chapters.setdefault(r["subject_id"], []).append(r)
  +        for s in subjects:
  +            chapters = all_chapters.get(s["id"], [])
  +            ch_links = "".join(f'<li><a href="/chapter/{ch["id"]}">Ch {ch["num"]}: {ch["title"]}</a></li>' for ch in chapters)
  +            if ch_links:
  +                rows += f'<div class="book-section"><h3>{s["name"]}</h3><ul style="columns:2;column-gap:2rem;padding-left:1.2rem;">{ch_links}</ul></div>'
  +    if not rows:
  +        rows = '<p style="text-align:center;padding:2rem;color:#666;">No topics available yet.</p>'
  +    content = f"""<div class="breadcrumb">{_build_breadcrumb([("Home", "/"), ("AI Tutor Hub", None)])}</div>
  +<div class="section"><h2>≡ƒºá AI Tutor Hub</h2><p>Select a chapter to start a question-based learning session.</p>{rows}</div>"""
  +    return HTMLResponse(_render(title="AI Tutor Hub - AI Study Companion", content=content))
  +
  +
  +@app.get("/tutor/{topic_id}", response_class=HTMLResponse)
  +async def tutor_page(topic_id: str):
  +    conn = DB
  +    topic = conn.query_one("SELECT * FROM topics WHERE id = ?", (topic_id,))
  +    if not topic:
  +        return HTMLResponse(
  +            _render(title="Topic Not Found", content='<div class="section"><h2>Topic Not Found</h2><p><a href="/">Go Home</a></p></div>'),
  +            status_code=404
  +        )
  +    chapter = conn.query_one("SELECT * FROM chapters WHERE id = ?", (topic["chapter_id"],))
  +    chunks = conn.query("SELECT * FROM chunks WHERE topic_id = ? ORDER BY seq", (topic_id,))
  +    questions = ai_tutor.generate_questions(topic["title"], topic.get("content", ""), chunks, 3)
  +    session_id = ai_tutor.create_tutor_session(topic_id)
  +
  +    questions_json = json.dumps(questions)
  +    starter_prompt = random.choice(ai_tutor.STARTER_PROMPTS) if hasattr(ai_tutor, "STARTER_PROMPTS") else "Let's learn!"
  +
  +    content = f"""<div class="breadcrumb">{_build_breadcrumb([
  +        ("Home", "/"),
  +        (chapter.get("board_id", "").upper(), f"/board/{chapter['board_id']}"),
  +        (f"Ch {chapter['num']}: {chapter['title']}", f"/chapter/{chapter['id']}"),
  +        (topic["title"], f"/topic/{topic_id}"),
  +        ("AI Tutor", None)
  +    ])}</div>
  +<div class="section" id="tutor-section">
  +<h2>≡ƒºá AI Tutor: {topic['title']}</h2>
  +<p style="color:#666;margin-bottom:1rem;">Question-Based Learning</p>
  +<div id="tutor-progress" style="margin-bottom:1rem;font-size:0.85rem;color:var(--text-muted);">Question 1 of {len(questions)}</div>
  +<div id="tutor-content">
  +<div class="tutor-question-card">
  +<p class="tutor-prompt">{starter_prompt}</p>
  +<p class="tutor-question-text" id="tutor-question">{questions[0]["question"] if questions else "No questions available."}</p>
  +<textarea id="tutor-answer" class="tutor-input" rows="4" placeholder="Type your answer here..."></textarea>
  +<div style="display:flex;gap:0.5rem;margin-top:0.8rem;flex-wrap:wrap;">
  +<button class="tts-btn" onclick="submitTutorAnswer({session_id})">Submit Answer</button>
  +<button class="tts-btn" onclick="skipTutorQuestion({session_id})" style="opacity:0.7;">Skip</button>
  +</div></div>
  +<div id="tutor-feedback" style="display:none;"></div></div>
  +<div id="tutor-complete" style="display:none;"></div></div>
  +<script>
  +var tutorQuestions = {questions_json};
  +var tutorSessionId = {session_id};
  +var tutorQIndex = 0;
  +var topicId = '{topic_id}';
  +function submitTutorAnswer(sessionId){{
  +    var answer = document.getElementById('tutor-answer').value.trim();
  +    if(!answer){{ alert('Please write your answer first.'); return; }}
  +    var q = tutorQuestions[tutorQIndex];
  +    fetch('/api/tutor/answer',{{
  +        method:'POST', headers:{{'Content-Type':'application/x-www-form-urlencoded'}},
  +        body:'session_id='+sessionId+'&question='+encodeURIComponent(q.question)+'&qtype='+q.type+'&model_answer='+encodeURIComponent(q.model_answer)+'&student_answer='+encodeURIComponent(answer)
  +    }}).then(r=>r.json()).then(data=>{{
  +        var fb = document.getElementById('tutor-feedback');
  +        fb.style.display='block';
  +        fb.innerHTML='<div class="tutor-feedback-card"><h4 style="margin-top:0;">Your Answer</h4><p style="background:#f8f9ff;padding:0.8rem;border-radius:6px;">'+answer.replace(/</g,'&lt;')+'</p><h4>How did you do?</h4><div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-top:0.5rem;"><button class="tts-btn" style="background:#dcfce7;" onclick="selfAssess('+data.answer_id+',\\'correct\\','+sessionId+')">Γ£à Got it right</button><button class="tts-btn" style="background:#fef9c3;" onclick="selfAssess('+data.answer_id+',\\'partial\\','+sessionId+')">≡ƒƒí Partially correct</button><button class="tts-btn" style="background:#fee2e2;" onclick="selfAssess('+data.answer_id+',\\'wrong\\','+sessionId+')">Γ¥î Needs work</button></div></div>';
  +        document.getElementById('tutor-answer').disabled=true;
  +    }});
  +}}
  +function selfAssess(answerId,assessment,sessionId){{
  +    fetch('/api/tutor/remedial',{{
  +        method:'POST', headers:{{'Content-Type':'application/x-www-form-urlencoded'}},
  +        body:'answer_id='+answerId+'&self_assessment='+assessment+'&session_id='+sessionId
  +    }}).then(r=>r.json()).then(data=>{{
  +        var fb = document.getElementById('tutor-feedback');
  +        var q = tutorQuestions[tutorQIndex];
  +        var showModel = '<h4 style="margin-top:0.8rem;">Model Answer</h4><div class="tutor-model-answer"><p>'+q.model_answer+'</p></div>';
  +        if(assessment=='correct'){{ fb.innerHTML+='<p style="color:#16a34a;">Great job!</p>'+showModel; }}
  +        else {{ fb.innerHTML+=showModel+(data.remedial_html||''); }}
  +        document.getElementById('tutor-answer').value=''; document.getElementById('tutor-answer').disabled=false;
  +        tutorQIndex++;
  +        if(tutorQIndex<tutorQuestions.length){{
  +            document.getElementById('tutor-question').textContent=tutorQuestions[tutorQIndex].question;
  +            document.getElementById('tutor-progress').textContent='Question '+(tutorQIndex+1)+' of '+tutorQuestions.length;
  +        }}else{{
  +            fetch('/api/tutor/complete',{{
  +                method:'POST', headers:{{'Content-Type':'application/x-www-form-urlencoded'}},
  +                body:'session_id='+sessionId
  +            }}).then(r=>r.json()).then(d=>{{ document.getElementById('tutor-content').innerHTML='<div style="text-align:center;padding:2rem;"><h3>≡ƒÄë Session Complete!</h3><p>+'+d.xp+' XP</p><a class="tts-btn" href="/topic/'+topicId+'">Back to Topic</a></div>'; }});
  +        }}
  +    }});
  +}}
  +function skipTutorQuestion(sessionId){{
  +    if(confirm('Skip this question?')){{
  +        var q = tutorQuestions[tutorQIndex];
  +        fetch('/api/tutor/answer',{{
  +            method:'POST', headers:{{'Content-Type':'application/x-www-form-urlencoded'}},
  +            body:'session_id='+sessionId+'&question='+encodeURIComponent(q.question)+'&qtype='+q.type+'&model_answer='+encodeURIComponent(q.model_answer)+'&student_answer=[skipped]'
  +        }}).then(function(){{
  +            tutorQIndex++;
  +            if(tutorQIndex<tutorQuestions.length){{
  +                document.getElementById('tutor-question').textContent=tutorQuestions[tutorQIndex].question;
  +                document.getElementById('tutor-progress').textContent='Question '+(tutorQIndex+1)+' of '+tutorQuestions.length;
  +            }}else{{
  +                fetch('/api/tutor/complete',{{
  +                    method:'POST', headers:{{'Content-Type':'application/x-www-form-urlencoded'}},
  +                    body:'session_id='+sessionId
  +                }}).then(r=>r.json()).then(d=>{{ document.getElementById('tutor-content').innerHTML='<div style="text-align:center;padding:2rem;"><h3>≡ƒÄë Session Complete!</h3><p>+'+d.xp+' XP</p><a class="tts-btn" href="/topic/'+topicId+'">Back to Topic</a></div>'; }}));
  +            }}
  +        }});
  +    }}
  +}}
  +</script>"""
  +    return HTMLResponse(_render(title=f"AI Tutor: {topic['title']}", content=content))
  +
  +
  +@app.get("/board/{board_id}", response_class=HTMLResponse)
  +async def board_page(board_id: str):
  +    conn = DB
  +    board_id = board_id.lower()
  +    subjects = conn.query("SELECT id, name, board_id FROM subjects WHERE LOWER(board_id) = ? ORDER BY name", (board_id,))
  +    if not subjects:
  +        return HTMLResponse(
  +            _render(title="Board Not Found", content=f'<div class="section"><h2>Board Not Found</h2><p>No board found for "{board_id}". <a href="/">Go Home</a></p></div>'),
  +            status_code=404
  +        )
  +    rows = ""
  +    for s in subjects:
  +        chs = _get_chapters(conn, s["id"])
  +        ch_links = "".join(f'<a href="/chapter/{ch["id"]}" class="chunk-view"><div class="chunk-title">Ch {ch["num"]}: {ch["title"]}</div></a>' for ch in chs)
  +        rows += f'<div class="book-section"><h3><a href="/board/{board_id}/{s["id"]}" style="color:var(--primary);">{s["name"]}</a></h3><div style="margin-bottom:0.8rem;">{ch_links}</div></div>'
  +    content = f"""<div class="breadcrumb">{_build_breadcrumb([("Home", "/"), (board_id.upper(), None)])}</div>
  +<div class="section"><h2>≡ƒôÿ {board_id.upper()} Board</h2><p style="color:#666;margin-bottom:1rem;">Select a subject to begin learning.</p>{rows}</div>"""
  +    return HTMLResponse(_render(title=f"{board_id.upper()} Board - AI Study Companion", content=content))
  +
  +
  +@app.get("/board/{board_id}/{subject_slug}", response_class=HTMLResponse)
  +async def subject_page(board_id: str, subject_slug: str):
  +    conn = DB
  +    board_id = board_id.lower()
  +    subject_name = subject_slug.replace("-", " ").title()
  +    # First attempt exact match on ID or exact lowercase name to avoid overlapping matches
  +    subjects = conn.query(
  +        "SELECT id, name, board_id FROM subjects WHERE LOWER(board_id) = ? AND (LOWER(id) = ? OR LOWER(name) = ?)",
  +        (board_id, subject_slug.lower(), subject_slug.replace("-", " ").lower())
  +    )
  +    if not subjects:
  +        subjects = conn.query(
  +            "SELECT id, name, board_id FROM subjects WHERE LOWER(board_id) = ? AND LOWER(name) LIKE ? ORDER BY name",
  +            (board_id, f"%{subject_name.lower()}%")
  +        )
  +    if not subjects:
  +        subjects = conn.query(
  +            "SELECT id, name, board_id FROM subjects WHERE LOWER(board_id) = ? ORDER BY name",
  +            (board_id,)
  +        )
  +        if not subjects:
  +            return HTMLResponse(
  +                _render(title="Not Found", content='<div class="section"><h2>Not Found</h2><p><a href="/">Go Home</a></p></div>'),
  +                status_code=404
  +            )
  +    rows = ""
  +    for s in subjects:
  +        chs = _get_chapters(conn, s["id"])
  +        ch_links = "".join(f'<a href="/chapter/{ch["id"]}" class="chapter-card-premium"><span class="chapter-badge">Chapter {ch["num"]}</span><h3 class="chapter-title">{ch["title"]}</h3><span class="start-learning-btn">Start Learning &rarr;</span></a>' for ch in chs)
  +        rows += f'<h3 style="margin:2rem 0 1rem;color:var(--primary);font-weight:800;font-size:1.3rem;">{s["name"]}</h3><div class="chapters-grid">{ch_links}</div>'
  +    content = f"""<div class="breadcrumb">{_build_breadcrumb([("Home", "/"), (board_id.upper(), f"/board/{board_id}"), (subject_name, None)])}</div>
  +<div class="subject-header-card">
  +    <div class="subject-badge">{board_id.upper()} Board</div>
  +    <h2>{subject_name} Syllabus</h2>
  +    <p>Explore chapters, topics, formulas, solved examples, and experiments.</p>
  +</div>
  +{rows}"""
  +    return HTMLResponse(_render(title=f"{board_id.upper()} - {subject_name} - AI Study Companion", content=content))
  +
  +
  +@app.get("/board/{board_id}/subject/{subject_slug}", response_class=HTMLResponse)
  +async def subject_page_compat(board_id: str, subject_slug: str):
  +    return await subject_page(board_id, subject_slug)
  +
  +
  +@app.get("/chapter/{chapter_id}", response_class=HTMLResponse)
  +async def chapter_page(chapter_id: str):
  +    conn = DB
  +    chapter = conn.query_one("SELECT * FROM chapters WHERE id = ?", (chapter_id,))
  +    if not chapter:
  +        return HTMLResponse(
  +            _render(title="Chapter Not Found", content='<div class="section"><h2>Chapter Not Found</h2><p><a href="/">Go Home</a></p></div>'),
  +            status_code=404
  +        )
  +    subject = conn.query_one("SELECT * FROM subjects WHERE id = ?", (chapter["subject_id"],))
  +    topics = _get_topics(conn, chapter_id)
  +
  +    # Batch-load all chunks for all topics in one query
  +    topic_ids = [t["id"] for t in topics]
  +    chunks_by_topic = {}
  +    if topic_ids:
  +        placeholders = ",".join(["?"] * len(topic_ids))
  +        all_chunks = conn.query(
  +            f"SELECT * FROM chunks WHERE topic_id IN ({placeholders}) ORDER BY seq",
  +            topic_ids
  +        )
  +        for c in all_chunks:
  +            chunks_by_topic.setdefault(c["topic_id"], []).append(c)
  +
  +    topics_html = ""
  +    is_math = subject and ("math" in subject.get("id", "").lower() or "math" in subject.get("name", "").lower())
  +    is_science = subject and ("science" in subject.get("id", "").lower() or "science" in subject.get("name", "").lower())
  +    is_social = subject and any(x in subject.get("id", "").lower() or x in subject.get("name", "").lower() for x in ["social", "history", "geography", "civics", "political", "economics", "democrat"])
  +
  +    for t in topics:
  +        chunks = chunks_by_topic.get(t["id"], [])
  +        if is_math:
  +            content_html = format_math_content(t.get("content", ""))
  +            chunks_html = "".join(f'<div class="chunk-view"><div class="chunk-title">{htmlmod.escape(c.get("title",""))}</div><div class="chunk-content">{format_math_content(c.get("content",""))}</div></div>' for c in chunks)
  +        elif is_science:
  +            content_html = format_science_content(t.get("content", ""))
  +            chunks_html = "".join(f'<div class="chunk-view"><div class="chunk-title">{htmlmod.escape(c.get("title",""))}</div><div class="chunk-content">{format_science_content(c.get("content",""))}</div></div>' for c in chunks)
  +        elif is_social:
  +            content_html = format_social_content(t.get("content", ""))
  +            chunks_html = "".join(f'<div class="chunk-view"><div class="chunk-title">{htmlmod.escape(c.get("title",""))}</div><div class="chunk-content">{format_social_content(c.get("content",""))}</div></div>' for c in chunks)
  +        else:
  +            content_html = format_general_content(t.get("content", ""))
  +            chunks_html = "".join(f'<div class="chunk-view"><div class="chunk-title">{htmlmod.escape(c.get("title",""))}</div><div class="chunk-content">{format_general_content(c.get("content",""))}</div></div>' for c in chunks)
  +
  +        topics_html += f"""<div class="section" id="topic-{t['id']}">
  +<h2><a href="/topic/{t['id']}" style="color:var(--primary);">{htmlmod.escape(t['title'])}</a></h2>
  +{content_html or chunks_html}
  +<div class="chapter-actions">
  +<a href="/topic/{t['id']}" class="tts-btn" style="font-size:0.8rem;">≡ƒôû Study</a>
  +<a href="/tutor/{t['id']}" class="tts-btn" style="font-size:0.8rem;">≡ƒºá AI Tutor</a>
  +<a href="/quiz/{chapter_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒô¥ Quiz</a>
  +<a href="/interactives/matching/{t['id']}" class="tts-btn" style="font-size:0.8rem;">≡ƒöä Matching</a>
  +</div></div>"""
  +
  +
  +    subj_name = subject["name"] if subject else ""
  +    board_id = (subject["board_id"] if subject else "").upper()
  +    content = f"""<div class="breadcrumb">{_build_breadcrumb([
  +        ("Home", "/"),
  +        (board_id, f"/board/{subject['board_id'].lower() if subject else ''}"),
  +        (subj_name, None),
  +        (f"Ch {chapter['num']}: {chapter['title']}", None)
  +    ])}</div>
  +<div class="section">
  +<h2>≡ƒôû Ch {chapter['num']}: {chapter['title']}</h2>
  +<p style="color:#666;margin-bottom:1rem;">{subject["name"] if subject else ""}</p>
  +<div class="chapter-actions">
  +<a href="/notes/{chapter_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒô¥ Notes</a>
  +<a href="/revision/{chapter_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒöä Revision</a>
  +<a href="/quiz/{chapter_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒô¥ Quiz</a>
  +</div>
  +</div>{topics_html}"""
  +    return HTMLResponse(_render(title=f"Ch {chapter['num']}: {chapter['title']} - AI Study Companion", content=content))
  +
  +
  +def format_math_content(text):
  +    if not text:
  +        return ""
  +    html = format_content(text)
  +    
  +    # 1. Theorem Cards
  +    html = re.sub(
  +        r'(<p>)?<strong>(Theorem|Lemma)\b([^:]*):?</strong>(.*?)(</p>)?',
  +        r'<div class="theorem-card"><div class="theorem-title">≡ƒôÉ \2\3</div><div class="theorem-body">\4</div></div>',
  +        html,
  +        flags=re.DOTALL | re.IGNORECASE
  +    )
  +    
  +    # 2. Key Tips/Memory Aids Cards
  +    html = re.sub(
  +        r'(<p>)?<strong>(Key points to remember|Memory aid|Board Exam Tip|Tip)\b([^:]*):?</strong>(.*?)(</p>)?',
  +        r'<div class="concept-tip-card"><div class="concept-tip-title">≡ƒÆí \2\3</div><div>\4</div></div>',
  +        html,
  +        flags=re.DOTALL | re.IGNORECASE
  +    )
  +    
  +    # 3. Tables enhancement
  +    html = re.sub(
  +        r'<table>(.*?)</table>',
  +        r'<div class="formula-card" style="overflow-x:auto;"><table style="width:100%; border-collapse: collapse;">\1</table></div>',
  +        html,
  +        flags=re.DOTALL
  +    )
  +    return html
  +
  +
  +def build_math_cheat_sheet(content, chunks):
  +    formulas = []
  +    all_text = (content or "") + "\n" + "\n".join(c.get("content", "") for c in chunks)
  +    equations = re.findall(r'\$\$(.*?)\$\$', all_text, re.DOTALL)
  +    for eq in equations:
  +        eq_clean = eq.strip()
  +        if eq_clean and eq_clean not in formulas:
  +            formulas.append(eq_clean)
  +            
  +    lines = all_text.split("\n")
  +    for line in lines:
  +        if "=" in line and any(x in line.lower() for x in ["sin", "cos", "tan", "sec", "cosec", "cot", "log", "hcf", "lcm", "area", "volume", "perimeter", "mean", "mode", "median", "probability", "d_i", "f_i", "x_i", "u_i", "a_i", "r^2", "pi", "a = bq"]):
  +            line_clean = line.strip("ΓÇó-* ").strip()
  +            if line_clean and len(line_clean) < 150 and line_clean not in [f if isinstance(f, str) else f[0] for f in formulas]:
  +                formulas.append((line_clean, True))
  +                
  +    if not formulas:
  +        return f'<div class="concept-tip-card"><div class="concept-tip-title">ΓÜí Formula Sheet</div><p>Refer to the Concept Explainer tab for key equations.</p></div>'
  +        
  +    html = '<div class="section"><h3>ΓÜí Key Formulas & Reference Sheet</h3><p style="color:#666;margin-bottom:1.5rem;">Quick reference formulas and relationships for this topic.</p>'
  +    for idx, item in enumerate(formulas):
  +        is_plain = False
  +        if isinstance(item, tuple):
  +            formula, is_plain = item
  +        else:
  +            formula = item
  +            
  +        if is_plain:
  +            formatted_eq = f'<div style="text-align:center; font-size:1.1rem; font-weight:600; margin:1rem 0; color:var(--accent2);">{formula}</div>'
  +        else:
  +            if '=' in formula and '\\' not in formula and '$$' not in formula:
  +                formatted_eq = f'<div style="text-align:center; font-size:1.1rem; font-weight:600; margin:1rem 0; color:var(--accent2);">$${formula}$$</div>'
  +            else:
  +                formatted_eq = f'<div style="text-align:center; font-size:1.1rem; font-weight:600; margin:1rem 0; color:var(--accent2);">$${formula.replace("$$", "")}$$</div>'
  +        html += f"""<div class="formula-card" style="margin-bottom: 1rem;">
  +            <div style="font-weight:700; font-size:0.85rem; color:var(--text-muted); text-transform:uppercase; margin-bottom:0.5rem;">Formula {idx+1}</div>
  +            {formatted_eq}
  +        </div>"""
  +    html += '</div>'
  +    return html
  +
  +
  +def format_solved_problem(p, idx):
  +    qtext = format_math_content(p.get("problem_text", ""))
  +    stext = p.get("solution_text", "")
  +    
  +    step_matches = re.split(r'(?:^|\n)(?:Step\s*\d+\s*:|Step\s*\d+\b|\d+\.\s+)', stext)
  +    steps_html = ""
  +    step_num = 1
  +    for part in step_matches:
  +        part_clean = part.strip()
  +        if not part_clean:
  +            continue
  +        step_formatted = format_math_content(part_clean)
  +        steps_html += f"""
  +        <div class="step-container">
  +            <span class="step-badge">{step_num}</span>
  +            <div class="step-content">{step_formatted}</div>
  +        </div>
  +        """
  +        step_num += 1
  +        
  +    if not steps_html:
  +        steps_html = format_math_content(stext)
  +        
  +    return f"""
  +    <div class="solved-problem-card">
  +        <div class="solved-problem-header" onclick="this.classList.toggle('open'); this.nextElementSibling.classList.toggle('open'); var sign = this.querySelector('.sign'); if (sign) sign.textContent = this.classList.contains('open') ? 'ΓêÆ' : '+';">
  +            <span>Γ¥ô Question {idx}: {htmlmod.escape(p.get('problem_text', '')[:300])}...</span>
  +            <span class="sign" style="font-size:1.2rem; color:var(--accent); font-weight:bold;">+</span>
  +        </div>
  +        <div class="solved-problem-body">
  +            <div class="problem-box" style="margin-top:0;">
  +                <div class="problem-header">Problem Statement</div>
  +                <div class="problem-text">{qtext}</div>
  +            </div>
  +            <div class="solution-steps">
  +                <div class="problem-header" style="color:var(--success); border-bottom-color:rgba(16,185,129,0.1);">Step-by-step Solution</div>
  +                {steps_html}
  +            </div>
  +            <div class="concept-tip-card" style="margin-top: 1rem; margin-bottom: 0;">
  +                <div class="concept-tip-title">≡ƒ¢í∩╕Å Exam Tip</div>
  +                <p>Write down every calculation step and cite the underlying theorem (e.g. Euclid's Division Lemma) to earn full step-marks in exams.</p>
  +            </div>
  +        </div>
  +    </div>
  +    """
  +
  +
  +
  +def format_science_content(text):
  +    if not text:
  +        return ""
  +    html = format_content(text)
  +    
  +    # 1. Chemical states formatting
  +    html = re.sub(
  +        r'\(([slg]|aq)\)',
  +        r'<span class="reaction-state-badge">(\1)</span>',
  +        html
  +    )
  +    
  +    # 2. Activity / Experiment boxes
  +    html = re.sub(
  +        r'(<p>)?<strong>(Activity\s*\d+\.\d+|Experiment\s*\d+\.\d+)\b([^:]*):?</strong>(.*?)(</p>)?',
  +        r'<div class="science-activity-card"><div class="activity-title">≡ƒº¬ \2\3</div><div class="activity-section-content">\4</div></div>',
  +        html,
  +        flags=re.DOTALL | re.IGNORECASE
  +    )
  +    
  +    # 3. Science tips and safety alerts
  +    html = re.sub(
  +        r'(<p>)?<strong>(Key points to remember|Safety Precautions|Observation|Inference|Conclusion|Tip)\b([^:]*):?</strong>(.*?)(</p>)?',
  +        r'<div class="concept-tip-card" style="border-left-color:#0d9488;"><div class="concept-tip-title" style="color:#0f766e;">≡ƒÆí \2\3</div><div>\4</div></div>',
  +        html,
  +        flags=re.DOTALL | re.IGNORECASE
  +    )
  +    return html
  +
  +
  +def build_science_experiment_lab(content, chunks):
  +    all_text = (content or "") + "\n" + "\n".join(c.get("content", "") for c in chunks)
  +    activities = re.findall(r'(Activity\s*\d+\.\d+|Experiment\s*\d+\.\d+)(.*?)(?=(?:Activity\s*\d+\.\d+|Experiment\s*\d+\.\d+)|$)', all_text, re.DOTALL | re.IGNORECASE)
  +    
  +    if not activities:
  +        return '<div class="concept-tip-card" style="border-left-color:#0d9488;"><div class="concept-tip-title" style="color:#0f766e;">≡ƒº¬ Experiment Lab</div><p>No laboratory activities or experiments are listed for this specific topic.</p></div>'
  +        
  +    html = '<div class="section"><h3>≡ƒº¬ Experiment & Practical Activity Lab</h3><p style="color:#666;margin-bottom:1.5rem;">Study the key practical activities from your textbook. Focus on procedures, observations, and chemical equations.</p>'
  +    for title, body in activities:
  +        body_html = format_science_content(body)
  +        html += f"""
  +        <div class="science-activity-card">
  +            <div class="activity-title">≡ƒº¬ {title.strip()}</div>
  +            <div class="activity-section-content">{body_html}</div>
  +        </div>
  +        """
  +    html += '</div>'
  +    return html
  +
  +
  +def format_science_solved_problem(p, idx):
  +    qtext = format_science_content(p.get("problem_text", ""))
  +    stext = p.get("solution_text", "")
  +    
  +    step_matches = re.split(r'(?:^|\n)(?:Step\s*\d+\s*:|Step\s*\d+\b|\d+\.\s+)', stext)
  +    steps_html = ""
  +    step_num = 1
  +    for part in step_matches:
  +        part_clean = part.strip()
  +        if not part_clean:
  +            continue
  +        step_formatted = format_science_content(part_clean)
  +        steps_html += f"""
  +        <div class="step-container">
  +            <span class="step-badge" style="background:#0d9488;">{step_num}</span>
  +            <div class="step-content">{step_formatted}</div>
  +        </div>
  +        """
  +        step_num += 1
  +        
  +    if not steps_html:
  +        steps_html = format_science_content(stext)
  +        
  +    return f"""
  +    <div class="solved-problem-card" style="border-color:rgba(13,148,136,0.15);">
  +        <div class="solved-problem-header" style="background:#fafdfd;" onclick="this.classList.toggle('open'); this.nextElementSibling.classList.toggle('open'); var sign = this.querySelector('.sign'); if (sign) sign.textContent = this.classList.contains('open') ? 'ΓêÆ' : '+';">
  +            <span>Γ¥ô Question {idx}: {htmlmod.escape(p.get('problem_text', '')[:300])}...</span>
  +            <span class="sign" style="font-size:1.2rem; color:#0d9488; font-weight:bold;">+</span>
  +        </div>
  +        <div class="solved-problem-body">
  +            <div class="problem-box" style="margin-top:0; border-color:rgba(13,148,136,0.15); background:#fcfdfd;">
  +                <div class="problem-header" style="color:#0d9488; border-bottom-color:rgba(13,148,136,0.15);">Problem Statement</div>
  +                <div class="problem-text">{qtext}</div>
  +            </div>
  +            <div class="solution-steps" style="border-color:rgba(13,148,136,0.15); background:#fcfcfc;">
  +                <div class="problem-header" style="color:var(--success); border-bottom-color:rgba(16,185,129,0.1);">Step-by-step Solution</div>
  +                {steps_html}
  +            </div>
  +            <div class="concept-tip-card" style="margin-top: 1rem; margin-bottom: 0; border-left-color:#0d9488;">
  +                <div class="concept-tip-title" style="color:#0f766e;">≡ƒ¢í∩╕Å Exam Tip</div>
  +                <p>Include physical states of reactants and products (like s, l, g, aq) and mention details like the catalyst or heating symbol (╬ö) above the arrow to get full marks.</p>
  +            </div>
  +        </div>
  +    </div>
  +    """
  +
  +
  +
  +def format_social_content(text):
  +    if not text:
  +        return ""
  +    html = format_content(text)
  +    
  +    # 1. Key Historical Terms formatting
  +    html = re.sub(
  +        r'(<p>)?<strong>(Satyagraha|Rowlatt Act|Khilafat|Boycott|Purna Swaraj|Harijan|Civil Disobedience|Hartal|Nation-state|Alluri Sitarama Raju|Baba Ramchandra)\b([^:]*):?</strong>(.*?)(</p>)?',
  +        r'<div class="social-term-card"><div class="term-title">≡ƒÅ╖∩╕Å <span class="term-badge">\2\3</span></div><div>\4</div></div>',
  +        html,
  +        flags=re.DOTALL | re.IGNORECASE
  +    )
  +    
  +    # 2. Tips & Chronology alerts
  +    html = re.sub(
  +        r'(<p>)?<strong>(Key points to remember|Chronology|Map work|Board Exam Tip|Tip)\b([^:]*):?</strong>(.*?)(</p>)?',
  +        r'<div class="concept-tip-card" style="border-left-color:#d97706;"><div class="concept-tip-title" style="color:#92400e;">≡ƒÆí \2\3</div><div>\4</div></div>',
  +        html,
  +        flags=re.DOTALL | re.IGNORECASE
  +    )
  +    return html
  +
  +
  +def build_social_timeline(content, chunks):
  +    all_text = (content or "") + "\n" + "\n".join(c.get("content", "") for c in chunks)
  +    events = []
  +    lines = all_text.split("\n")
  +    for line in lines:
  +        match = re.search(r'\b(1[789]\d{2}|20\d{2})\b', line)
  +        if match:
  +            year = match.group(1)
  +            event_text = line.replace(year, "").strip("ΓÇó-* :").strip()
  +            if event_text and len(event_text) > 10 and len(event_text) < 300:
  +                events.append((int(year), event_text))
  +                
  +    events = sorted(list(set(events)), key=lambda x: x[0])
  +    
  +    if not events:
  +        return '<div class="concept-tip-card" style="border-left-color:#d97706;"><div class="concept-tip-title" style="color:#92400e;">≡ƒôà Chronology & Timeline</div><p>No historical milestones or chronological dates are listed for this specific topic.</p></div>'
  +        
  +    html = '<div class="section"><h3>≡ƒôà Chronology & Historical Timeline</h3><p style="color:#666;margin-bottom:1.5rem;">Study the sequential milestone events for this topic. Chronology is crucial for matching and board exam essay questions.</p><div class="social-timeline-container">'
  +    for year, text in events:
  +        words = text.split()
  +        title = " ".join(words[:5]) + "..." if len(words) > 5 else text
  +        html += f"""
  +        <div class="timeline-item">
  +            <span class="timeline-marker"></span>
  +            <span class="timeline-year">{year}</span>
  +            <div class="timeline-content">
  +                <h4>{htmlmod.escape(title)}</h4>
  +                <p>{format_social_content(text)}</p>
  +            </div>
  +        </div>
  +        """
  +    html += '</div></div>'
  +    return html
  +
  +
  +def format_social_solved_problem(p, idx):
  +    qtext = format_social_content(p.get("problem_text", ""))
  +    stext = p.get("solution_text", "")
  +    
  +    step_matches = re.split(r'(?:^|\n)(?:Step\s*\d+\s*:|Step\s*\d+\b|\d+\.\s+)', stext)
  +    steps_html = ""
  +    step_num = 1
  +    for part in step_matches:
  +        part_clean = part.strip()
  +        if not part_clean:
  +            continue
  +        step_formatted = format_social_content(part_clean)
  +        steps_html += f"""
  +        <div class="step-container">
  +            <span class="step-badge" style="background:#d97706;">{step_num}</span>
  +            <div class="step-content">{step_formatted}</div>
  +        </div>
  +        """
  +        step_num += 1
  +        
  +    if not steps_html:
  +        steps_html = format_social_content(stext)
  +        
  +    return f"""
  +    <div class="solved-problem-card" style="border-color:rgba(217,119,6,0.15);">
  +        <div class="solved-problem-header" style="background:#fffdfa;" onclick="this.classList.toggle('open'); this.nextElementSibling.classList.toggle('open'); var sign = this.querySelector('.sign'); if (sign) sign.textContent = this.classList.contains('open') ? 'ΓêÆ' : '+';">
  +            <span>Γ¥ô Question {idx}: {htmlmod.escape(p.get('problem_text', '')[:300])}...</span>
  +            <span class="sign" style="font-size:1.2rem; color:#d97706; font-weight:bold;">+</span>
  +        </div>
  +        <div class="solved-problem-body">
  +            <div class="problem-box" style="margin-top:0; border-color:rgba(217,119,6,0.15); background:#fcfcf9;">
  +                <div class="problem-header" style="color:#d97706; border-bottom-color:rgba(217,119,6,0.15);">Problem Statement</div>
  +                <div class="problem-text">{qtext}</div>
  +            </div>
  +            <div class="solution-steps" style="border-color:rgba(217,119,6,0.15); background:#fcfcfc;">
  +                <div class="problem-header" style="color:var(--success); border-bottom-color:rgba(16,185,129,0.1);">Detailed Answer Points</div>
  +                {steps_html}
  +            </div>
  +            <div class="concept-tip-card" style="margin-top: 1rem; margin-bottom: 0; border-left-color:#d97706;">
  +                <div class="concept-tip-title" style="color:#92400e;">≡ƒ¢í∩╕Å Exam Tip</div>
  +                <p>Present social science answers in bulleted points rather than long paragraphs. Underline key keywords, historical names, and dates to capture the evaluator's attention.</p>
  +            </div>
  +        </div>
  +    </div>
  +    """
  +
  +
  +
  +def format_general_content(text):
  +    if not text:
  +        return ""
  +    html = format_content(text)
  +    
  +    # 1. Key Vocabulary / Terms
  +    html = re.sub(
  +        r'(<p>)?<strong>(Vocabulary|Meaning|Definition|Grammar Rule|Character)\b([^:]*):?</strong>(.*?)(</p>)?',
  +        r'<div class="social-term-card" style="border-left-color:var(--accent);"><div class="term-title" style="color:var(--primary-light);">≡ƒÅ╖∩╕Å <span class="term-badge" style="background:#e0f2fe; color:#0369a1;">\2\3</span></div><div>\4</div></div>',
  +        html,
  +        flags=re.DOTALL | re.IGNORECASE
  +    )
  +    
  +    # 2. General Board exam tips
  +    html = re.sub(
  +        r'(<p>)?<strong>(Key points|Summary|Board Exam Tip|Tip)\b([^:]*):?</strong>(.*?)(</p>)?',
  +        r'<div class="concept-tip-card" style="border-left-color:var(--accent2);"><div class="concept-tip-title" style="color:var(--primary);">≡ƒÆí \2\3</div><div>\4</div></div>',
  +        html,
  +        flags=re.DOTALL | re.IGNORECASE
  +    )
  +    return html
  +
  +
  +def build_general_glossary(content, chunks):
  +    all_text = (content or "") + "\n" + "\n".join(c.get("content", "") for c in chunks)
  +    terms = []
  +    lines = all_text.split("\n")
  +    for line in lines:
  +        if ":" in line and "**" in line:
  +            match = re.match(r'^\s*[-*ΓÇó]?\s*\*\*(.*?)\*\*:\s*(.*)', line)
  +            if match:
  +                term, val = match.groups()
  +                if len(term) < 50 and len(val) > 5 and len(val) < 200:
  +                    terms.append((term, val))
  +                    
  +    if not terms:
  +        return '<div class="concept-tip-card" style="border-left-color:var(--accent2);"><div class="concept-tip-title">≡ƒôÜ Glossary & Terms</div><p>Refer to the Concept Explainer tab for core definitions and summaries.</p></div>'
  +        
  +    html = '<div class="section"><h3>≡ƒôÜ Glossary & Key Reference Words</h3><p style="color:#666;margin-bottom:1.5rem;">Study key glossary words and reference terms to master comprehension and writing skills.</p>'
  +    for term, val in terms:
  +        html += f"""
  +        <div class="social-term-card" style="border-left-color:var(--accent);">
  +            <div class="term-title">≡ƒÅ╖∩╕Å <span class="term-badge" style="background:#e0f2fe; color:#0369a1;">{htmlmod.escape(term)}</span></div>
  +            <p>{format_general_content(val)}</p>
  +        </div>
  +        """
  +    html += '</div>'
  +    return html
  +
  +
  +def format_general_solved_problem(p, idx):
  +    qtext = format_general_content(p.get("problem_text", ""))
  +    stext = p.get("solution_text", "")
  +    
  +    step_matches = re.split(r'(?:^|\n)(?:Step\s*\d+\s*:|Step\s*\d+\b|\d+\.\s+)', stext)
  +    steps_html = ""
  +    step_num = 1
  +    for part in step_matches:
  +        part_clean = part.strip()
  +        if not part_clean:
  +            continue
  +        step_formatted = format_general_content(part_clean)
  +        steps_html += f"""
  +        <div class="step-container">
  +            <span class="step-badge" style="background:var(--accent);">{step_num}</span>
  +            <div class="step-content">{step_formatted}</div>
  +        </div>
  +        """
  +        step_num += 1
  +        
  +    if not steps_html:
  +        steps_html = format_general_content(stext)
  +        
  +    return f"""
  +    <div class="solved-problem-card" style="border-color:var(--border);">
  +        <div class="solved-problem-header" style="background:#fafafa;" onclick="this.classList.toggle('open'); this.nextElementSibling.classList.toggle('open'); var sign = this.querySelector('.sign'); if (sign) sign.textContent = this.classList.contains('open') ? 'ΓêÆ' : '+';">
  +            <span>Γ¥ô Question {idx}: {htmlmod.escape(p.get('problem_text', '')[:300])}...</span>
  +            <span class="sign" style="font-size:1.2rem; color:var(--accent); font-weight:bold;">+</span>
  +        </div>
  +        <div class="solved-problem-body">
  +            <div class="problem-box" style="margin-top:0; border-color:var(--border); background:#fcfcfc;">
  +                <div class="problem-header" style="color:var(--primary); border-bottom-color:var(--border);">Problem Statement</div>
  +                <div class="problem-text">{qtext}</div>
  +            </div>
  +            <div class="solution-steps" style="border-color:var(--border); background:#fcfcfc;">
  +                <div class="problem-header" style="color:var(--success); border-bottom-color:rgba(16,185,129,0.1);">Detailed Solution</div>
  +                {steps_html}
  +            </div>
  +            <div class="concept-tip-card" style="margin-top: 1rem; margin-bottom: 0; border-left-color:var(--accent);">
  +                <div class="concept-tip-title" style="color:var(--primary-light);">≡ƒ¢í∩╕Å Exam Tip</div>
  +                <p>Provide contextual explanations, structured points, and reference correct spelling and terms to secure high marks in exams.</p>
  +            </div>
  +        </div>
  +    </div>
  +    """
  +
  +
  +@app.get("/topic/{topic_id}", response_class=HTMLResponse)
  +async def topic_page(topic_id: str):
  +    conn = DB
  +    topic = conn.query_one("SELECT * FROM topics WHERE id = ?", (topic_id,))
  +    if not topic:
  +        return HTMLResponse(
  +            _render(title="Topic Not Found", content='<div class="section"><h2>Topic Not Found</h2><p><a href="/">Go Home</a></p></div>'),
  +            status_code=404
  +        )
  +    chapter = conn.query_one("SELECT * FROM chapters WHERE id = ?", (topic["chapter_id"],))
  +    subject = conn.query_one("SELECT * FROM subjects WHERE id = ?", (chapter["subject_id"],)) if chapter else None
  +    chunks = conn.query("SELECT * FROM chunks WHERE topic_id = ? ORDER BY seq", (topic_id,))
  +
  +    bc_items = [("Home", "/")]
  +    if subject:
  +        bc_items.append((subject.get("board_id", "").upper(), f"/board/{subject['board_id'].lower()}"))
  +        bc_items.append((subject.get("name", ""), None))
  +    bc_items.append((f"Ch {chapter['num']}: {chapter['title']}", f"/chapter/{chapter['id']}"))
  +    bc_items.append((topic["title"], None))
  +
  +    is_math = subject and ("math" in subject.get("id", "").lower() or "math" in subject.get("name", "").lower())
  +    is_science = subject and ("science" in subject.get("id", "").lower() or "science" in subject.get("name", "").lower())
  +    is_social = subject and any(x in subject.get("id", "").lower() or x in subject.get("name", "").lower() for x in ["social", "history", "geography", "civics", "political", "economics", "democrat"])
  +
  +    if is_math:
  +        content_html = format_math_content(topic.get("content", ""))
  +        chunks_html = ""
  +        for c in chunks:
  +            chunks_html += f"""<div class="section" id="chunk-{c['id']}">
  +<h3>{htmlmod.escape(c.get("title",""))}</h3>
  +<div class="chunk-content">{format_math_content(c.get("content",""))}</div>
  +</div>"""
  +
  +        problems = conn.query("SELECT * FROM problems WHERE topic_id = ? ORDER BY seq", (topic_id,)) if conn.table_exists("problems") else []
  +        if not problems and chapter:
  +            problems = conn.query("SELECT * FROM problems WHERE chapter_id = ? ORDER BY seq LIMIT 6", (chapter["id"],)) if conn.table_exists("problems") else []
  +
  +        solved_html = ""
  +        for idx, p in enumerate(problems, 1):
  +            solved_html += format_solved_problem(p, idx)
  +        if not solved_html:
  +            solved_html = '<p style="color:#666;">No practice problems for this topic yet.</p>'
  +
  +        formulas_html = build_math_cheat_sheet(topic.get("content", ""), chunks)
  +
  +        # Tabbed Layout construction
  +        content = f"""<div class="breadcrumb">{_build_breadcrumb(bc_items)}</div>
  +<div class="section">
  +<h2>{htmlmod.escape(topic['title'])}</h2>
  +<div class="chapter-actions" style="margin-bottom:1.5rem;">
  +<a href="/tutor/{topic_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒºá AI Tutor</a>
  +<a href="/mindmap/{topic_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒù║∩╕Å Mind Map</a>
  +<a href="/interactives/cards/{topic_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒâÅ Flashcards</a>
  +</div>
  +
  +<div class="math-tabs">
  +  <button class="math-tab-btn active" onclick="switchMathTab('concept')">≡ƒôû Concept Explainer</button>
  +  <button class="math-tab-btn" onclick="switchMathTab('formulas')">ΓÜí Formulas & Theorems</button>
  +  <button class="math-tab-btn" onclick="switchMathTab('problems')">≡ƒô¥ Solved Exercises</button>
  +</div>
  +
  +<div id="math-tab-concept" class="math-tab-content active">
  +  {content_html}
  +  {chunks_html}
  +</div>
  +
  +<div id="math-tab-formulas" class="math-tab-content">
  +  {formulas_html}
  +</div>
  +
  +<div id="math-tab-problems" class="math-tab-content">
  +  <div class="section">
  +    <h3>≡ƒô¥ NCERT Solved Practice Exercises</h3>
  +    <p style="color:#666;margin-bottom:1.5rem;">Study step-by-step solved solutions. Tap any question to toggle the active-recall solution view.</p>
  +    {solved_html}
  +  </div>
  +</div>
  +</div>"""
  +    elif is_science:
  +        content_html = format_science_content(topic.get("content", ""))
  +        chunks_html = ""
  +        for c in chunks:
  +            chunks_html += f"""<div class="section" id="chunk-{c['id']}">
  +<h3>{htmlmod.escape(c.get("title",""))}</h3>
  +<div class="chunk-content">{format_science_content(c.get("content",""))}</div>
  +</div>"""
  +
  +        problems = conn.query("SELECT * FROM problems WHERE topic_id = ? ORDER BY seq", (topic_id,)) if conn.table_exists("problems") else []
  +        if not problems and chapter:
  +            problems = conn.query("SELECT * FROM problems WHERE chapter_id = ? ORDER BY seq LIMIT 6", (chapter["id"],)) if conn.table_exists("problems") else []
  +
  +        solved_html = ""
  +        for idx, p in enumerate(problems, 1):
  +            solved_html += format_science_solved_problem(p, idx)
  +        if not solved_html:
  +            solved_html = '<p style="color:#666;">No practice problems for this topic yet.</p>'
  +
  +        experiments_html = build_science_experiment_lab(topic.get("content", ""), chunks)
  +
  +        # Tabbed Layout construction
  +        content = f"""<div class="breadcrumb">{_build_breadcrumb(bc_items)}</div>
  +<div class="section">
  +<h2>{htmlmod.escape(topic['title'])}</h2>
  +<div class="chapter-actions" style="margin-bottom:1.5rem;">
  +<a href="/tutor/{topic_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒºá AI Tutor</a>
  +<a href="/mindmap/{topic_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒù║∩╕Å Mind Map</a>
  +<a href="/interactives/cards/{topic_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒâÅ Flashcards</a>
  +</div>
  +
  +<div class="math-tabs">
  +  <button class="math-tab-btn active" onclick="switchMathTab('concept')">≡ƒôû Concept Explainer</button>
  +  <button class="math-tab-btn" onclick="switchMathTab('formulas')">≡ƒº¬ Experiment Lab</button>
  +  <button class="math-tab-btn" onclick="switchMathTab('problems')">≡ƒô¥ Solved Exercises</button>
  +</div>
  +
  +<div id="math-tab-concept" class="math-tab-content active">
  +  {content_html}
  +  {chunks_html}
  +</div>
  +
  +<div id="math-tab-formulas" class="math-tab-content">
  +  {experiments_html}
  +</div>
  +
  +<div id="math-tab-problems" class="math-tab-content">
  +  <div class="section">
  +    <h3>≡ƒô¥ NCERT Solved Practice Exercises</h3>
  +    <p style="color:#666;margin-bottom:1.5rem;">Study step-by-step solved solutions. Tap any question to toggle the active-recall solution view.</p>
  +    {solved_html}
  +  </div>
  +</div>
  +</div>"""
  +    elif is_social:
  +        content_html = format_social_content(topic.get("content", ""))
  +        chunks_html = ""
  +        for c in chunks:
  +            chunks_html += f"""<div class="section" id="chunk-{c['id']}">
  +<h3>{htmlmod.escape(c.get("title",""))}</h3>
  +<div class="chunk-content">{format_social_content(c.get("content",""))}</div>
  +</div>"""
  +
  +        problems = conn.query("SELECT * FROM problems WHERE topic_id = ? ORDER BY seq", (topic_id,)) if conn.table_exists("problems") else []
  +        if not problems and chapter:
  +            problems = conn.query("SELECT * FROM problems WHERE chapter_id = ? ORDER BY seq LIMIT 6", (chapter["id"],)) if conn.table_exists("problems") else []
  +
  +        solved_html = ""
  +        for idx, p in enumerate(problems, 1):
  +            solved_html += format_social_solved_problem(p, idx)
  +        if not solved_html:
  +            solved_html = '<p style="color:#666;">No practice problems for this topic yet.</p>'
  +
  +        timeline_html = build_social_timeline(topic.get("content", ""), chunks)
  +
  +        # Tabbed Layout construction
  +        content = f"""<div class="breadcrumb">{_build_breadcrumb(bc_items)}</div>
  +<div class="section">
  +<h2>{htmlmod.escape(topic['title'])}</h2>
  +<div class="chapter-actions" style="margin-bottom:1.5rem;">
  +<a href="/tutor/{topic_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒºá AI Tutor</a>
  +<a href="/mindmap/{topic_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒù║∩╕Å Mind Map</a>
  +<a href="/interactives/cards/{topic_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒâÅ Flashcards</a>
  +</div>
  +
  +<div class="math-tabs">
  +  <button class="math-tab-btn active" onclick="switchMathTab('concept')">≡ƒôû Concept Explainer</button>
  +  <button class="math-tab-btn" onclick="switchMathTab('formulas')">≡ƒôà Timeline & Events</button>
  +  <button class="math-tab-btn" onclick="switchMathTab('problems')">≡ƒô¥ Solved Exercises</button>
  +</div>
  +
  +<div id="math-tab-concept" class="math-tab-content active">
  +  {content_html}
  +  {chunks_html}
  +</div>
  +
  +<div id="math-tab-formulas" class="math-tab-content">
  +  {timeline_html}
  +</div>
  +
  +<div id="math-tab-problems" class="math-tab-content">
  +  <div class="section">
  +    <h3>≡ƒô¥ NCERT Solved Practice Exercises</h3>
  +    <p style="color:#666;margin-bottom:1.5rem;">Study step-by-step solved solutions. Tap any question to toggle the active-recall solution view.</p>
  +    {solved_html}
  +  </div>
  +</div>
  +</div>"""
  +
  +    else:
  +        content_html = format_general_content(topic.get("content", ""))
  +        chunks_html = ""
  +        for c in chunks:
  +            chunks_html += f"""<div class="section" id="chunk-{c['id']}">
  +<h3>{htmlmod.escape(c.get("title",""))}</h3>
  +<div class="chunk-content">{format_general_content(c.get("content",""))}</div>
  +</div>"""
  +
  +        problems = conn.query("SELECT * FROM problems WHERE topic_id = ? ORDER BY seq", (topic_id,)) if conn.table_exists("problems") else []
  +        if not problems and chapter:
  +            problems = conn.query("SELECT * FROM problems WHERE chapter_id = ? ORDER BY seq LIMIT 6", (chapter["id"],)) if conn.table_exists("problems") else []
  +
  +        solved_html = ""
  +        for idx, p in enumerate(problems, 1):
  +            solved_html += format_general_solved_problem(p, idx)
  +        if not solved_html:
  +            solved_html = '<p style="color:#666;">No practice problems for this topic yet.</p>'
  +
  +        glossary_html = build_general_glossary(topic.get("content", ""), chunks)
  +
  +        # Tabbed Layout construction
  +        content = f"""<div class="breadcrumb">{_build_breadcrumb(bc_items)}</div>
  +<div class="section">
  +<h2>{htmlmod.escape(topic['title'])}</h2>
  +<div class="chapter-actions" style="margin-bottom:1.5rem;">
  +<a href="/tutor/{topic_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒºá AI Tutor</a>
  +<a href="/mindmap/{topic_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒù║∩╕Å Mind Map</a>
  +<a href="/interactives/cards/{topic_id}" class="tts-btn" style="font-size:0.8rem;">≡ƒâÅ Flashcards</a>
  +</div>
  +
  +<div class="math-tabs">
  +  <button class="math-tab-btn active" onclick="switchMathTab('concept')">≡ƒôû Concept Explainer</button>
  +  <button class="math-tab-btn" onclick="switchMathTab('formulas')">≡ƒôÜ Vocabulary & Reference</button>
  +  <button class="math-tab-btn" onclick="switchMathTab('problems')">≡ƒô¥ Solved Exercises</button>
  +</div>
  +
  +<div id="math-tab-concept" class="math-tab-content active">
  +  {content_html}
  +  {chunks_html}
  +</div>
  +
  +<div id="math-tab-formulas" class="math-tab-content">
  +  {glossary_html}
  +</div>
  +
  +<div id="math-tab-problems" class="math-tab-content">
  +  <div class="section">
  +    <h3>≡ƒô¥ NCERT Solved Practice Exercises</h3>
  +    <p style="color:#666;margin-bottom:1.5rem;">Study step-by-step solved solutions. Tap any question to toggle the active-recall solution view.</p>
  +    {solved_html}
  +  </div>
  +</div>
  +</div>"""
  +
  +
  +
  +    return HTMLResponse(_render(title=f"{topic['title']} - AI Study Companion", content=content))
  +
  +
  +
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +# API ROUTES ΓÇö ASYNC
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +
  +@app.post("/api/tutor/start")
  +@rate_limit(30)
  +async def api_tutor_start(request: Request, user: Optional[dict] = Depends(get_current_user)):
  +    data = await request.form()
  +    topic_id = data.get("topic_id", "")
  +    if not topic_id:
  +        return JSONResponse({"error": "Missing topic_id"}, status_code=400)
  +    conn = DB
  +    topic = conn.query_one("SELECT * FROM topics WHERE id = ?", (topic_id,))
  +    if not topic:
  +        return JSONResponse({"error": "Topic not found"}, status_code=404)
  +    chunks = conn.query("SELECT * FROM chunks WHERE topic_id = ? ORDER BY seq", (topic_id,))
  +    questions = ai_tutor.generate_questions(topic["title"], topic.get("content", ""), chunks, 3)
  +    session_id = ai_tutor.create_tutor_session(topic_id)
  +    return {"session_id": session_id, "questions": questions, "topic_title": topic["title"]}
  +
  +
  +@app.post("/api/tutor/answer")
  +@rate_limit(60)
  +async def api_tutor_answer(request: Request, user: Optional[dict] = Depends(get_current_user)):
  +    data = await request.form()
  +    try:
  +        session_id = int(data.get("session_id", 0))
  +    except (ValueError, TypeError):
  +        return JSONResponse({"error": "Invalid session_id"}, status_code=400)
  +    question = data.get("question", "")
  +    qtype = data.get("qtype", "")
  +    model_answer = data.get("model_answer", "")
  +    student_answer = data.get("student_answer", "")
  +    if not session_id or not question:
  +        return JSONResponse({"error": "Missing fields"}, status_code=400)
  +    session = DB.query_one("SELECT id FROM tutor_sessions WHERE id = ?", (session_id,))
  +    if not session:
  +        return JSONResponse({"error": "Invalid session"}, status_code=400)
  +    answer_id = ai_tutor.save_answer(session_id, question, qtype, model_answer, student_answer)
  +    return {"answer_id": answer_id, "status": "ok"}
  +
  +
  +@app.post("/api/tutor/remedial")
  +@rate_limit(30)
  +async def api_tutor_remedial(request: Request, user: Optional[dict] = Depends(get_current_user)):
  +    data = await request.form()
  +    try:
  +        answer_id = int(data.get("answer_id", 0))
  +        session_id = int(data.get("session_id", 0))
  +    except (ValueError, TypeError):
  +        return JSONResponse({"error": "Invalid params"}, status_code=400)
  +    self_assessment = data.get("self_assessment", "")
  +    if not answer_id or not self_assessment:
  +        return JSONResponse({"error": "Missing fields"}, status_code=400)
  +    ai_tutor.update_answer(answer_id, data.get("student_answer", ""), self_assessment)
  +    if self_assessment == "correct":
  +        return {"status": "ok", "remedial_html": ""}
  +    answer = DB.query_one(
  +        "SELECT ta.*, ts.topic_id FROM tutor_answers ta "
  +        "JOIN tutor_sessions ts ON ta.session_id = ts.id WHERE ta.id = ?",
  +        (answer_id,)
  +    )
  +    if not answer:
  +        return {"status": "ok", "remedial_html": ""}
  +    topic = DB.query_one("SELECT * FROM topics WHERE id = ?", (answer["topic_id"],))
  +    chunks = DB.query("SELECT * FROM chunks WHERE topic_id = ? ORDER BY seq", (answer["topic_id"],))
  +    remedial = ai_tutor.get_remedial_content(
  +        topic["content"] if topic else "",
  +        chunks,
  +        answer["question_type"],
  +        answer["question"]
  +    )
  +    html = f'<div class="tutor-remedial"><h4>≡ƒôÜ Let\'s Review This</h4><div class="tutor-remedial-content">{format_content(remedial)}</div></div>'
  +    return {"status": "ok", "remedial_html": html}
  +
  +
  +@app.post("/api/tutor/complete")
  +@rate_limit(30)
  +async def api_tutor_complete(request: Request, user: Optional[dict] = Depends(get_current_user)):
  +    data = await request.form()
  +    try:
  +        session_id = int(data.get("session_id", 0))
  +    except (ValueError, TypeError):
  +        return JSONResponse({"error": "Invalid session_id"}, status_code=400)
  +    xp = ai_tutor.complete_session(session_id)
  +    return {"status": "ok", "xp": xp}
  +
  +
  +@app.get("/api/ai/enrich")
  +@rate_limit(20)
  +async def api_ai_enrich(request: Request, topic: str = Query(...), chapter: str = Query(""), subject: str = Query(""), topic_type: str = Query("concept")):
  +    loop = asyncio.get_event_loop()
  +    enriched = await loop.run_in_executor(
  +        None, content_enricher.enrich_topic_content,
  +        topic, chapter, subject, "", topic_type
  +    )
  +    html = content_enricher.format_ai_content(enriched)
  +    return {"html": html, "cached": bool(enriched.get("explanation"))}
  +
  +
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +# AI TOOL API HANDLERS
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +
  +
  +async def _run_in_thread(func, *args):
  +    loop = asyncio.get_event_loop()
  +    return await loop.run_in_executor(None, func, *args)
  +
  +
  +@app.get("/api/ai/diagram")
  +@rate_limit(20)
  +async def api_ai_diagram(request: Request, concept: str = Query(...), type: str = Query("flowchart")):
  +    result = await _run_in_thread(ai_services.napkin_diagram, concept, type)
  +    return result
  +
  +
  +@app.get("/api/ai/presentation")
  +@rate_limit(10)
  +async def api_ai_presentation(request: Request, subject: str = Query(...), chapter: str = Query(...)):
  +    idx = get_index()
  +    topics = idx.get_chapter(chapter) if hasattr(idx, 'get_chapter') else []
  +    result = await _run_in_thread(ai_services.gamma_presentation, subject, chapter, topics)
  +    return result
  +
  +
  +@app.get("/api/ai/story")
  +@rate_limit(20)
  +async def api_ai_story(request: Request, topic: str = Query(...), chapter: str = Query(""), subject: str = Query("CBSE Science")):
  +    result = await _run_in_thread(ai_services.tome_story, topic, chapter, subject)
  +    return result
  +
  +
  +@app.get("/api/ai/music")
  +@rate_limit(20)
  +async def api_ai_music(request: Request, mood: str = Query("calm study piano")):
  +    result = await _run_in_thread(ai_services.browser_music_params, mood)
  +    return result
  +
  +
  +@app.get("/api/ai/pomelli")
  +@rate_limit(30)
  +async def api_ai_pomelli(request: Request, template: str = Query(...), a: str = Query(None), b: str = Query(None), c: str = Query(None)):
  +    params = {}
  +    if a is not None: params["a"] = a
  +    if b is not None: params["b"] = b
  +    if c is not None: params["c"] = c
  +    if template == "list":
  +        return ai_services.pomelli_list_templates()
  +    result = await _run_in_thread(ai_services.pomelli_generate, template, params)
  +    return result
  +
  +
  +@app.get("/api/ai/metai")
  +@rate_limit(10)
  +async def api_ai_metai(request: Request, concept: str = Query(...), style: str = Query("explainer"), subject: str = Query("Science")):
  +    result = await _run_in_thread(ai_services.metai_generate, concept, subject, style)
  +    return result
  +
  +
  +@app.get("/api/ai/opengrok")
  +@rate_limit(30)
  +async def api_ai_opengrok(request: Request, query: str = Query(...)):
  +    loop = asyncio.get_event_loop()
  +    results = await loop.run_in_executor(None, ai_services.opengrok_search, query)
  +    html = ai_services.opengrok_results_html(query)
  +    return {"results": results, "html": html}
  +
  +
  +@app.get("/api/ai/notebooklm")
  +@rate_limit(10)
  +async def api_ai_notebooklm(request: Request, subject: str = Query(...), chapter: str = Query(...), topic: str = Query(None)):
  +    if topic:
  +        result = await _run_in_thread(ai_services.notebooklm_pedagogical, subject, chapter, topic)
  +    else:
  +        idx = get_index()
  +        topics = idx.get_chapter(chapter) if hasattr(idx, 'get_chapter') else []
  +        result = await _run_in_thread(ai_services.notebooklm_export, subject, chapter, topics)
  +    return result
  +
  +
  +@app.get("/api/ai/youtube")
  +@rate_limit(20)
  +async def api_ai_youtube(request: Request, topic: str = Query(...), chapter: str = Query(""), subject: str = Query("")):
  +    html = await _run_in_thread(ai_services.youtube_section_html, topic, chapter, subject)
  +    results = await _run_in_thread(ai_services.youtube_search, f"{topic} {chapter} {subject}")
  +    return {"html": html, "results": results}
  +
  +
  +@app.get("/api/ai/youtube/generate")
  +@rate_limit(5)
  +async def api_ai_youtube_generate(request: Request, topic_id: str = Query(""), chapter_id: str = Query(""), topic_name: str = Query(""), max_clips: int = Query(8)):
  +    result = await _run_in_thread(ai_services.youtube_generate_clips,
  +                                  topic_id or None, chapter_id or None, topic_name or None, min(max_clips, 20))
  +    return result
  +
  +
  +@app.get("/api/ai/research")
  +@rate_limit(10)
  +async def api_ai_research(request: Request, query: str = Query(...), subject: str = Query("CBSE")):
  +    result = await _run_in_thread(ai_services.llm_research, query, subject)
  +    return result
  +
  +
  +@app.get("/api/ai/literature")
  +@rate_limit(10)
  +async def api_ai_literature(request: Request, query: str = Query(...), subject: str = Query("science")):
  +    result = await _run_in_thread(ai_services.llm_literature, query, subject)
  +    return result
  +
  +
  +@app.get("/api/ai/visualize")
  +@rate_limit(20)
  +async def api_ai_visualize(request: Request, concept: str = Query(...), style: str = Query("diagram")):
  +    result = await _run_in_thread(ai_services.svg_visualize, concept, style)
  +    return result
  +
  +
  +@app.get("/api/ai/gemma4")
  +@rate_limit(10)
  +async def api_ai_gemma4(request: Request, prompt: str = Query(...), system: str = Query(None)):
  +    result = await _run_in_thread(ai_services.gemma4_query, prompt, system)
  +    return {"response": result}
  +
  +
  +@app.get("/api/ai/flash")
  +@rate_limit(10)
  +async def api_ai_flash(request: Request, prompt: str = Query(...), system: str = Query(None)):
  +    result = await _run_in_thread(ai_services.google_flash_query, prompt, system)
  +    return {"response": result}
  +
  +
  +@app.get("/api/ai/quillbot")
  +@rate_limit(20)
  +async def api_ai_quillbot(request: Request, text: str = Query(...), mode: str = Query("simpler")):
  +    result = await _run_in_thread(ai_services.quillbot_paraphrase, text, mode)
  +    return result
  +
  +
  +@app.get("/api/ai/voiceover")
  +@rate_limit(30)
  +async def api_ai_voiceover(request: Request, text: str = Query(...), voice: str = Query("female"), lang: str = Query("en-IN")):
  +    result = ai_services.quillbot_speak_segments(text, lang, voice)
  +    return result
  +
  +
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +# AI TOOL PAGES
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +
  +@app.get("/ai/diagram", response_class=HTMLResponse)
  +async def ai_diagram():
  +    return _render(
  +        title="AI Diagram Generator ΓÇö AI Study Companion",
  +        content="""
  +        <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> <a href="/ai">AI Studio</a> <span class="sep">ΓÇ║</span> Diagram Generator</div>
  +        <div class="section">
  +            <h2>≡ƒôÉ AI Diagram & Mind Map Generator</h2>
  +            <p class="subtitle">Generate interactive flowcharts, mind maps, and concept diagrams grounded in local NCERT textbook contexts</p>
  +            <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +                <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Concept</label>
  +                <input type="text" id="diagram-concept" value="Photosynthesis" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +                <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Type</label>
  +                <select id="diagram-type" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +                    <option value="flowchart">Flowchart</option>
  +                    <option value="mindmap">Mind Map</option>
  +                    <option value="concept-map">Concept Map</option>
  +                </select>
  +                <button onclick="generateDiagram()" class="btn-primary" style="padding:0.8rem 2rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;">Generate</button>
  +                <div id="diagram-output" style="margin-top:1.5rem;padding:1.5rem;border:1px solid var(--border);border-radius:12px;min-height:200px;background:#fcfcfd;display:flex;justify-content:center;align-items:center;overflow-x:auto;">
  +                    <span style="color:#888;font-size:0.95rem;">Your generated visual diagram will appear here.</span>
  +                </div>
  +            </div>
  +        </div>
  +        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
  +        <script>
  +        mermaid.initialize({ startOnLoad: false, theme: 'neutral', securityLevel: 'loose' });
  +        function runInjectedScripts(container) {
  +            const scripts = container.querySelectorAll('script');
  +            scripts.forEach(s => {
  +                const newScript = document.createElement('script');
  +                newScript.textContent = s.textContent;
  +                document.body.appendChild(newScript);
  +            });
  +        }
  +        async function generateDiagram() {
  +            const concept = document.getElementById('diagram-concept').value;
  +            const type = document.getElementById('diagram-type').value;
  +            const out = document.getElementById('diagram-output');
  +            out.innerHTML = '<em>Generating visual diagram...</em>';
  +            try {
  +                const resp = await fetch('/api/ai/diagram?concept='+encodeURIComponent(concept)+'&type='+encodeURIComponent(type));
  +                const data = await resp.json();
  +                if (data.html) {
  +                    out.innerHTML = data.html;
  +                    runInjectedScripts(out);
  +                } else if (data.diagram) {
  +                    const id = 'mermaid-' + Math.floor(Math.random() * 10000);
  +                    let contentHtml = '<div style="display:flex; flex-direction:column; gap:1.5rem; width:100%;">';
  +                    contentHtml += '<div class="mermaid-card" style="background:#fff; padding:1.5rem; border-radius:12px; border:1px solid var(--border); box-shadow:0 4px 12px rgba(0,0,0,0.03);">';
  +                    contentHtml += '<div class="mermaid" id="' + id + '" style="width:100%; text-align:center; overflow-x:auto;">' + data.diagram + '</div>';
  +                    contentHtml += '</div>';
  +                    
  +                    if (data.explanation) {
  +                        let headerTitle = "≡ƒôû Study Guide & Exam Prep";
  +                        let introText = "";
  +                        if (type === 'mindmap') {
  +                            headerTitle = "≡ƒù║∩╕Å Dot-Connection & Association Guide";
  +                            introText = '<div style="margin-bottom:1rem; padding:1rem; border-radius:8px; background:#e0f2fe; border-left:4px solid #0284c7; font-size:0.95rem; color:#0369a1;"><strong>Mind Map focus: Connecting concepts & filling gaps.</strong> Mapping associative properties radially outward back to the core concept.</div>';
  +                        } else if (type === 'flowchart') {
  +                            headerTitle = "≡ƒôÉ Sequential Process & Outcomes Guide";
  +                            introText = '<div style="margin-bottom:1rem; padding:1rem; border-radius:8px; background:#fef3c7; border-left:4px solid #d97706; font-size:0.95rem; color:#b45309;"><strong>Flowchart focus: Step outcomes.</strong> Follow the step outcomes in the flowchart to understand the product at each milestone.</div>';
  +                        } else if (type === 'concept-map') {
  +                            headerTitle = "≡ƒöù Detailed Concept Relation Guide";
  +                            introText = '<div style="margin-bottom:1rem; padding:1rem; border-radius:8px; background:#dcfce7; border-left:4px solid #16a34a; font-size:0.95rem; color:#15803d;"><strong>Relation Map focus: High fidelity structural connections.</strong> Maps complex cross-links and semantic verbs. See the dynamic simulator player added below the diagram.</div>';
  +                        }
  +                        
  +                        contentHtml += '<div class="study-guide-card" style="background:#fff; padding:1.5rem; border-radius:12px; border:1px solid var(--border); box-shadow:0 4px 12px rgba(0,0,0,0.03); text-align:left;">';
  +                        contentHtml += '<h3 style="color:var(--primary); margin-top:0; border-bottom:1px solid var(--border); padding-bottom:0.5rem; display:flex; align-items:center; gap:0.5rem;">' + headerTitle + '</h3>';
  +                        contentHtml += introText;
  +                        contentHtml += '<div style="font-size:0.95rem; line-height:1.6; color:#333;">' + data.explanation + '</div>';
  +                        contentHtml += '</div>';
  +                    }
  +                    
  +                    // If concept-map, inject video simulator below the diagram card
  +                    if (type === 'concept-map') {
  +                        try {
  +                            const videoResp = await fetch('/api/ai/diagram?concept='+encodeURIComponent(concept)+'&type=veo-animator');
  +                            const videoData = await videoResp.json();
  +                            if (videoData.html) {
  +                                contentHtml += '<div style="margin-top:1.5rem; width:100%;">' + videoData.html + '</div>';
  +                            }
  +                        } catch (err) {
  +                            console.error("Failed to load video animator: ", err);
  +                        }
  +                    }
  +                    
  +                    contentHtml += '</div>';
  +                    out.innerHTML = contentHtml;
  +                    runInjectedScripts(out);
  +                    
  +                    await mermaid.run({
  +                        nodes: [document.getElementById(id)]
  +                    });
  +                } else {
  +                    out.innerHTML = '<em>No diagram generated</em>';
  +                }
  +            } catch(e) {
  +                out.innerHTML = '<em style="color:#dc2626;">Error: ' + e.message + '</em>';
  +            }
  +        }
  +        </script>"""
  +    )
  +
  +
  +@app.get("/ai/presentation", response_class=HTMLResponse)
  +async def ai_presentation():
  +    return _render(
  +        title="AI Presentation Generator ΓÇö AI Study Companion",
  +        content="""
  +        <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> <a href="/ai">AI Studio</a> <span class="sep">ΓÇ║</span> Presentation</div>
  +        <div class="section">
  +            <h2>≡ƒô╜∩╕Å AI Presentation Generator</h2>
  +            <p class="subtitle">Create HTML slide presentations for any topic using Mistral AI</p>
  +            <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +                <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Subject</label>
  +                <input type="text" id="pres-subject" value="Science" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +                <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Chapter / Topic</label>
  +                <input type="text" id="pres-chapter" value="Photosynthesis" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +                <button onclick="generatePresentation()" class="btn-primary" style="padding:0.8rem 2rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;">Generate</button>
  +                <div id="pres-output" style="margin-top:1rem;"></div>
  +            </div>
  +        </div>
  +        <script>
  +        async function generatePresentation() {
  +            const s = document.getElementById('pres-subject').value;
  +            const c = document.getElementById('pres-chapter').value;
  +            const out = document.getElementById('pres-output');
  +            out.innerHTML = '<em>Generating...</em>';
  +            try {
  +                const resp = await fetch('/api/ai/presentation?subject='+encodeURIComponent(s)+'&chapter='+encodeURIComponent(c));
  +                const data = await resp.json();
  +                out.innerHTML = data.html || '<em>No presentation generated</em>';
  +            } catch(e) {
  +                out.innerHTML = '<em>Error: ' + e.message + '</em>';
  +            }
  +        }
  +        </script>"""
  +    )
  +
  +
  +@app.get("/ai/voiceover", response_class=HTMLResponse)
  +async def ai_voiceover():
  +    return _render(
  +        title="AI Voiceover ΓÇö AI Study Companion",
  +        content="""
  +        <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> <a href="/ai">AI Studio</a> <span class="sep">ΓÇ║</span> Voiceover</div>
  +        <div class="section">
  +            <h2>≡ƒÄñ AI Voiceover Studio</h2>
  +            <p class="subtitle">Text-to-speech with Indian language support & voice-video sync</p>
  +            <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +                <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Script / Text to speak</label>
  +                <textarea id="vo-text" rows="4" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">In this lesson, we will learn about the process of photosynthesis. Plants use sunlight, water, and carbon dioxide to produce food and oxygen.</textarea>
  +                <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1rem;">
  +                    <div style="flex:1;min-width:140px;">
  +                        <label style="font-weight:500;display:block;font-size:0.85rem;margin-bottom:0.3rem;">Language</label>
  +                        <select id="vo-lang" style="width:100%;padding:0.5rem;border:1px solid var(--border);border-radius:6px;font-size:0.85rem;">
  +                            <option value="en-IN">English (India)</option>
  +                            <option value="hi-IN">αñ╣αñ┐αñ¿αÑìαñªαÑÇ (Hindi)</option>
  +                            <option value="te-IN">α░ñα▒åα░▓α▒üα░ùα▒ü (Telugu)</option>
  +                        </select>
  +                    </div>
  +                    <div style="flex:1;min-width:140px;">
  +                        <label style="font-weight:500;display:block;font-size:0.85rem;margin-bottom:0.3rem;">Voice</label>
  +                        <select id="vo-voice" style="width:100%;padding:0.5rem;border:1px solid var(--border);border-radius:6px;font-size:0.85rem;">
  +                            <option value="female">≡ƒæ⌐ Female</option>
  +                            <option value="male">≡ƒæ¿ Male</option>
  +                        </select>
  +                    </div>
  +                    <div style="flex:1;min-width:140px;">
  +                        <label style="font-weight:500;display:block;font-size:0.85rem;margin-bottom:0.3rem;">Rate</label>
  +                        <input type="range" id="vo-rate" min="0.5" max="2" step="0.1" value="1" oninput="document.getElementById('vo-rate-val').textContent=this.value" style="width:100%;">
  +                        <span id="vo-rate-val" style="font-size:0.8rem;color:#666;">1</span>
  +                    </div>
  +                </div>
  +                <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
  +                    <button onclick="speakText()" class="btn-primary" style="padding:0.7rem 1.5rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:0.95rem;font-weight:600;cursor:pointer;">≡ƒöè Speak</button>
  +                    <button onclick="stopSpeech()" style="padding:0.7rem 1.5rem;background:#fee2e2;color:#dc2626;border:none;border-radius:8px;font-size:0.95rem;font-weight:600;cursor:pointer;">ΓÅ╣ Stop</button>
  +                    <button onclick="syncWithVideo()" style="padding:0.7rem 1.5rem;background:#e8f4f8;color:#4a90d9;border:none;border-radius:8px;font-size:0.95rem;font-weight:600;cursor:pointer;">≡ƒÄ¼ Sync with Video</button>
  +                </div>
  +                <div id="vo-waveform" style="margin-top:1rem;height:60px;background:#f8f9fa;border-radius:8px;border:1px solid var(--border);overflow:hidden;position:relative;">
  +                    <canvas id="vo-canvas" style="width:100%;height:60px;"></canvas>
  +                </div>
  +                <div id="vo-status" style="margin-top:0.5rem;font-size:0.85rem;color:#666;text-align:center;"></div>
  +            </div>
  +        </div>
  +        <script>
  +        var voAudioCtx = null;
  +        var voAnalyser = null;
  +        var voSource = null;
  +        var voAnimationId = null;
  +        function speakText() {
  +            var text = document.getElementById('vo-text').value;
  +            var lang = document.getElementById('vo-lang').value;
  +            var voice = document.getElementById('vo-voice').value;
  +            var rate = parseFloat(document.getElementById('vo-rate').value);
  +            if (!('speechSynthesis' in window)) { alert('Text-to-speech not supported in this browser.'); return; }
  +            window.speechSynthesis.cancel();
  +            var utter = new SpeechSynthesisUtterance(text);
  +            utter.lang = lang;
  +            utter.rate = rate;
  +            utter.pitch = voice === 'female' ? 1.2 : 0.85;
  +            utter.onstart = function() { document.getElementById('vo-status').textContent = '≡ƒöè Speaking... (' + voice + ')'; startWaveform(); };
  +            utter.onend = function() { document.getElementById('vo-status').textContent = 'Γ£à Done'; stopWaveform(); };
  +            utter.onerror = function() { document.getElementById('vo-status').textContent = 'Γ¥î Error'; stopWaveform(); };
  +            window.speechSynthesis.speak(utter);
  +        }
  +        function stopSpeech() { window.speechSynthesis.cancel(); stopWaveform(); document.getElementById('vo-status').textContent = 'ΓÅ╣ Stopped'; }
  +        function startWaveform() {
  +            var canvas = document.getElementById('vo-canvas');
  +            var ctx = canvas.getContext('2d');
  +            canvas.width = canvas.offsetWidth;
  +            canvas.height = 60;
  +            var w = canvas.width, h = canvas.height;
  +            function draw() {
  +                ctx.clearRect(0,0,w,h);
  +                var bars = 48;
  +                var barW = (w - bars * 2) / bars;
  +                for (var i = 0; i < bars; i++) {
  +                    var val = Math.random() * 0.7 + 0.3;
  +                    var barH = val * h * 0.8;
  +                    var x = i * (barW + 2);
  +                    var hue = 200 + i * 3;
  +                    ctx.fillStyle = 'hsl(' + hue + ', 70%, 55%)';
  +                    ctx.globalAlpha = 0.7;
  +                    ctx.fillRect(x, (h - barH) / 2, barW, barH);
  +                }
  +                ctx.globalAlpha = 1;
  +                voAnimationId = requestAnimationFrame(draw);
  +            }
  +            draw();
  +        }
  +        function stopWaveform() { if (voAnimationId) { cancelAnimationFrame(voAnimationId); voAnimationId = null; } }
  +        function syncWithVideo() {
  +            var text = document.getElementById('vo-text').value;
  +            var voice = document.getElementById('vo-voice').value;
  +            var lang = document.getElementById('vo-lang').value;
  +            document.getElementById('vo-status').textContent = '≡ƒöä Generating voiceover segments for video sync...';
  +            fetch('/api/ai/voiceover?text='+encodeURIComponent(text)+'&voice='+voice+'&lang='+lang)
  +                .then(function(r) { return r.json(); })
  +                .then(function(data) {
  +                    if (data.tts === 'browser') {
  +                        document.getElementById('vo-status').textContent = 'Γ£à Ready for video sync. Click "Speak" to play voiceover with video.';
  +                        // Auto-start with a short delay for demo
  +                        setTimeout(function() { speakText(); }, 500);
  +                    } else {
  +                        document.getElementById('vo-status').textContent = 'Γ£à Voiceover synced';
  +                    }
  +                })
  +                .catch(function(e) { document.getElementById('vo-status').textContent = 'Γ¥î Sync error: ' + e.message; });
  +        }
  +        window.addEventListener('resize', function() {
  +            var canvas = document.getElementById('vo-canvas');
  +            if (canvas) canvas.width = canvas.offsetWidth;
  +        });
  +        </script>"""
  +    )
  +
  +
  +@app.get("/ai/music", response_class=HTMLResponse)
  +async def ai_music():
  +    return _render(
  +        title="AI Music ΓÇö AI Study Companion",
  +        content="""
  +        <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> <a href="/ai">AI Studio</a> <span class="sep">ΓÇ║</span> Music</div>
  +        <div class="section">
  +            <h2>≡ƒÄ╡ AI Music Generator</h2>
  +            <p class="subtitle">Generate study music with configurable mood parameters using Mistral AI</p>
  +            <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +                <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Mood</label>
  +                <select id="music-mood" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +                    <option value="calm study piano">Calm ΓÇö Study Piano</option>
  +                    <option value="focus ambient">Focus ΓÇö Ambient</option>
  +                    <option value="energetic learning">Energetic ΓÇö Learning</option>
  +                </select>
  +                <button onclick="generateMusic()" class="btn-primary" style="padding:0.8rem 2rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;">Generate</button>
  +                <div id="music-output" style="margin-top:1rem;padding:1rem;border:1px solid var(--border);border-radius:8px;min-height:60px;"></div>
  +            </div>
  +        </div>
  +        <script>
  +        async function generateMusic() {
  +            const mood = document.getElementById('music-mood').value;
  +            const out = document.getElementById('music-output');
  +            out.innerHTML = '<em>Generating music parameters...</em>';
  +            try {
  +                const resp = await fetch('/api/ai/music?mood='+encodeURIComponent(mood));
  +                const data = await resp.json();
  +                out.innerHTML = '<pre style="margin:0;">' + JSON.stringify(data, null, 2) + '</pre>';
  +            } catch(e) {
  +                out.innerHTML = '<em>Error: ' + e.message + '</em>';
  +            }
  +        }
  +        </script>"""
  +    )
  +
  +
  +@app.get("/ai/story", response_class=HTMLResponse)
  +async def ai_story():
  +    return _render(
  +        title="AI Story Generator ΓÇö AI Study Companion",
  +        content="""
  +        <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> <a href="/ai">AI Studio</a> <span class="sep">ΓÇ║</span> Story</div>
  +        <div class="section">
  +            <h2>≡ƒôû AI Story Generator</h2>
  +            <p class="subtitle">Generate educational stories that make learning fun ΓÇö powered by Mistral AI</p>
  +            <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +                <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Topic</label>
  +                <input type="text" id="story-topic" value="Photosynthesis" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +                <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Chapter</label>
  +                <input type="text" id="story-chapter" value="Life Processes" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +                <button onclick="generateStory()" class="btn-primary" style="padding:0.8rem 2rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;">Generate Story</button>
  +                <div id="story-output" style="margin-top:1rem;padding:1rem;border:1px solid var(--border);border-radius:8px;min-height:100px;"></div>
  +            </div>
  +        </div>
  +        <script>
  +        async function generateStory() {
  +            const t = document.getElementById('story-topic').value;
  +            const c = document.getElementById('story-chapter').value;
  +            const out = document.getElementById('story-output');
  +            out.innerHTML = '<em>Generating story...</em>';
  +            try {
  +                const resp = await fetch('/api/ai/story?topic='+encodeURIComponent(t)+'&chapter='+encodeURIComponent(c));
  +                const data = await resp.json();
  +                out.innerHTML = data.story || data.html || '<em>No story generated</em>';
  +            } catch(e) {
  +                out.innerHTML = '<em>Error: ' + e.message + '</em>';
  +            }
  +        }
  +        </script>"""
  +    )
  +
  +
  +@app.get("/ai/pomelli", response_class=HTMLResponse)
  +async def ai_pomelli():
  +    return _render(
  +        title="Pomelli Interactive Math ΓÇö AI Study Companion",
  +        content="""
  +        <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> <a href="/ai">AI Studio</a> <span class="sep">ΓÇ║</span> Pomelli Math</div>
  +        <div class="section">
  +            <h2>≡ƒôÉ Pomelli Interactive Math</h2>
  +            <p class="subtitle">Interactive math visualizations ΓÇö graphs, geometry, fractions, and more</p>
  +            <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +                <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Template</label>
  +                <select id="pomelli-template" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +                    <option value="graph-linear">Linear Graph</option>
  +                    <option value="graph-quadratic">Quadratic Graph</option>
  +                    <option value="graph-trig">Trigonometric Graph</option>
  +                    <option value="geometry-transform">Geometry Transform</option>
  +                    <option value="fractions">Fractions</option>
  +                    <option value="pythagoras">Pythagoras Theorem</option>
  +                    <option value="number-line">Number Line</option>
  +                    <option value="probability">Probability</option>
  +                    <option value="statistics">Statistics</option>
  +                    <option value="area-perimeter">Area & Perimeter</option>
  +                </select>
  +                <button onclick="loadPomelli()" class="btn-primary" style="padding:0.8rem 2rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;margin-top:1rem;">Load Interactive</button>
  +                <div id="pomelli-output" style="margin-top:1rem;padding:1rem;border:1px solid var(--border);border-radius:8px;min-height:200px;"></div>
  +            </div>
  +        </div>
  +        <script>
  +        async function loadPomelli() {
  +            const tpl = document.getElementById('pomelli-template').value;
  +            const out = document.getElementById('pomelli-output');
  +            out.innerHTML = '<em>Loading...</em>';
  +            try {
  +                const resp = await fetch('/api/ai/pomelli?template='+encodeURIComponent(tpl));
  +                const data = await resp.json();
  +                out.innerHTML = data.html || '<em>No content generated</em>';
  +            } catch(e) {
  +                out.innerHTML = '<em>Error: ' + e.message + '</em>';
  +            }
  +        }
  +        </script>"""
  +    )
  +
  +
  +@app.get("/ai/metai", response_class=HTMLResponse)
  +async def ai_metai():
  +    return _render(
  +        title="MetaAI Learning ΓÇö AI Study Companion",
  +        content="""
  +        <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> <a href="/ai">AI Studio</a> <span class="sep">ΓÇ║</span> MetaAI</div>
  +        <div class="section">
  +            <h2>≡ƒñû MetaAI Learning</h2>
  +            <p class="subtitle">Contextual learning powered by MetaAI ΓÇö explanations, storyboards, and learning guides</p>
  +            <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +                <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Concept</label>
  +                <input type="text" id="metai-concept" value="Photosynthesis" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +                <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Style</label>
  +                <select id="metai-style" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +                    <option value="explainer">Explainer</option>
  +                    <option value="storyboard">Storyboard</option>
  +                    <option value="qa">Q&A</option>
  +                    <option value="summary">Summary</option>
  +                </select>
  +                <button onclick="generateMetai()" class="btn-primary" style="padding:0.8rem 2rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;">Generate</button>
  +                <div id="metai-output" style="margin-top:1rem;padding:1rem;border:1px solid var(--border);border-radius:8px;min-height:100px;"></div>
  +            </div>
  +        </div>
  +        <script>
  +        async function generateMetai() {
  +            const c = document.getElementById('metai-concept').value;
  +            const s = document.getElementById('metai-style').value;
  +            const out = document.getElementById('metai-output');
  +            out.innerHTML = '<em>Generating...</em>';
  +            try {
  +                const resp = await fetch('/api/ai/metai?concept='+encodeURIComponent(c)+'&style='+encodeURIComponent(s));
  +                const data = await resp.json();
  +                out.innerHTML = data.html || data.content || '<em>No content generated</em>';
  +            } catch(e) {
  +                out.innerHTML = '<em>Error: ' + e.message + '</em>';
  +            }
  +        }
  +        </script>"""
  +    )
  +
  +
  +@app.get("/ai/opengrok", response_class=HTMLResponse)
  +async def ai_opengrok():
  +    return _render(
  +        title="OpenGrok Search ΓÇö AI Study Companion",
  +        content="""
  +        <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> <a href="/ai">AI Studio</a> <span class="sep">ΓÇ║</span> OpenGrok</div>
  +        <div class="section">
  +            <h2>≡ƒöì OpenGrok Formula & Theorem Search</h2>
  +            <p class="subtitle">Search formulas, theorems, and code across the CBSE curriculum</p>
  +            <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +                <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Search Query</label>
  +                <input type="text" id="og-query" value="quadratic equation" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +                <button onclick="searchOpenGrok()" class="btn-primary" style="padding:0.8rem 2rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;">Search</button>
  +                <div id="og-output" style="margin-top:1rem;padding:1rem;border:1px solid var(--border);border-radius:8px;min-height:100px;"></div>
  +            </div>
  +        </div>
  +        <script>
  +        async function searchOpenGrok() {
  +            const q = document.getElementById('og-query').value;
  +            const out = document.getElementById('og-output');
  +            out.innerHTML = '<em>Searching...</em>';
  +            try {
  +                const resp = await fetch('/api/ai/opengrok?query='+encodeURIComponent(q));
  +                const data = await resp.json();
  +                out.innerHTML = data.html || JSON.stringify(data.results || data, null, 2) || '<em>No results found</em>';
  +            } catch(e) {
  +                out.innerHTML = '<em>Error: ' + e.message + '</em>';
  +            }
  +        }
  +        </script>"""
  +    )
  +
  +
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +# MISSING BRIDGE PAGES (replacing legacy catch-all)
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +
  +
  +@app.get("/about", response_class=HTMLResponse)
  +async def about_page():
  +    return HTMLResponse(_render(title="About ΓÇö AI Study Companion", content="""
  +    <div class="section">
  +        <h2>≡ƒôû About AI Study Companion</h2>
  +        <p style="color:#666;margin-bottom:1rem;">AI-powered learning platform for CBSE, AP Board, and TS Board Class VΓÇôX students.</p>
  +        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1rem;">
  +            <div class="book-section"><h3>≡ƒôÜ Multi-Board Support</h3><p>CBSE ┬╖ AP Board ┬╖ Telangana Board ΓÇö complete syllabus coverage.</p></div>
  +            <div class="book-section"><h3>≡ƒñû AI-Powered Tools</h3><p>Mistral AI & Gemini: diagram generation, presentations, voiceovers, research, and more.</p></div>
  +            <div class="book-section"><h3>≡ƒÄ» Interactive Learning</h3><p>Quizzes, mind maps, interactive cards, matching games for every topic.</p></div>
  +            <div class="book-section"><h3>≡ƒÅå Gamification</h3><p>XP, levels, streaks, and achievements to keep you motivated.</p></div>
  +            <div class="book-section"><h3>≡ƒîÉ Multi-Lingual</h3><p>English ┬╖ αñ╣αñ┐αñ¿αÑìαñªαÑÇ ┬╖ α░ñα▒åα░▓α▒üα░ùα▒ü ┬╖ α«ñα««α«┐α«┤α»ì ┬╖ α▓òα▓¿α│ìα▓¿α▓í ┬╖ αª¼αª╛αªéαª▓αª╛ ┬╖ α┤«α┤▓α┤»α┤╛α┤│α┤é ΓÇö learn in your preferred medium.</p></div>
  +            <div class="book-section"><h3>≡ƒôè Progress Tracking</h3><p>Personalized learning paths, revision notes, and mock exams.</p></div>
  +        </div>
  +    </div>"""))
  +
  +
  +@app.get("/exams", response_class=HTMLResponse)
  +async def exams_page():
  +    conn = DB
  +    rows = ""
  +    if conn and conn.table_exists("subjects"):
  +        subjects = conn.query("SELECT id, name, board_id FROM subjects ORDER BY board_id, name")
  +        for s in subjects:
  +            chs = conn.query("SELECT id, num, title FROM chapters WHERE subject_id = ? ORDER BY num LIMIT 5", (s["id"],))
  +            ch_links = "".join(f'<li><a href="/chapter/{ch["id"]}">Ch {ch["num"]}: {ch["title"]}</a></li>' for ch in chs)
  +            if ch_links:
  +                rows += f'<div class="book-section"><h3><a href="/board/{s["board_id"]}/{s["id"]}">{s["name"]}</a></h3><ul>{ch_links}</ul><p style="margin-top:0.3rem;"><a href="/quiz/{s["id"]}" class="tts-btn" style="font-size:0.78rem;">Take Mock Exam</a></p></div>'
  +    if not rows:
  +        rows = '<p style="text-align:center;padding:2rem;color:#666;">No exams available yet.</p>'
  +    return HTMLResponse(_render(title="Mock Exams ΓÇö AI Study Companion", content=f"""
  +    <div class="breadcrumb">{_build_breadcrumb([("Home", "/"), ("Mock Exams", None)])}</div>
  +    <div class="section"><h2>≡ƒÅå Mock Exams</h2><p style="color:#666;margin-bottom:1rem;">Practice with chapter-wise mock exams. Track your progress and improve.</p>{rows}</div>"""))
  +
  +
  +@app.get("/ai", response_class=HTMLResponse)
  +async def ai_studio_hub():
  +    return HTMLResponse(_render(title="AI Studio ΓÇö AI Study Companion", content="""
  +    <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> AI Studio</div>
  +    <div class="section"><h2>≡ƒñû AI Studio</h2>
  +    <p style="color:#666;margin-bottom:1rem;">AI-powered learning tools powered by Mistral AI & Gemini.</p>
  +    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:0.8rem;">
  +        <a href="/ai/diagram" class="book-section" style="text-decoration:none;display:block;"><h3>≡ƒôÉ Diagram Generator</h3><p style="font-size:0.85rem;color:#666;">Flowcharts, mind maps, concept maps</p></a>
  +        <a href="/ai/presentation" class="book-section" style="text-decoration:none;display:block;"><h3>≡ƒô╜∩╕Å Presentations</h3><p style="font-size:0.85rem;color:#666;">HTML slide decks for any topic</p></a>
  +        <a href="/ai/story" class="book-section" style="text-decoration:none;display:block;"><h3>≡ƒôû Story Generator</h3><p style="font-size:0.85rem;color:#666;">Educational stories & analogies</p></a>
  +        <a href="/ai/voiceover" class="book-section" style="text-decoration:none;display:block;"><h3>≡ƒÄñ Voiceover</h3><p style="font-size:0.85rem;color:#666;">Text-to-speech in Indian languages</p></a>
  +        <a href="/ai/music" class="book-section" style="text-decoration:none;display:block;"><h3>≡ƒÄ╡ Study Music</h3><p style="font-size:0.85rem;color:#666;">Ambient focus & study music</p></a>
  +        <a href="/ai/research" class="book-section" style="text-decoration:none;display:block;"><h3>≡ƒö¼ Research Assistant</h3><p style="font-size:0.85rem;color:#666;">Deep topic research & analysis</p></a>
  +        <a href="/ai/literature" class="book-section" style="text-decoration:none;display:block;"><h3>≡ƒôÜ Literature Review</h3><p style="font-size:0.85rem;color:#666;">Research paper summaries</p></a>
  +        <a href="/ai/visualize" class="book-section" style="text-decoration:none;display:block;"><h3>≡ƒæü∩╕Å SVG Visualizer</h3><p style="font-size:0.85rem;color:#666;">Concept ΓåÆ SVG diagrams</p></a>
  +        <a href="/ai/pomelli" class="book-section" style="text-decoration:none;display:block;"><h3>≡ƒôÉ Pomelli Math</h3><p style="font-size:0.85rem;color:#666;">Interactive math visualizations</p></a>
  +        <a href="/ai/metai" class="book-section" style="text-decoration:none;display:block;"><h3>≡ƒñû MetaAI Learning</h3><p style="font-size:0.85rem;color:#666;">Storyboards & learning guides</p></a>
  +        <a href="/ai/metai" class="book-section" style="text-decoration:none;display:block;"><h3>≡ƒñû MetaAI Learning</h3><p style="font-size:0.85rem;color:#666;">Storyboards & learning guides</p></a>
  +        <a href="/ai/youtube" class="book-section" style="text-decoration:none;display:block;"><h3>≡ƒÄ¼ Concept Storyboards</h3><p style="font-size:0.85rem;color:#666;">Offline animated visual lessons</p></a>
  +        <a href="/ai/opengrok" class="book-section" style="text-decoration:none;display:block;"><h3>≡ƒôÉ Formulas & Theorems</h3><p style="font-size:0.85rem;color:#666;">Math & science formula search</p></a>
  +    </div></div>"""))
  +
  +
  +@app.get("/ai/youtube", response_class=HTMLResponse)
  +async def ai_youtube_page():
  +    return HTMLResponse(_render(title="AI Concept Storyboard Studio ΓÇö AI Study Companion", content="""
  +    <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> <a href="/ai">AI Studio</a> <span class="sep">ΓÇ║</span> Concept Storyboards</div>
  +    <div class="section">
  +        <h2>≡ƒÄ¼ AI Concept Storyboard Studio</h2>
  +        <p class="subtitle">Search and generate offline-first concept storyboards grounded in local textbook databases</p>
  +        <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +            <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Concept Topic</label>
  +            <input type="text" id="yt-topic" value="Photosynthesis" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +            <button onclick="searchYouTube()" class="btn-primary" style="padding:0.8rem 2rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;">≡ƒÄ¼ Generate Storyboards</button>
  +            <div id="yt-output" style="margin-top:1rem;"></div>
  +        </div>
  +    </div>
  +    <div class="section">
  +        <h2>≡ƒÄ₧∩╕Å Iterative Short-Clip Visual Script Generator</h2>
  +        <p class="subtitle">Convert a long topic into sequential short scenes with narration and layout scripts</p>
  +        <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +            <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Topic Name</label>
  +            <input type="text" id="yt-clip-topic" value="Quadratic Equations" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:0.5rem;">
  +            <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
  +                <input type="text" id="yt-clip-chapter" placeholder="Chapter ID (optional)" style="flex:1;min-width:120px;padding:0.7rem;border:1px solid var(--border);border-radius:8px;">
  +                <input type="number" id="yt-clip-count" value="5" min="2" max="20" style="width:80px;padding:0.7rem;border:1px solid var(--border);border-radius:8px;">
  +                <button onclick="generateClips()" class="btn-primary" style="padding:0.8rem 2rem;background:var(--accent);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;">≡ƒÄ¼ Generate Scene Playlist</button>
  +            </div>
  +            <div id="yt-clip-output" style="margin-top:1rem;"></div>
  +        </div>
  +    </div>
  +    <script>
  +    async function searchYouTube() {
  +        const topic = document.getElementById('yt-topic').value;
  +        const out = document.getElementById('yt-output');
  +        out.innerHTML = '<em>Generating concept storyboards...</em>';
  +        try {
  +            const resp = await fetch('/api/ai/youtube?topic='+encodeURIComponent(topic));
  +            const data = await resp.json();
  +            out.innerHTML = data.html || '<em>No storyboards found</em>';
  +        } catch(e) {
  +            out.innerHTML = '<em>Error: ' + e.message + '</em>';
  +        }
  +    }
  +    async function generateClips() {
  +        const topic = document.getElementById('yt-clip-topic').value;
  +        const chapter = document.getElementById('yt-clip-chapter').value;
  +        const max = document.getElementById('yt-clip-count').value || 5;
  +        const out = document.getElementById('yt-clip-output');
  +        out.innerHTML = '<em>Generating visual scenes and scripts...</em>';
  +        try {
  +            let url = '/api/ai/youtube/generate?topic_name='+encodeURIComponent(topic)+'&max_clips='+max;
  +            if (chapter) url += '&chapter_id='+encodeURIComponent(chapter);
  +            const resp = await fetch(url);
  +            const data = await resp.json();
  +            if (!data.success) { out.innerHTML = '<em>Generation failed</em>'; return; }
  +            let h = '<div style="margin-top:0.5rem;"><h4 style="color:var(--accent);margin-bottom:0.3rem;">≡ƒÄ¼ Internal Video Script: '+data.topic+'</h4>';
  +            h += '<p style="font-size:0.8rem;color:#666;">'+data.total_clips+' scenes &middot; ~'+data.total_duration+'s total duration</p>';
  +            h += '<div style="display:flex;flex-direction:column;gap:1.2rem;margin-top:1rem;">';
  +            for (const c of data.clips) {
  +                h += '<div class="book-section" style="padding:1.2rem;border-left:4px solid '+c.color+';">';
  +                h += '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-bottom:0.8rem;">';
  +                h += '<strong style="font-size:1.1rem;">'+c.icon+' Scene '+c.index+': '+c.segment_title+'</strong>';
  +                h += '<span style="font-size:0.85rem;background:#f1f5f9;padding:0.2rem 0.6rem;border-radius:20px;color:#666;">~'+c.duration_sec+'s</span>';
  +                h += '</div>';
  +                h += '<div style="margin-bottom:0.8rem;padding:0.8rem;background:#fafafa;border-radius:6px;border:1px dashed #ddd;">';
  +                h += '<span style="font-size:0.75rem;text-transform:uppercase;color:#888;font-weight:700;display:block;margin-bottom:0.3rem;">Visual Layout Description</span>';
  +                h += '<p style="margin:0;font-size:0.9rem;color:#333;">'+c.visual_description+'</p>';
  +                h += '</div>';
  +                h += '<div style="margin-bottom:0.8rem;">';
  +                h += '<span style="font-size:0.75rem;text-transform:uppercase;color:#888;font-weight:700;display:block;margin-bottom:0.3rem;">Voiceover Script</span>';
  +                h += '<p style="margin:0;font-size:0.95rem;line-height:1.5;color:#111;">'+c.text+'</p>';
  +                h += '</div>';
  +                if (c.key_formula_or_term) {
  +                    h += '<div style="font-size:0.85rem;color:var(--primary);margin-top:0.5rem;font-weight:600;">≡ƒöæ Focus Formula/Term: <code style="background:#eef2ff;padding:0.1rem 0.4rem;border-radius:4px;">'+c.key_formula_or_term+'</code></div>';
  +                }
  +                h += '<div style="margin-top:1rem;display:flex;gap:0.5rem;">';
  +                h += '<button onclick="speakTextLocally(\''+c.text.replace(/'/g, "\\'")+'\')" style="padding:0.4rem 1rem;background:var(--primary);color:#fff;border:none;border-radius:6px;font-size:0.8rem;cursor:pointer;font-weight:600;">≡ƒöè Play Voiceover</button>';
  +                h += '</div>';
  +                h += '</div>';
  +            }
  +            h += '</div></div>';
  +            out.innerHTML = h;
  +        } catch(e) {
  +            out.innerHTML = '<em>Error: ' + e.message + '</em>';
  +        }
  +    }
  +    function speakTextLocally(text) {
  +        if (!('speechSynthesis' in window)) { alert('Text-to-speech not supported in this browser.'); return; }
  +        window.speechSynthesis.cancel();
  +        var utter = new SpeechSynthesisUtterance(text);
  +        utter.lang = 'en-IN';
  +        utter.pitch = 1.0;
  +        utter.rate = 1.0;
  +        window.speechSynthesis.speak(utter);
  +    }
  +    </script>"""))
  +
  +
  +@app.get("/ai/research", response_class=HTMLResponse)
  +async def ai_research_page():
  +    return HTMLResponse(_render(title="AI Research Assistant ΓÇö AI Study Companion", content="""
  +    <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> <a href="/ai">AI Studio</a> <span class="sep">ΓÇ║</span> Research</div>
  +    <div class="section">
  +        <h2>≡ƒö¼ AI Research Assistant</h2>
  +        <p class="subtitle">Deep research on any topic ΓÇö powered by Mistral AI</p>
  +        <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +            <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Research Query</label>
  +            <input type="text" id="res-query" value="Photosynthesis process" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +            <button onclick="doResearch()" class="btn-primary" style="padding:0.8rem 2rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;">Research</button>
  +            <div id="res-output" style="margin-top:1rem;padding:1rem;border:1px solid var(--border);border-radius:8px;min-height:80px;"></div>
  +        </div>
  +    </div>
  +    <script>
  +    async function doResearch() {
  +        const q = document.getElementById('res-query').value;
  +        const out = document.getElementById('res-output');
  +        out.innerHTML = '<em>Researching...</em>';
  +        try {
  +            const resp = await fetch('/api/ai/research?query='+encodeURIComponent(q));
  +            const data = await resp.json();
  +            out.innerHTML = '<div style="line-height:1.7;">' + data.answer.replace(/\\n/g, '<br>').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>') + '</div>';
  +        } catch(e) {
  +            out.innerHTML = '<em>Error: ' + e.message + '</em>';
  +        }
  +    }
  +    </script>"""))
  +
  +
  +@app.get("/ai/literature", response_class=HTMLResponse)
  +async def ai_literature_page():
  +    return HTMLResponse(_render(title="AI Literature Review ΓÇö AI Study Companion", content="""
  +    <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> <a href="/ai">AI Studio</a> <span class="sep">ΓÇ║</span> Literature</div>
  +    <div class="section">
  +        <h2>≡ƒôÜ AI Literature Review</h2>
  +        <p class="subtitle">Research paper summaries on any topic</p>
  +        <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +            <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Topic</label>
  +            <input type="text" id="lit-topic" value="Photosynthesis" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +            <button onclick="doLitReview()" class="btn-primary" style="padding:0.8rem 2rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;">Review</button>
  +            <div id="lit-output" style="margin-top:1rem;"></div>
  +        </div>
  +    </div>
  +    <script>
  +    async function doLitReview() {
  +        const q = document.getElementById('lit-topic').value;
  +        const out = document.getElementById('lit-output');
  +        out.innerHTML = '<em>Reviewing literature...</em>';
  +        try {
  +            const resp = await fetch('/api/ai/literature?query='+encodeURIComponent(q));
  +            const data = await resp.json();
  +            const papers = data.results || [];
  +            let html = '';
  +            papers.forEach(function(p) {
  +                html += '<div class="book-section" style="margin-bottom:0.5rem;"><h4 style="margin:0;">' + p.title + '</h4><p style="font-size:0.85rem;color:#666;margin:0.2rem 0;">' + (p.authors || '') + ' (' + (p.year || '') + ')</p><p style="font-size:0.9rem;margin:0.3rem 0 0;">' + (p.abstract || '') + '</p></div>';
  +            });
  +            out.innerHTML = html || '<em>No literature found</em>';
  +        } catch(e) {
  +            out.innerHTML = '<em>Error: ' + e.message + '</em>';
  +        }
  +    }
  +    </script>"""))
  +
  +
  +@app.get("/ai/visualize", response_class=HTMLResponse)
  +async def ai_visualize_page():
  +    return HTMLResponse(_render(title="AI SVG Visualizer ΓÇö AI Study Companion", content="""
  +    <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> <a href="/ai">AI Studio</a> <span class="sep">ΓÇ║</span> Visualizer</div>
  +    <div class="section">
  +        <h2>≡ƒæü∩╕Å AI SVG Visualizer</h2>
  +        <p class="subtitle">Generate SVG diagrams for any concept</p>
  +        <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +            <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Concept</label>
  +            <input type="text" id="vis-concept" value="Photosynthesis" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +            <button onclick="doVisualize()" class="btn-primary" style="padding:0.8rem 2rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;">Generate SVG</button>
  +            <div id="vis-output" style="margin-top:1rem;"></div>
  +        </div>
  +    </div>
  +    <script>
  +    async function doVisualize() {
  +        const c = document.getElementById('vis-concept').value;
  +        const out = document.getElementById('vis-output');
  +        out.innerHTML = '<em>Generating SVG...</em>';
  +        try {
  +            const resp = await fetch('/api/ai/visualize?concept='+encodeURIComponent(c));
  +            const data = await resp.json();
  +            out.innerHTML = data.svg ? '<div style="background:#fff;border-radius:8px;padding:1rem;">' + data.svg + '</div>' : '<em>No SVG generated</em>';
  +        } catch(e) {
  +            out.innerHTML = '<em>Error: ' + e.message + '</em>';
  +        }
  +    }
  +    </script>"""))
  +
  +
  +@app.get("/ai/pedagogical", response_class=HTMLResponse)
  +async def ai_pedagogical_page():
  +    return HTMLResponse(_render(title="NotebookLM Pedagogical Guide ΓÇö AI Study Companion", content="""
  +    <div class="breadcrumb"><a href="/">Home</a> <span class="sep">ΓÇ║</span> <a href="/ai">AI Studio</a> <span class="sep">ΓÇ║</span> Pedagogical Guide</div>
  +    <div class="section">
  +        <h2>≡ƒôû AI Pedagogical Guide</h2>
  +        <p class="subtitle">Detailed study guides with learning objectives, prerequisites, and practice questions</p>
  +        <div class="book-section" style="padding:1.5rem;margin-top:1rem;">
  +            <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Subject</label>
  +            <input type="text" id="ped-subject" value="Science" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +            <label style="font-weight:500;display:block;margin-bottom:0.5rem;">Topic</label>
  +            <input type="text" id="ped-topic" value="Photosynthesis" style="width:100%;padding:0.7rem;border:1px solid var(--border);border-radius:8px;margin-bottom:1rem;">
  +            <button onclick="doPedagogical()" class="btn-primary" style="padding:0.8rem 2rem;background:var(--primary);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;">Generate Guide</button>
  +            <div id="ped-output" style="margin-top:1rem;padding:1rem;border:1px solid var(--border);border-radius:8px;min-height:80px;"></div>
  +        </div>
  +    </div>
  +    <script>
  +    async function doPedagogical() {
  +        const s = document.getElementById('ped-subject').value;
  +        const t = document.getElementById('ped-topic').value;
  +        const out = document.getElementById('ped-output');
  +        out.innerHTML = '<em>Generating pedagogical guide...</em>';
  +        try {
  +            const resp = await fetch('/api/ai/notebooklm?subject='+encodeURIComponent(s)+'&chapter=General&topic='+encodeURIComponent(t));
  +            const data = await resp.json();
  +            out.innerHTML = '<div style="line-height:1.7;white-space:pre-wrap;font-family:monospace;font-size:0.85rem;">' + (data.markdown || '<em>No guide generated</em>') + '</div>';
  +        } catch(e) {
  +            out.innerHTML = '<em>Error: ' + e.message + '</em>';
  +        }
  +    }
  +    </script>"""))
  +
  +
  +@app.get("/sw.js", response_class=Response)
  +async def service_worker():
  +    sw_js = """self.addEventListener('install', function(e) { self.skipWaiting(); });
  +self.addEventListener('activate', function(e) { e.waitUntil(clients.claim()); });
  +self.addEventListener('fetch', function(e) {
  +    if (e.request.method === 'GET') {
  +        e.respondWith(
  +            fetch(e.request).then(function(resp) {
  +                if (resp.status === 200) {
  +                    var respClone = resp.clone();
  +                    caches.open('cbse-v1').then(function(cache) {
  +                        cache.put(e.request, respClone);
  +                    });
  +                }
  +                return resp;
  +            }).catch(function() {
  +                return caches.match(e.request);
  +            })
  +        );
  +    }
  +});"""
  +    return Response(content=sw_js, media_type="application/javascript")
  +
  +
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +# CONTENT ROUTES (notes, revision, quiz, mindmap, interactives)
  +# ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
  +
  +
  +@app.get("/notes/{chapter_id}", response_class=HTMLResponse)
  +async def notes_page(chapter_id: str):
  +    conn = DB
  +    chapter = conn.query_one("SELECT * FROM chapters WHERE id = ?", (chapter_id,)) if conn and conn.table_exists("chapters") else None
  +    if not chapter:
  +        return HTMLResponse(_render(title="Notes ΓÇö Not Found", content='<div class="section"><h2>Notes Not Found</h2><p><a href="/">Go Home</a></p></div>'), status_code=404)
  +    topics = conn.query("SELECT * FROM topics WHERE chapter_id = ? ORDER BY num, title", (chapter_id,))
  +    items = "".join(f'<li><strong>{t["title"]}</strong>: {t.get("content","")[:200]}...</li>' for t in topics)
  +    return HTMLResponse(_render(title=f"Notes: {chapter['title']}", content=f"""
  +    <div class="breadcrumb">{_build_breadcrumb([("Home", "/"), (f"Ch {chapter['num']}: {chapter['title']}", f"/chapter/{chapter_id}"), ("Notes", None)])}</div>
  +    <div class="section"><h2>≡ƒô¥ Revision Notes: {chapter['title']}</h2><ul style="line-height:1.8;">{items}</ul></div>"""))
  +
  +
  +@app.get("/revision/{chapter_id}", response_class=HTMLResponse)
  +async def revision_page(chapter_id: str):
  +    conn = DB
  +    chapter = conn.query_one("SELECT * FROM chapters WHERE id = ?", (chapter_id,)) if conn and conn.table_exists("chapters") else None
  +    if not chapter:
  +        return HTMLResponse(_render(title="Revision ΓÇö Not Found", content='<div class="section"><h2>Revision Not Found</h2><p><a href="/">Go Home</a></p></div>'), status_code=404)
  +    topics = conn.query("SELECT title, content FROM topics WHERE chapter_id = ? ORDER BY num, title", (chapter_id,))
  +    points = "".join(f'<li>Γ£ö {t["title"]}: {t.get("content","")[:150]}</li>' for t in topics)
  +    return HTMLResponse(_render(title=f"Revision: {chapter['title']}", content=f"""
  +    <div class="breadcrumb">{_build_breadcrumb([("Home", "/"), (f"Ch {chapter['num']}: {chapter['title']}", f"/chapter/{chapter_id}"), ("Revision", None)])}</div>
  +    <div class="section"><h2>≡ƒöä Quick Revision: {chapter['title']}</h2><ul style="line-height:1.8;">{points}</ul></div>"""))
  +
  +
  +@app.get("/quiz/{entity_id}", response_class=HTMLResponse)
  +async def quiz_page(entity_id: str):
  +    conn = DB
  +    # Try as chapter_id first
  +    chapter = conn.query_one("SELECT * FROM chapters WHERE id = ?", (entity_id,)) if conn and conn.table_exists("chapters") else None
  +    if not chapter:
  +        # Try as subject_id ΓÇö list all chapter quizzes
  +        subject = conn.query_one("SELECT * FROM subjects WHERE id = ?", (entity_id,)) if conn and conn.table_exists("subjects") else None
  +        if subject:
  +            chapters = conn.query("SELECT * FROM chapters WHERE subject_id = ? ORDER BY num", (entity_id,))
  +            quiz_links = ""
  +            for ch in chapters:
  +                quiz_links += f'<div class="book-section" style="margin-bottom:0.5rem;"><a href="/quiz/{ch["id"]}" style="text-decoration:none;display:flex;justify-content:space-between;align-items:center;"><span>Ch {ch["num"]}: {ch["title"]}</span><span style="font-size:0.8rem;color:var(--accent);">≡ƒô¥ Quiz ΓåÆ</span></a></div>'
  +            if not quiz_links:
  +                quiz_links = '<p style="color:#666;">No chapters available for quizzes yet.</p>'
  +            return HTMLResponse(_render(title=f"Quizzes: {subject['name']}", content=f"""
  +            <div class="breadcrumb">{_build_breadcrumb([("Home", "/"), (f"{subject['name']}", f"/board/{subject['board_id']}/{entity_id}"), ("Quizzes", None)])}</div>
  +            <div class="section"><h2>≡ƒô¥ Practice Quizzes: {subject['name']}</h2><p style="color:#666;margin-bottom:1rem;">Select a chapter to practice.</p>{quiz_links}</div>"""))
  +        return HTMLResponse(_render(title="Quiz ΓÇö Not Found", content='<div class="section"><h2>Quiz Not Found</h2><p><a href="/">Go Home</a></p></div>'), status_code=404)
  +    chapter_id = entity_id
  +    problems = conn.query("SELECT * FROM problems WHERE chapter_id = ? LIMIT 20", (chapter_id,)) if conn.table_exists("problems") else []
  +    cards = ""
  +    for p in problems:
  +        qtext = p.get("problem_text", "")[:200]
  +        atext = p.get("solution_text", "")[:150]
  +        cards += f'<div class="book-section" style="margin-bottom:0.5rem;"><h4 style="margin:0;">Q: {qtext}</h4><p style="color:#2ecc71;font-size:0.85rem;margin:0.3rem 0 0;">Answer: {atext}</p></div>'
  +    if not cards:
  +        cards = '<p style="color:#666;">No practice problems for this chapter yet.</p>'
  +    return HTMLResponse(_render(title=f"Quiz: {chapter['title']}", content=f"""
  +    <div class="breadcrumb">{_build_breadcrumb([("Home", "/"), (f"Ch {chapter['num']}: {chapter['title']}", f"/chapter/{chapter_id}"), ("Quiz", None)])}</div>
  +    <div class="section"><h2>≡ƒô¥ Practice Quiz: {chapter['title']}</h2><p style="color:#666;margin-bottom:1rem;">Test your knowledge with these practice problems.</p>{cards}</div>"""))
  +
  +
  +@app.get("/mindmap/{topic_id}", response_class=HTMLResponse)
  +async def mindmap_page(topic_id: str):
  +    conn = DB
  +    topic = conn.query_one("SELECT * FROM topics WHERE id = ?", (topic_id,)) if conn and conn.table_exists("topics") else None
  +    if not topic:
  +        return HTMLResponse(_render(title="Mind Map ΓÇö Not Found", content='<div class="section"><h2>Mind Map Not Found</h2><p><a href="/">Go Home</a></p></div>'), status_code=404)
  +    
  +    import asyncio
  +    res_mm, res_fc, res_cm = await asyncio.gather(
  +        _run_in_thread(ai_services.napkin_diagram, topic["title"], "mindmap"),
  +        _run_in_thread(ai_services.napkin_diagram, topic["title"], "flowchart"),
  +        _run_in_thread(ai_services.napkin_diagram, topic["title"], "concept-map")
  +    )
  +    
  +    veo_html = ai_services.get_fallback_veo_animator(topic["title"])
  +
  +    content = f"""
  +    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
  +    <script>
  +        mermaid.initialize({{ startOnLoad: true, theme: 'neutral', securityLevel: 'loose' }});
  +        function switchDiagTab(tab) {{
  +            document.querySelectorAll('.diag-tab-content').forEach(c => c.style.display = 'none');
  +            document.querySelectorAll('.diag-tab-btn').forEach(b => b.classList.remove('active'));
  +            document.getElementById('diag-tab-' + tab).style.display = 'block';
  +            event.currentTarget.classList.add('active');
  +        }}
  +    </script>
  +    <style>
  +        .diag-explanation {{
  +            margin-top: 1rem;
  +            padding: 1rem;
  +            border-radius: 8px;
  +            background: #f8fafc;
  +            border-left: 4px solid var(--primary);
  +            font-size: 0.95rem;
  +            color: #475569;
  +        }}
  +        .concept-badge {{
  +            display: inline-block;
  +            padding: 0.25rem 0.5rem;
  +            font-size: 0.75rem;
  +            font-weight: 600;
  +            border-radius: 4px;
  +            margin-bottom: 0.5rem;
  +        }}
  +    </style>
  +    <div class="breadcrumb">{_build_breadcrumb([("Home", "/"), (topic['title'], f"/topic/{topic_id}"), ("Visualizations", None)])}</div>
  +    <div class="section">
  +        <h2>≡ƒºá Interactive Concept Visualizer: {htmlmod.escape(topic['title'])}</h2>
  +        <p class="subtitle" style="color:#666; margin-bottom:1.5rem;">Explore customized representations of this concept tailored for different learning modes.</p>
  +        
  +        <div class="math-tabs">
  +            <button class="math-tab-btn active diag-tab-btn" onclick="switchDiagTab('mindmap')">≡ƒù║∩╕Å 1. Radial Mind Map (Dot Connectors)</button>
  +            <button class="math-tab-btn diag-tab-btn" onclick="switchDiagTab('flowchart')">≡ƒôÉ 2. Process Flowchart (Step Outcomes)</button>
  +            <button class="math-tab-btn diag-tab-btn" onclick="switchDiagTab('conceptmap')">≡ƒöù 3. Relation Map & Video (Detailed Visuals)</button>
  +        </div>
  +        
  +        <div id="diag-tab-mindmap" class="diag-tab-content" style="margin-top:1.5rem; display:block;">
  +            <span class="concept-badge" style="background:#e0f2fe; color:#0369a1;">MIND MAP CONCEPT</span>
  +            <div class="diag-explanation">
  +                <strong>Mind Map focus: Connecting the concepts and filling knowledge gaps.</strong> Radial diagrams allow you to map associations outwards, connecting new definitions back to the core concept root.
  +            </div>
  +            <div class="mermaid-card" style="background:#fff; padding:1.5rem; border-radius:12px; border:1px solid var(--border); box-shadow:0 4px 12px rgba(0,0,0,0.03); text-align:center; margin-top:1rem;">
  +                <pre class="mermaid" style="background:none; border:none; margin:0; padding:0; overflow-x:auto;">{res_mm.get("diagram", "")}</pre>
  +            </div>
  +            <div class="study-guide-card" style="background:#fff; padding:1.5rem; border-radius:12px; border:1px solid var(--border); box-shadow:0 4px 12px rgba(0,0,0,0.03); text-align:left; margin-top:1.5rem;">
  +                <h3 style="color:var(--primary); margin-top:0; border-bottom:1px solid var(--border); padding-bottom:0.5rem;">≡ƒôû Dot-Connection & Association Guide</h3>
  +                <div style="font-size:0.95rem; line-height:1.6; color:#333;">{res_mm.get("explanation", "")}</div>
  +            </div>
  +        </div>
  +
  +        <div id="diag-tab-flowchart" class="diag-tab-content" style="margin-top:1.5rem; display:none;">
  +            <span class="concept-badge" style="background:#fef3c7; color:#b45309;">PROCESS FLOWCHART</span>
  +            <div class="diag-explanation">
  +                <strong>Flowchart focus: Step-by-step outcomes.</strong> Follow the directional processes below to see what output is produced by each step.
  +            </div>
  +            <div class="mermaid-card" style="background:#fff; padding:1.5rem; border-radius:12px; border:1px solid var(--border); box-shadow:0 4px 12px rgba(0,0,0,0.03); text-align:center; margin-top:1rem;">
  +                <pre class="mermaid" style="background:none; border:none; margin:0; padding:0; overflow-x:auto;">{res_fc.get("diagram", "")}</pre>
  +            </div>
  +            <div class="study-guide-card" style="background:#fff; padding:1.5rem; border-radius:12px; border:1px solid var(--border); box-shadow:0 4px 12px rgba(0,0,0,0.03); text-align:left; margin-top:1.5rem;">
  +                <h3 style="color:var(--primary); margin-top:0; border-bottom:1px solid var(--border); padding-bottom:0.5rem;">≡ƒôû Sequential Process & Outcomes Guide</h3>
  +                <div style="font-size:0.95rem; line-height:1.6; color:#333;">{res_fc.get("explanation", "")}</div>
  +            </div>
  +        </div>
  +
  +        <div id="diag-tab-conceptmap" class="diag-tab-content" style="margin-top:1.5rem; display:none;">
  +            <span class="concept-badge" style="background:#dcfce7; color:#15803d;">RELATION MAP & VIDEO</span>
  +            <div class="diag-explanation">
  +                <strong>Relation Map focus: High fidelity structural connections.</strong> Cross-link multiple sub-concepts with clear connecting verbs, accompanied by a dynamic Google Veo video concept simulator below.
  +            </div>
  +            <div class="mermaid-card" style="background:#fff; padding:1.5rem; border-radius:12px; border:1px solid var(--border); box-shadow:0 4px 12px rgba(0,0,0,0.03); text-align:center; margin-top:1rem;">
  +                <pre class="mermaid" style="background:none; border:none; margin:0; padding:0; overflow-x:auto;">{res_cm.get("diagram", "")}</pre>
  +            </div>
  +            
  +            <div style="margin-top:2rem;">
  +                {veo_html}
  +            </div>
  +
  +            <div class="study-guide-card" style="background:#fff; padding:1.5rem; border-radius:12px; border:1px solid var(--border); box-shadow:0 4px 12px rgba(0,0,0,0.03); text-align:left; margin-top:1.5rem;">
  +                <h3 style="color:var(--primary); margin-top:0; border-bottom:1px solid var(--border); padding-bottom:0.5rem;">≡ƒôû Detailed Concept Relation Guide</h3>
  +                <div style="font-size:0.95rem; line-height:1.6; color:#333;">{res_cm.get("explanation", "")}</div>
  +            </div>
  +        </div>
  +    </div>
  +    """
  +    return HTMLResponse(_render(title=f"Diagrams: {topic['title']}", content=content))
  +
  +
  +@app.get("/interactives/cards/{topic_id}", response_class=HTMLResponse)
  +async def interactives_cards_page(topic_id: str):
  +    conn = DB
  +    topic = conn.query_one("SELECT * FROM topics WHERE id = ?", (topic_id,)) if conn and conn.table_exists("topics") else None
  +    if not topic:
  +        return HTMLResponse(_render(title="Flash Cards ΓÇö Not Found", content='<div class="section"><h2>Flash Cards Not Found</h2><p><a href="/">Go Home</a></p></div>'), status_code=404)
  +    chunks = conn.query("SELECT * FROM chunks WHERE topic_id = ? ORDER BY seq", (topic_id,))
  +    cards_html = ""
  +    for c in chunks:
  +        title = c.get("title", "") or c.get("content", "")[:40]
  +        content = c.get("content", "")
  +        cards_html += f'<div class="book-section" style="cursor:pointer;margin-bottom:0.5rem;" onclick="this.querySelector(\'.card-content\').style.display=this.querySelector(\'.card-content\').style.display===\'none\'?\'block\':\'none\'"><h4 style="margin:0;">≡ƒôç {title}</h4><div class="card-content" style="display:none;margin-top:0.5rem;padding:0.8rem;background:#f8f9ff;border-radius:6px;">{content}</div></div>'
  +    if not cards_html:
  +        cards_html = '<p style="color:#666;">No flash cards for this topic yet.</p>'
  +    return HTMLResponse(_render(title=f"Flash Cards: {topic['title']}", content=f"""
  +    <div class="breadcrumb">{_build_breadcrumb([("Home", "/"), (topic['title'], f"/topic/{topic_id}"), ("Flash Cards", None)])}</div>
  +    <div class="section"><h2>≡ƒâÅ Flash Cards: {topic['title']}</h2><p style="color:#666;margin-bottom:1rem;">Click a card to flip it.</p>{cards_html}</div>
  +    <script>document.querySelectorAll('.book-section h4').forEach(function(el,i){{el.textContent = '≡ƒôç Card '+(i+1)+': '+el.textContent.replace('≡ƒôç ','');}});</script>"""))
  +
  +
  +@app.get("/interactives/matching/{entity_id}", response_class=HTMLResponse)
  +async def interactives_matching_page(entity_id: str):
  +    conn = DB
  +    if not conn or not conn.table_exists("chapters"):
  +        return HTMLResponse(_render(title="Matching ΓÇö Not Found", content='<div class="section"><h2>Matching Game Not Found</h2><p><a href="/">Go Home</a></p></div>'), status_code=404)
  +    # Accept either chapter_id or topic_id
  +    chapter = conn.query_one("SELECT * FROM chapters WHERE id = ?", (entity_id,))
  +    if not chapter:
  +        topic = conn.query_one("SELECT * FROM topics WHERE id = ?", (entity_id,))
  +        if topic:
  +            chapter = conn.query_one("SELECT * FROM chapters WHERE id = ?", (topic["chapter_id"],))
  +    if not chapter:
  +        return HTMLResponse(_render(title="Matching ΓÇö Not Found", content='<div class="section"><h2>Matching Game Not Found</h2><p><a href="/">Go Home</a></p></div>'), status_code=404)
  +    chapter_id = chapter["id"]
  +    topics = conn.query("SELECT id, title, content FROM topics WHERE chapter_id = ? ORDER BY RANDOM() LIMIT 12", (chapter_id,))
  +    if len(topics) < 4:
  +        topics = conn.query("SELECT id, title, content FROM topics WHERE chapter_id = ? LIMIT 12", (chapter_id,))
  +    left = "".join(f'<div class="match-item" data-id="{t["id"]}" style="padding:0.5rem 0.8rem;background:#e8f4f8;border-radius:6px;cursor:pointer;margin:0.2rem;text-align:center;font-size:0.85rem;font-weight:500;">{t["title"]}</div>' for t in topics)
  +    right = "".join(f'<div class="match-item" data-id="{t["id"]}" style="padding:0.5rem 0.8rem;background:#fef9c3;border-radius:6px;cursor:pointer;margin:0.2rem;text-align:center;font-size:0.85rem;">{t.get("content","")[:80]}</div>' for t in topics)
  +    return HTMLResponse(_render(title=f"Matching: {chapter['title']}", content=f"""
  +    <div class="breadcrumb">{_build_breadcrumb([("Home", "/"), (f"Ch {chapter['num']}: {chapter['title']}", f"/chapter/{chapter_id}"), ("Matching Game", None)])}</div>
  +    <div class="section"><h2>≡ƒöù Matching Game: {chapter['title']}</h2><p style="color:#666;margin-bottom:1rem;">Match topics with their descriptions.</p>
  +    <div style="display:flex;gap:2rem;flex-wrap:wrap;">
  +        <div style="flex:1;min-width:200px;"><h4 style="font-size:0.9rem;">Topics</h4><div id="match-left">{left}</div></div>
  +        <div style="flex:1;min-width:200px;"><h4 style="font-size:0.9rem;">Descriptions</h4><div id="match-right">{right}</div></div>
  +    </div>
  +    <p id="match-status" style="margin-top:1rem;font-weight:600;"></p></div>
  +    <script>
  +    (function(){{
  +        var sel = null;
  +        function checkMatch() {{
  +            var matched = 0; var total = document.querySelectorAll('#match-left .match-item').length;
  +            document.querySelectorAll('#match-left .match-item').forEach(function(l,i){{
  +                var r = document.querySelector('#match-right .match-item[data-id="'+l.dataset.id+'"]');
  +                if(l.style.opacity==='0.4' && r.style.opacity==='0.4') matched++;
  +            }});
  +            document.getElementById('match-status').textContent = matched + ' / ' + total + ' matched';
  +            if(matched===total) document.getElementById('match-status').textContent = '≡ƒÄë All matched! Perfect!';
  +        }}
  +        document.querySelectorAll('#match-left .match-item').forEach(function(el){{
  +            el.addEventListener('click',function(){{
  +                if(this.style.opacity==='0.4') return;
  +                if(sel){{sel.style.outline='none';}}
  +                sel=this; this.style.outline='3px solid #4a90d9';
  +            }});
  +        }});
  +        document.querySelectorAll('#match-right .match-item').forEach(function(el){{
  +            el.addEventListener('click',function(){{
  +                if(!sel || this.style.opacity==='0.4') return;
  +                if(sel.dataset.id===this.dataset.id){{
  +                    sel.style.opacity='0.4'; this.style.opacity='0.4';
  +                    sel.style.outline='none'; sel=null;
  +                    checkMatch();
  +                }} else {{
  +                    this.style.background='#fee2e2';
  +                    setTimeout(function(){{el.style.background='#fef9c3';}},500);
  +                }}
  +            }});
  +        }});
  +    }})();
  +    </script>"""))
  +
  +
  +def _pomelli_mindmap_svg(nodes):
  +    """Generate an SVG mind map visualization using PomelliAI-style rendering."""
  +    if not nodes:
  +        return '<p style="color:#666;">No nodes for mind map.</p>'
  +    center = nodes[0]
  +    children = nodes[1:]
  +    if len(children) > 10:
  +        children = children[:10]
  +    svg_w, svg_h = 700, max(300, len(children) * 50 + 100)
  +    cx, cy = 100, svg_h // 2
  +    items = ""
  +    colors = ["#4a90d9", "#2ecc71", "#9b59b6", "#e74c3c", "#f39c12", "#1abc9c", "#e67e22", "#3498db", "#2c3e50", "#8e44ad"]
  +    angle_step = min(60, 320 // max(1, len(children)))
  +    start_angle = 180 - (len(children) - 1) * angle_step / 2
  +    for i, node in enumerate(children):
  +        angle = (start_angle + i * angle_step) * 3.14159 / 180
  +        r = 220
  +        nx = cx + r * 0.8
  +        ny = 40 + i * (svg_h - 80) // max(1, len(children))
  +        color = colors[i % len(colors)]
  +        node_text = node[:50].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
  +        items += f'<line x1="{cx+15}" y1="{cy}" x2="{nx}" y2="{ny}" stroke="{color}" stroke-width="1.5" opacity="0.5"/><circle cx="{nx}" cy="{ny}" r="6" fill="{color}" opacity="0.8"/><text x="{nx+12}" y="{ny+4}" font-size="12" fill="#333">{node_text}</text>'
  +    escaped_center = center[:40].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
  +    svg = f'<svg viewBox="0 0 {svg_w} {svg_h}" style="width:100%;max-width:{svg_w}px;height:auto;" xmlns="http://www.w3.org/2000/svg"><rect width="{svg_w}" height="{svg_h}" fill="#f8f9fa" rx="12"/><circle cx="{cx}" cy="{cy}" r="30" fill="#4a90d9" opacity="0.15"/><circle cx="{cx}" cy="{cy}" r="20" fill="#4a90d9" opacity="0.25"/><text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="11" font-weight="600" fill="#1a1a2e">{escaped_center}</text>{items}</svg>'
  +    return svg
  +
  +
  +@app.get("/api/search")
  +@rate_limit(60)
  +async def api_search(request: Request, q: str = Query(""), board: Optional[str] = None, limit: int = Query(15, le=50)):
  +    if not q:
  +        return {"results": []}
  +    try:
  +        idx = get_index()
  +        results = idx.search(q, board=board, limit=limit)
  +    except Exception:
  +        results = []
  +    return {"results": results}
  +
  +
  +@app.get("/api/gamification")
  +async def api_gamification(user: dict = Depends(get_current_user)):
  +    try:
  +        learner = gamification.get_learner()
  +    except Exception:
  +        learner = {"xp": 0, "level": 1, "streak": 0, "lives": 5, "topics_completed": 0}
  +    return {
  +        "xp": learner.get("xp", 0),
  +        "level": learner.get("level", 1),
  +        "streak": learner.get("streak", 0),
  +        "lives": learner.get("lives", 5),
  +        "topics_completed": learner.get("topics_completed", 0)
  +    }
  +
  +
  +SYLLABUS_CACHE_FILE = os.path.join(os.path.dirname(__file__), "syllabus_index.json")
  +_syllabus_cache = None
  +_syllabus_cache_mtime = 0
  +
  +def rebuild_syllabus_cache():
  +    conn = get_db()
  +    # 1. Compute subjects list
  +    subjects = conn.query("""
  +        SELECT s.id, s.name, s.board_id,
  +            (SELECT COUNT(*) FROM chapters c WHERE c.subject_id = s.id) as chapter_count,
  +            (SELECT COUNT(*) FROM topics t JOIN chapters c ON t.chapter_id = c.id WHERE c.subject_id = s.id) as topic_count,
  +            (SELECT COUNT(*) FROM chunks WHERE chapter_id IN (SELECT id FROM chapters WHERE subject_id = s.id)) as chunk_count,
  +            (SELECT COUNT(*) FROM problems p JOIN topics t ON p.topic_id = t.id JOIN chapters c ON t.chapter_id = c.id WHERE c.subject_id = s.id) as problem_count
  +        FROM subjects s ORDER BY s.board_id, s.name
  +    """)
  +    subjects_list = []
  +    for s in subjects:
  +        s_dict = dict(s)
  +        pct = min(100, int(s_dict["chunk_count"] / max(1, s_dict["topic_count"] * 3) * 100)) if s_dict["topic_count"] else 0
  +        s_dict["coverage"] = pct
  +        subjects_list.append(s_dict)
  +    
  +    # 2. Compute chapters per subject
  +    subject_chapters = {}
  +    for s in subjects_list:
  +        sub_id = s["id"]
  +        chapters = conn.query("""
  +            SELECT c.id, c.num, c.title, c.subject_id,
  +                (SELECT COUNT(*) FROM topics t WHERE t.chapter_id = c.id) as topic_count,
  +                (SELECT COUNT(*) FROM chunks WHERE chapter_id = c.id) as chunk_count,
  +                (SELECT COUNT(*) FROM problems p JOIN topics t ON p.topic_id = t.id WHERE t.chapter_id = c.id) as problem_count
  +            FROM chapters c WHERE c.subject_id = ? ORDER BY c.num
  +        """, (sub_id,))
  +        
  +        chapters_list = []
  +        for ch in chapters:
  +            ch_dict = dict(ch)
  +            pct = min(100, int(ch_dict["chunk_count"] / max(1, ch_dict["topic_count"] * 3) * 100)) if ch_dict["topic_count"] else 0
  +            ch_dict["coverage"] = pct
  +            ch_dict["subject_name"] = s["name"]
  +            chapters_list.append(ch_dict)
  +        subject_chapters[sub_id] = chapters_list
  +
  +    cache_data = {
  +        "subjects": subjects_list,
  +        "subject_chapters": subject_chapters,
  +        "timestamp": time.time()
  +    }
  +    
  +    try:
  +        with open(SYLLABUS_CACHE_FILE, "w", encoding="utf-8") as f:
  +            json.dump(cache_data, f, indent=2)
  +    except Exception as e:
  +        log.warning("Failed to write syllabus cache file: %s", e)
  +        
  +    return cache_data
  +
  +def get_syllabus_cache(force_rebuild=False):
  +    global _syllabus_cache, _syllabus_cache_mtime
  +    
  +    if not force_rebuild:
  +        if os.path.exists(SYLLABUS_CACHE_FILE):
  +            try:
  +                mtime = os.path.getmtime(SYLLABUS_CACHE_FILE)
  +                if _syllabus_cache is not None and mtime == _syllabus_cache_mtime:
  +                    return _syllabus_cache
  +                # Reload file
  +                with open(SYLLABUS_CACHE_FILE, "r", encoding="utf-8") as f:
  +                    _syllabus_cache = json.load(f)
  +                    _syllabus_cache_mtime = mtime
  +                    return _syllabus_cache
  +            except Exception as e:
  +                log.warning("Failed to read syllabus cache file: %s", e)
  +        else:
  +            _syllabus_cache = None
  +            _syllabus_cache_mtime = 0
  +            
  +    # Rebuild
  +    _syllabus_cache = rebuild_syllabus_cache()
  +    try:
  +        _syllabus_cache_mtime = os.path.getmtime(SYLLABUS_CACHE_FILE)
  +    except Exception:
  +        _syllabus_cache_mtime = 0
  +    return _syllabus_cache
  +
  +@app.get("/api/syllabus")
  +@rate_limit(120)
  +async def api_syllabus(request: Request, subject_id: Optional[str] = Query(None)):
  +    cache = get_syllabus_cache()
  +    if subject_id:
  +        chapters = cache.get("subject_chapters", {}).get(subject_id)
  +        if chapters is None:
  +            cache = get_syllabus_cache(force_rebuild=True)
  +            chapters = cache.get("subject_chapters", {}).get(subject_id, [])
  +        return JSONResponse(content=chapters)
  +    else:
  +        return JSONResponse(content=cache.get("subjects", []))
  +
  +
  +@app.api_route("/{path:path}", methods=["GET", "POST"], response_class=HTMLResponse, include_in_schema=False)
  +async def catch_all(request: Request, path: str):
  +    """Fallback to the original CBSEHandler for unmigrated routes."""
  +    from app import CBSEHandler
  +    import io
  +
  +    class FakeWriter:
  +        def __init__(self):
  +            self.status = 200
  +            self.headers = {}
  +            self.body = b""
  +        def send_response(self, code, msg=None):
  +            self.status = code
  +        def send_header(self, key, val):
  +            self.headers[key] = val
  +        def end_headers(self):
  +            pass
  +        def write(self, data):
  +            self.body += data if isinstance(data, bytes) else data.encode()
  +
  +    fake_writer = FakeWriter()
  +    raw_path = request.url.path
  +
  +    # Route rewriting for backward compatibility / validation
  +    if raw_path == "/learn-hub":
  +        raw_path = "/learn"
  +    elif raw_path == "/analytics":
  +        raw_path = "/parent-report"
  +    elif raw_path == "/game/quiz":
  +        raw_path = "/tutor"
  +    elif raw_path == "/game/flashcard":
  +        raw_path = "/tutor"
  +    elif raw_path == "/study-plan":
  +        raw_path = "/"
  +    else:
  +        # Rewrite /cbse/{subject}/chapter/{chapter_id} -> /chapter/{chapter_id}
  +        m_ch = re.match(r"^/cbse/[^/]+/chapter/([^/]+)", raw_path)
  +        if m_ch:
  +            raw_path = f"/chapter/{m_ch.group(1)}"
  +        else:
  +            # Rewrite /cbse/{subject} -> /board/cbse/{subject}
  +            m_sb = re.match(r"^/cbse/([^/]+)$", raw_path)
  +            if m_sb:
  +                raw_path = f"/board/cbse/{m_sb.group(1)}"
  +
  +    if request.query_params:
  +        raw_path += "?" + str(request.query_params)
  +
  +    handler = CBSEHandler.__new__(CBSEHandler)
  +    handler.command = request.method
  +    handler.path = raw_path
  +    handler.headers = dict(request.headers)
  +    handler.rfile = io.BytesIO(await request.body()) if request.method == "POST" else io.BytesIO()
  +    handler.wfile = fake_writer
  +    handler.send_response = fake_writer.send_response
  +    handler.send_header = fake_writer.send_header
  +    handler.end_headers = fake_writer.end_headers
  +    handler.requestline = f"{request.method} {raw_path} HTTP/1.1"
  +    handler.client_address = (request.client.host if request.client else "0.0.0.0", 0)
  +    handler.close_connection = True
  +    handler.server_version = "FastAPI/3.0"
  +
  +    loop = asyncio.get_event_loop()
  +    try:
  +        if request.method == "GET":
  +            await loop.run_in_executor(None, handler.do_GET)
  +        else:
  +            await loop.run_in_executor(None, handler.do_POST)
  +    except Exception as e:
  +        log.error("Legacy handler error for %s: %s", raw_path, e)
  +
  +    content_type = fake_writer.headers.get("Content-Type", "text/html; charset=utf-8")
  +    return Response(
  +        content=fake_writer.body,
  +        status_code=fake_writer.status,
  +        media_type=content_type.split(";")[0].strip()
  +    )
  +
  +
  +if __name__ == "__main__":
  +    import uvicorn
  +    port = int(os.environ.get("PORT", "9090"))
  +    workers = int(os.environ.get("UVICORN_WORKERS", "4"))
  +    log.info("Starting FastAPI on 0.0.0.0:%d with %d workers", port, workers)
  +    uvicorn.run("server:app", host="0.0.0.0", port=port, workers=workers, log_level="info")
diff --cc templates/base.html
index 0ac5131,0ac5131,0000000..592917e
mode 100644,100644,000000..100644
--- a/templates/base.html
+++ b/templates/base.html
@@@@ -1,127 -1,127 -1,0 +1,129 @@@@
  +<!DOCTYPE html>
  +<html lang="en">
  +<head>
  +<meta charset="UTF-8">
  +<meta name="viewport" content="width=device-width, initial-scale=1.0">
  +<title>{{ title }}</title>
  +<link rel="canonical" href="https://cbse.app/" />
  +<meta name="description" content="{{ description }}" />
  +<meta property="og:title" content="{{ title }}" />
  +<meta property="og:description" content="{{ description }}" />
  +<meta name="twitter:card" content="summary" />
  +<link rel="manifest" href="/manifest.json">
  +<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>≡ƒôÜ</text></svg>">
  +<link rel="stylesheet" href="/style.css">
+++<link rel="stylesheet" href="/style_vidya.css">
  +<style>
  +@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
  +:root {
  +    --primary: #1e1b4b;
  +    --primary-light: #312e81;
  +    --accent: #6366f1;
  +    --accent2: #8b5cf6;
  +    --accent-glow: #a78bfa;
  +    --highlight: #f43f5e;
  +    --bg: #f1f5f9;
  +    --card-bg: #ffffff;
  +    --glass-bg: rgba(255, 255, 255, 0.75);
  +    --text: #0f172a;
  +    --text-muted: #64748b;
  +    --border: #e2e8f0;
  +    --radius: 12px;
  +    --radius-sm: 8px;
  +    --radius-lg: 20px;
  +    --transition: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  +    --bottom-safe: env(safe-area-inset-bottom, 0px);
  +    --error: #ef4444;
  +    --success: #10b981;
  +    --font: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  +}
  +* { box-sizing: border-box; margin: 0; padding: 0; }
  +body {
  +    font-family: var(--font);
  +    background: var(--bg);
  +    color: var(--text);
  +    min-height: 100vh;
  +    min-height: 100dvh;
  +    overflow-x: hidden;
  +    line-height: 1.6;
  +    -webkit-font-smoothing: antialiased;
  +}
  +</style>
  +<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  +<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  +<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '\\(', right: '\\)', display: false}, {left: '$', right: '$', display: false}]});"></script>
  +{{ extra_css | safe }}</head>
  +<body class="{{ body_class }}">
+++<div class="vg-tricolor" aria-hidden="true"></div>
  +<div class="sticky-wrapper">
  +<div class="gbar">
  +  <div class="gbar-inner">
  +    <a href="/" class="gbar-brand">≡ƒôÜ AI Study Companion</a>
  +    <div class="gbar-nav">
  +      <a href="/">Home</a>
  +      <a href="/search">≡ƒöì Search</a>
  +      <a href="/tutor">≡ƒºá Tutor</a>
  +      <a href="/exams">≡ƒÅå Exams</a>
  +      <a href="/about">Γä╣∩╕Å About</a>
  +    </div>
  +    <div class="gbar-right">
  +      <span class="xp-badge">Γ¡É <span id="xp-display">{{ xp }}</span> XP</span>
  +{% if user %}
  +      <span class="user-badge">≡ƒæñ {{ user.username }}</span>
  +      <a href="/profile" class="gbar-link">Profile</a>
  +      <a href="#" onclick="fetch('/api/auth/logout',{method:'POST'}).then(()=>location.href='/')" class="gbar-link">Logout</a>
  +{% elif auth_configured %}
  +      <a href="/login" class="gbar-link">Login</a>
  +      <a href="/signup" class="gbar-link">Sign Up</a>
  +{% endif %}
  +    </div>
  +  </div>
  +</div>
  +</div>
  +<div class="container">
  +{{ content | safe }}
  +</div>
  +
  +<script>
  +window.onerror = function(msg, url, line, col, err) {
  +    console.error('GLOBAL:', msg, 'at', url, line + ':' + col);
  +};
  +window.addEventListener('unhandledrejection', function(e) {
  +    console.error('UNHANDLED PROMISE:', e.reason);
  +});
  +function _setText(id, val) {
  +    var el = document.getElementById(id);
  +    if (el) el.textContent = val;
  +}
  +async function loadGamification() {
  +    try {
  +        const resp = await fetch('/api/gamification');
  +        const data = await resp.json();
  +        _setText('streak-count', data.streak);
  +        _setText('xp-count', data.xp);
  +        _setText('level-num', data.level);
  +    } catch(e) {}
  +}
  +function escapeHtml(text) {
  +    const d = document.createElement('div');
  +    d.textContent = text;
  +    return d.innerHTML;
  +}
  +function switchMathTab(tabId) {
  +    document.querySelectorAll('.math-tab-content').forEach(el => {
  +        el.classList.remove('active');
  +    });
  +    document.querySelectorAll('.math-tab-btn').forEach(el => {
  +        el.classList.remove('active');
  +    });
  +    const targetContent = document.getElementById('math-tab-' + tabId);
  +    if (targetContent) targetContent.classList.add('active');
  +    const targetBtn = document.querySelector(`[onclick="switchMathTab('${tabId}')"]`);
  +    if (targetBtn) targetBtn.classList.add('active');
  +}
  +document.addEventListener('DOMContentLoaded', function() {
  +    loadGamification();
  +});
  +</script>
  +</body>
  +</html>
# Agents

## AI Tutor (`ai_tutor.py`)
Question-based learning agent that generates conceptual questions, evaluates student answers, and provides remedial content for weak areas.

- Generates questions: definition, formula, example, comparison, application, analysis
- Templates extract key concepts from topic content (bold terms, formulas)
- Self-assessment workflow with XP rewards
- Tracks sessions, answers, and progress per topic

## RAG Engine (`rag_engine.py`)
Retrieval-Augmented Generation engine for semantic search across educational content.

- Full-text search via SQLite FTS5
- Context retrieval for explain/solve pipelines
- Feed chunks to LLM for grounded answers

## MCP Server (`mcp_server.py`)
Model Context Protocol server exposing tools, resources, and prompts for AI integration.

- Tools: search, get_topic, get_chapter, explain, solve, retrieve_context
- Prompts: study_guide, practice_session
- Communicates via stdio using JSON-RPC 2.0

## LLM Client (`llm_client.py`)
Unified LLM client supporting multiple backends.

- Priority: Claude API > Ollama > generic OpenAI-compatible server > local llama.cpp -> fallback
- Methods: `query()`, `explain_topic()`, `solve_problem()`
- Singleton via `get_client()`
