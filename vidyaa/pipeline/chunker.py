"""
Chunker — 500-1000 words, sentence-boundary, 80w overlap
Produces Google OKF v0.2 compatible chunks with syllabus correlation
"""
import re, hashlib

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

def chunk_text(text: str, doc_id: str, min_w=500, max_w=1000, overlap=80):
    words = text.split()
    if not words:
        return []
    # sentence-aware greedy packing
    sentences = SENT_SPLIT.split(text)
    chunks=[]; cur=[]; cur_w=0
    def flush():
        nonlocal cur, cur_w
        if not cur: return
        body = " ".join(cur).strip()
        w = len(body.split())
        if w < min_w and chunks:
            # merge tiny tail into previous
            chunks[-1]["text"] += " " + body
            chunks[-1]["words"] = len(chunks[-1]["text"].split())
            chunks[-1]["dedupKey"] = hashlib.sha256(chunks[-1]["text"].encode()).hexdigest()[:16]
        else:
            chunks.append({
                "id": f"{doc_id}__c{len(chunks):04d}",
                "docId": doc_id,
                "text": body,
                "words": w,
                "dedupKey": hashlib.sha256(body.encode()).hexdigest()[:16],
                "syllabusSource": "NCERT_2026_27",
                "academicYear": "2026-27"
            })
        # overlap: keep last `overlap` words as prefix for next
        tail = " ".join(cur).split()[-overlap:] if overlap else []
        cur = [" ".join(tail)] if tail else []
        cur_w = len(tail)

    for sent in sentences:
        sw = len(sent.split())
        if cur_w + sw > max_w:
            flush()
        cur.append(sent); cur_w += sw
        if cur_w >= min_w and cur_w >= max_w*0.7:
            # sentence boundary flush when in 500-1000 window
            if cur_w >= min_w:
                flush()
    if cur:
        flush()
    return chunks

def dedup(chunks):
    seen=set(); out=[]
    for c in chunks:
        # dedup via dedupKey + normalized key (no spaces/punct)
        from parser import dedup_key
        k = dedup_key(c["text"])[:64]
        if k in seen: continue
        seen.add(k); out.append(c)
    return out
