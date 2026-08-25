"""
Enterprise Schema — VidyaGyaan (AY 2026-27) additive layer
Dual-compatible: SQLite (WAL) + PostgreSQL/Neon via db.py translation.
Never drops existing tables; all CREATE IF NOT EXISTS.
Preserves: boards/subjects/chapters/topics/chunks/problems pipeline.
"""
import logging, json, uuid
from database import get_db

log = logging.getLogger("cbse.enterprise")

# SQLite-friendly but spec-aligned DDL.
# Postgres production will store UUID as TEXT (py generates), JSONB as TEXT (json dumps),
# TIMESTAMPTZ as TEXT (isoformat). db.py handles ?→%s, INSERT OR IGNORE etc.
ENTERPRISE_DDL = """
-- ── Students (spec: students UUID) ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    avatar TEXT,
    class_no INTEGER DEFAULT 10,
    academic_year TEXT DEFAULT '2026-2027',
    school_code TEXT,
    created_at TEXT DEFAULT (datetime('now','localtime'))
);
CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);

-- ── Exercises (per spec) ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id TEXT NOT NULL,
    exercise_label TEXT,
    exercise_type TEXT,
    question_count INTEGER,
    ncert_page_ref TEXT,
    FOREIGN KEY(chapter_id) REFERENCES chapters(id)
);
CREATE INDEX IF NOT EXISTS idx_exercises_chapter ON exercises(chapter_id);

-- ── Questions (spec: UUID, JSONB fields as TEXT) ───────────────────────
CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    exercise_id INTEGER REFERENCES exercises(id),
    question_number TEXT,
    question_text TEXT NOT NULL,
    question_type TEXT,
    difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 5),
    bloom_level TEXT,
    marks REAL,
    has_diagram INTEGER DEFAULT 0,
    ncert_page INTEGER,
    solution_steps TEXT,
    formulae_used TEXT,
    key_concepts TEXT,
    okf_concept_ids TEXT
);
CREATE INDEX IF NOT EXISTS idx_questions_exercise ON questions(exercise_id);

-- ── Theorems (MathTheoremEngine) ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS theorems (
    id TEXT PRIMARY KEY,
    chapter_id TEXT REFERENCES chapters(id),
    theorem_name TEXT NOT NULL,
    statement TEXT NOT NULL,
    proof_steps TEXT,
    analogy_text TEXT,
    analogy_visual TEXT,
    concept_orientation TEXT,
    okf_id TEXT UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_theorems_chapter ON theorems(chapter_id);

-- ── Experiments (ScienceStoryEngine) ────────────────────────────────────
CREATE TABLE IF NOT EXISTS experiments (
    id TEXT PRIMARY KEY,
    chapter_id TEXT REFERENCES chapters(id),
    experiment_no TEXT,
    title TEXT NOT NULL,
    objective TEXT,
    apparatus TEXT,
    chemicals TEXT,
    procedure TEXT,
    observations TEXT,
    conclusions TEXT,
    real_world_apps TEXT,
    safety_notes TEXT,
    story_narrative TEXT,
    advanced_apps TEXT,
    okf_id TEXT UNIQUE
);

-- ── History Scenes (HistoryThrillerEngine) ──────────────────────────────
CREATE TABLE IF NOT EXISTS history_scenes (
    id TEXT PRIMARY KEY,
    chapter_id TEXT REFERENCES chapters(id),
    event_name TEXT,
    year INTEGER,
    setting TEXT,
    characters TEXT,
    conflict TEXT,
    climax TEXT,
    resolution TEXT,
    cinematic_style TEXT,
    real_facts TEXT,
    exam_importance TEXT
);

-- ── Social Episodes (FamilyDramaEngine) ─────────────────────────────────
CREATE TABLE IF NOT EXISTS social_episodes (
    id TEXT PRIMARY KEY,
    chapter_id TEXT REFERENCES chapters(id),
    episode_title TEXT,
    narrative_style TEXT,
    cast TEXT,
    storyline TEXT,
    bullet_breakdown TEXT,
    moral TEXT
);

-- ── Streaks (enterprise, per student) ───────────────────────────────────
CREATE TABLE IF NOT EXISTS streaks (
    student_id TEXT PRIMARY KEY REFERENCES students(id),
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_active_date TEXT,
    streak_freeze_used INTEGER DEFAULT 0,
    total_xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    rank_title TEXT DEFAULT 'Beginner'
);

CREATE TABLE IF NOT EXISTS streak_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT REFERENCES students(id),
    active_date TEXT NOT NULL,
    xp_earned INTEGER,
    activities TEXT,
    UNIQUE(student_id, active_date)
);
CREATE INDEX IF NOT EXISTS idx_streak_history_student ON streak_history(student_id);

-- ── Badges / Student Badges (extend existing badges table) ──────────────
CREATE TABLE IF NOT EXISTS student_badges (
    student_id TEXT REFERENCES students(id),
    badge_code TEXT REFERENCES badges(code),
    earned_at TEXT DEFAULT (datetime('now','localtime')),
    PRIMARY KEY (student_id, badge_code)
);

-- ── Daily Quests (enterprise) ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS daily_quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quest_date TEXT DEFAULT (date('now','localtime')),
    quest_type TEXT,
    target_count INTEGER,
    xp_reward INTEGER,
    description TEXT
);
CREATE TABLE IF NOT EXISTS quest_completions (
    student_id TEXT REFERENCES students(id),
    quest_id INTEGER REFERENCES daily_quests(id),
    completed_at TEXT DEFAULT (datetime('now','localtime')),
    progress INTEGER DEFAULT 0,
    PRIMARY KEY (student_id, quest_id)
);

-- ── OKF v0.2 Knowledge Graph (enterprise, supplements knowledge_graph) ───
CREATE TABLE IF NOT EXISTS okf_entities (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    alternate_names TEXT,
    in_language TEXT DEFAULT 'en-IN',
    source_citation TEXT,
    subject TEXT,
    class_level INTEGER DEFAULT 10
);
CREATE INDEX IF NOT EXISTS idx_okf_entities_type ON okf_entities(type);
CREATE INDEX IF NOT EXISTS idx_okf_entities_subject ON okf_entities(subject);

CREATE TABLE IF NOT EXISTS okf_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    evidence_text TEXT,
    UNIQUE(subject, predicate, object)
);
CREATE INDEX IF NOT EXISTS idx_okf_relations_subject ON okf_relations(subject);
CREATE INDEX IF NOT EXISTS idx_okf_relations_object ON okf_relations(object);

-- ── Leaderboard weekly (materialized view → view in SQLite) ─────────────
DROP VIEW IF EXISTS leaderboard_weekly;
CREATE VIEW IF NOT EXISTS leaderboard_weekly AS
SELECT s.id as student_id, s.name, s.avatar,
       COALESCE(SUM(sh.xp_earned),0) as week_xp,
       st.current_streak
FROM students s
LEFT JOIN streaks st ON st.student_id = s.id
LEFT JOIN streak_history sh ON sh.student_id = s.id AND sh.active_date >= date('now','-7 days')
GROUP BY s.id, s.name, s.avatar, st.current_streak
ORDER BY week_xp DESC;
"""

