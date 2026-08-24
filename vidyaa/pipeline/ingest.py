#!/usr/bin/env python3
"""
Auto-Ingest Pipeline — CBSE 2026-27 → S3 + Graphify + Qdrant
Flow: Download (cbseacademic.nic.in) → Parse (Google Document Tree) → Normalize → Chunk 500-1000w → OKF v0.2 dedup → Embed → S3 (+ Vector/Graph) → Graphify communities

Usage:
  pip install -r requirements.txt
  cp .env.example .env  # set AWS creds + OPENAI_API_KEY
  python ingest.py --config config.json
  python ingest.py --watch   # auto on new PDFs in pipeline/raw/
"""
import argparse, json, os, hashlib, time
from pathlib import Path
import httpx
from dotenv import load_dotenv
load_dotenv()

from parser import normalize, extract_text_from_pdf
from chunker import chunk_text, dedup
from s3_store import S3Store

ROOT = Path(__file__).parent
RAW = ROOT / "raw"
OUT = Path(__file__).parent.parent / "graphify-out"

def download_pdfs(urls):
    RAW.mkdir(exist_ok=True)
    for url in urls:
        name = url.split("/")[-1] or f"cbse_{hashlib.sha256(url.encode()).hexdigest()[:8]}.pdf"
        dest = RAW / name
        if dest.exists() and dest.stat().st_size > 1024:
            print(f"cached {dest.name}")
            continue
        print(f"↓ {url}")
        try:
            r = httpx.get(url, follow_redirects=True, timeout=60)
            r.raise_for_status()
            dest.write_bytes(r.content)
            print(f"  → {dest} ({len(r.content)//1024} KB)")
        except Exception as e:
            print(f"  ! failed {url}: {e}")

def ingest_once(cfg):
    s3 = S3Store(cfg["s3"]["bucket"], cfg["s3"]["region"], cfg["s3"]["prefix"])
    all_chunks=[]
    pdfs = list(RAW.glob("*.pdf"))
    if not pdfs:
        print("No PDFs in pipeline/raw — downloading from config...")
        download_pdfs(cfg["syllabus"]["pdfUrls"])
        pdfs = list(RAW.glob("*.pdf"))

    for pdf in pdfs:
        print(f"\n— {pdf.name}")
        text = extract_text_from_pdf(pdf)
        print(f"  parsed {len(text.split())} words")
        doc_id = pdf.stem
        chunks = chunk_text(text, doc_id, cfg["chunking"]["minWords"], cfg["chunking"]["maxWords"], cfg["chunking"]["overlapWords"])
        chunks = dedup(chunks)
        print(f"  chunked → {len(chunks)} (500-1000w, overlap 80)")
        # enrich
        for c in chunks:
            c["source_location"] = f"{cfg['syllabus']['sourceOfTruth']}#{doc_id}"
            c["s3Key"] = s3.put_chunk(c["id"], c, subject="Mathematics", chapter=doc_id)
            print(f"    s3://{cfg['s3']['bucket']}/{cfg['s3']['prefix']}/chunks/.../{c['id'][:20]} ({c['words']}w)")
        all_chunks.extend(chunks)
        # upload raw pdf itself to s3://.../raw/
        s3.put_file(pdf, ["raw", pdf.name], metadata={"syllabusSource":"NCERT_2026_27"})
        print(f"  raw uploaded")

    # write local manifest for graphify
    OUT.mkdir(exist_ok=True)
    manifest = OUT / "chunks.json"
    manifest.write_text(json.dumps(all_chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✓ {len(all_chunks)} chunks → {manifest}")
    print(f"✓ S3 manifest: s3://{cfg['s3']['bucket']}/{cfg['s3']['prefix']}/chunks/")

    # build graphify graph (deep mode) — delegates to graphify CLI if installed
    try:
        import subprocess, sys
        py = sys.executable
        print("\n— building graphify graph (deep)...")
        # use python -m graphify if available, else skip
        subprocess.run([py, "-m", "graphify", "build", str(OUT)], check=False, timeout=30)
    except Exception as e:
        print(f"  graphify skip: {e}")

    # upload graph.json if exists
    g = OUT / "graph.json"
    if g.exists():
        s3.put_graph(g)
        print(f"✓ graph uploaded → s3://{cfg['s3']['bucket']}/{cfg['s3']['prefix']}/graph/graphify/graph.json")

    # presigned manifest url
    try:
        url = s3.presigned(f"{cfg['s3']['prefix']}/chunks/{all_chunks[0]['id']}.json")
        print(f"  presigned sample: {url[:90]}...")
    except: pass
    print(f"\nDone. Total chunks: {len(all_chunks)} | Bucket: {cfg['s3']['bucket']} | Region: {cfg['s3']['region']}")
    return all_chunks

def watch_loop(cfg, interval=60):
    print(f"watching {RAW} every {interval}s — drop new PDFs to auto-ingest (Ctrl+C to stop)")
    seen = set(p.stat().st_mtime for p in RAW.glob("*.pdf"))
    while True:
        time.sleep(interval)
        cur = set(p.stat().st_mtime for p in RAW.glob("*.pdf"))
        if cur != seen or any(p.suffix==".pdf" for p in RAW.glob("*.pdf")):
            print("\n[watch] change detected → re-ingest")
            ingest_once(cfg)
            seen = cur

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT/"config.json"))
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--download-only", action="store_true")
    args = ap.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    if args.download_only:
        download_pdfs(cfg["syllabus"]["pdfUrls"])
    elif args.watch:
        watch_loop(cfg)
    else:
        ingest_once(cfg)
