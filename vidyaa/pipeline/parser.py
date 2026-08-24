"""
Parser — Google Document Tree compatible normalizer
Strips air-fillers, extra spaces, apostrophes, commas, single/double quotes per spec,
but preserves semantic meaning for OKF v0.2 entity resolution
"""
import re
AIRFILLERS = [r"\buh\b", r"\blike\b", r"\byou know\b", r"\bso\b", r"\bactually\b", r"\bbasically\b", r"\bkind of\b", r"\bsort of\b"]
RE_AIR = re.compile("|".join(AIRFILLERS), flags=re.I)
RE_SPACES = re.compile(r"[ \t]{2,}")
RE_NEWLINES = re.compile(r"\n{3,}")

def normalize(text: str, strip_quotes=False) -> str:
    # 1. remove air-fillers
    text = RE_AIR.sub("", text)
    # 2. normalize quotes/apostrophes if requested for deduplication key only
    # keep original text readable; dedup key uses stripped variant
    # 3. collapse spaces
    text = RE_SPACES.sub(" ", text)
    text = RE_NEWLINES.sub("\n\n", text)
    # 4. trim lines
    text = "\n".join(line.strip() for line in text.splitlines())
    return text.strip()

def dedup_key(text: str) -> str:
    # for OKF duplicate elimination: lower, no spaces, no punctuation
    k = text.lower()
    k = re.sub(r"['\",`’“”]", "", k)
    k = re.sub(r"\s+", "", k)
    k = re.sub(r",", "", k)
    return k

def extract_text_from_pdf(pdf_path):
    import fitz  # PyMuPDF
    doc = fitz.open(str(pdf_path))
    full = "\n".join(page.get_text("text") for page in doc)
    return normalize(full)