ENTERPRISE_SEED = [
    # Seed VidyaGyaan subjects narrative_style mapping (spec insert)
    ("INSERT OR IGNORE INTO content_meta (key, value) VALUES (?, ?)", ("enterprise_schema_version", "1.0-vidya-2026-27")),
    ("INSERT OR IGNORE INTO content_meta (key, value) VALUES (?, ?)", ("enterprise_subjects_spec", json.dumps({
        "MA": {"name":"Mathematics","narrative":"theorem_analogy","icon":"🔢","color":"#6366F1"},
        "SC": {"name":"Science","narrative":"detective_story","icon":"🔬","color":"#10B981"},
        "SS": {"name":"Social Science","narrative":"cinematic","icon":"🌍","color":"#F59E0B"},
        "EN": {"name":"English","narrative":"soul_music","icon":"📚","color":"#EC4899"},
        "HI": {"name":"हिन्दी","narrative":"soul_music","icon":"🪷","color":"#EF4444"},
    }))),
]

BADGE_SEED = [
    ("first_step", "First Step", "Complete your first topic", "🌱", 50),
    ("streak_7", "Week Warrior", "7-day streak", "🔥", 100),
    ("streak_30", "Month Master", "30-day streak", "🏆", 300),
    ("math_pro", "Math Pro", "Solve 50 maths problems", "🔢", 150),
    ("science_star", "Science Star", "Complete 10 experiments", "🔬", 150),
    ("history_buff", "History Buff", "Watch 5 history thrillers", "🎬", 100),
]

def init_enterprise_schema():
    db = get_db()
    try:
        db.executescript(ENTERPRISE_DDL)
        for sql, *params in ENTERPRISE_SEED:
            try:
                if params:
                    db.execute(sql, params[0] if len(params)==1 and isinstance(params[0], tuple) else params)
                else:
                    db.execute(sql)
            except Exception as e:
                log.debug("seed skip %s: %s", sql[:60], e)
        # Seed badges required by spec
        for code, name, desc, icon, xp in BADGE_SEED:
            try:
                db.execute("INSERT OR IGNORE INTO badges (code, name, description, icon, xp_reward) VALUES (?, ?, ?, ?, ?)",
                           (code, name, desc, icon, xp))
            except Exception:
                # table may be named differently; try alternative
                try:
                    db.execute("INSERT OR IGNORE INTO badges (id, name, description, icon, xp) VALUES (?, ?, ?, ?, ?)",
                               (code, name, desc, icon, xp))
                except Exception as e:
                    log.debug("badge seed skip %s: %s", code, e)
        log.info("Enterprise schema initialized")
        return True
    except Exception as e:
        log.error("Enterprise schema init failed: %s", e)
        return False

if __name__ == "__main__":
    ok = init_enterprise_schema()
    print("enterprise_schema", "OK" if ok else "FAIL")
    # verify counts
    db = get_db()
    for t in ["students","exercises","questions","theorems","experiments","history_scenes","social_episodes","streaks","okf_entities","okf_relations"]:
        try:
            c = db.execute(f"SELECT COUNT(*) as c FROM {t}").fetchone()["c"]
            print(t, c)
        except Exception as e:
            print(t, "ERR", e)
