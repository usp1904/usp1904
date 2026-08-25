"""Quick IPv4/IPv6 + data sync check — run inside container or host"""
import socket, os, sqlite3, pathlib
print("=== Network ===")
for host in ["127.0.0.1", "app", "ollama"]:
    try:
        print(f" resolve {host} -> {socket.gethostbyname(host)}")
    except Exception as e:
        print(f" resolve {host} FAIL {e}")
# try listen addresses
import subprocess, json, sys
try:
    import httpx
    for url in ["http://127.0.0.1:9090/health","http://app:9090/health"]:
        try:
            r=httpx.get(url, timeout=3)
            print(f" GET {url} -> {r.status_code} {r.text[:120]}")
        except Exception as e:
            print(f" GET {url} FAIL {e}")
except: pass
print("\n=== Data sync ===")
for p in [pathlib.Path("cbse_content.db"), pathlib.Path("/app/data/cbse_content.db"), pathlib.Path("./data/cbse_content.db")]:
    print(f" {p} exists={p.exists()} size={(p.stat().st_size if p.exists() else 0)}")
    if p.exists():
        try:
            conn=sqlite3.connect(str(p))
            print("  ", conn.execute("SELECT value FROM content_meta WHERE key='syllabus_year'").fetchone())
            print("  ", conn.execute("SELECT count(*) FROM chunks").fetchone())
        except Exception as e:
            print(f"   err {e}")
print("\nEnv DATABASE_URL:", os.environ.get("DATABASE_URL","(default sqlite)"))
