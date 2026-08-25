"""
Internal ↔ External data sync (SQLite ↔ PostgreSQL)
- Internal: Docker bridge cbse_net (app ↔ db via DATABASE_URL)
- External: host file ./cbse_content.db ↔ named volume cbse_data:/app/data/cbse_content.db
Run:
  docker compose --profile sync run --rm db-sync
  # or host: python tools/sync_db.py --from-sqlite --to-postgres
"""
import os, sys, pathlib, sqlite3, logging
logging.basicConfig(level=logging.INFO, format="[sync] %(message)s")
log=logging.getLogger("sync")

ROOT=pathlib.Path(__file__).resolve().parents[1]
SQLITE_HOST=ROOT/"cbse_content.db"
SQLITE_DOCKER=pathlib.Path(os.environ.get("SQLITE_PATH","/data/cbse_content.db"))
PG_URL=os.environ.get("DATABASE_URL","")

def sync_host_to_volume():
    """Host -> Docker volume (external -> internal)"""
    if not SQLITE_HOST.exists():
        log.info(f"Host DB not found: {SQLITE_HOST} — skip")
        return
    SQLITE_DOCKER.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    # include WAL/SHM
    for suffix in ["", "-wal", "-shm"]:
        src=pathlib.Path(str(SQLITE_HOST)+suffix)
        dst=pathlib.Path(str(SQLITE_DOCKER)+suffix)
        if src.exists():
            shutil.copy2(src, dst)
            log.info(f"Copied {src.name} ({src.stat().st_size} bytes) -> volume")
    log.info("Host → volume sync done")

def sync_volume_to_host():
    """Volume -> Host (internal -> external) backup"""
    if not SQLITE_DOCKER.exists():
        log.info(f"Volume DB not found: {SQLITE_DOCKER} — skip")
        return
    import shutil
    for suffix in ["", "-wal", "-shm"]:
        src=pathlib.Path(str(SQLITE_DOCKER)+suffix)
        dst=pathlib.Path(str(SQLITE_HOST)+suffix)
        if src.exists():
            shutil.copy2(src, dst)
            log.info(f"Backed up {src.name} -> host")

def verify_sync():
    import sqlite3
    for label, path in [("host", SQLITE_HOST), ("volume", SQLITE_DOCKER)]:
        if not pathlib.Path(path).exists():
            log.info(f"{label}: missing {path}")
            continue
        try:
            conn=sqlite3.connect(str(path))
            cur=conn.cursor()
            cur.execute("SELECT count(*) FROM chunks")
            chunks=cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM topics")
            topics=cur.fetchone()[0]
            cur.execute("SELECT value FROM content_meta WHERE key='syllabus_year'")
            row=cur.fetchone()
            year=row[0] if row else "?"
            log.info(f"{label} {path.name}: syllabus_year={year}, topics={topics}, chunks={chunks}")
            conn.close()
        except Exception as e:
            log.warning(f"{label} verify failed {path}: {e}")

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--from-host", action="store_true", help="Host -> volume")
    ap.add_argument("--to-host", action="store_true", help="Volume -> host")
    ap.add_argument("--verify", action="store_true", help="Verify both")
    args=ap.parse_args()
    if args.from_host: sync_host_to_volume()
    elif args.to_host: sync_volume_to_host()
    else:
        # default: host -> volume if volume empty, else verify
        if not SQLITE_DOCKER.exists() or SQLITE_DOCKER.stat().st_size==0:
            sync_host_to_volume()
        verify_sync()
    if args.verify: verify_sync()
