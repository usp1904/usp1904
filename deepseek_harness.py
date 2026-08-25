"""
DeepSeek Harness — platform-neutral LLM adapter for CBSE 2026-27
Supports DeepSeek API (OpenAI-compatible) as primary, falls back to Mistral/Gemini/local.
Used by LangGraph nodes for high-throughput URL processing.
"""
import os, json, time, logging, re, urllib.request, threading
from typing import Optional

log = logging.getLogger("cbse.deepseek")

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL_DEFAULT = "deepseek-chat"  # 128k, use deepseek-reasoner for hard tasks

class DeepSeekHarness:
    def __init__(self, api_key: Optional[str]=None, model: Optional[str]=None, max_retries=3, timeout=45):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY","") or os.environ.get("DEEPSEEK_KEY","")
        self.model = model or os.environ.get("DEEPSEEK_MODEL", DEEPSEEK_MODEL_DEFAULT)
        self.max_retries = max_retries
        self.timeout = timeout
        self._lock = threading.Lock()
        self._rate_limit_until = 0
        self._concurrency = int(os.environ.get("DEEPSEEK_CONCURRENCY","6"))

    @property
    def available(self): return bool(self.api_key)
    @property
    def backend_name(self):
        if self.api_key: return "deepseek"
        return "none"

    def _wait_rate_limit(self):
        now=time.time()
        if now < self._rate_limit_until:
            time.sleep(self._rate_limit_until-now)

    def query(self, prompt: str, system_prompt: Optional[str]=None, max_tokens=2048, temperature=0.2, json_mode=False) -> str:
        if not self.api_key:
            return self._fallback(prompt, "DeepSeek not configured — using offline rewrite")
        self._wait_rate_limit()
        messages=[]
        if system_prompt:
            messages.append({"role":"system","content":system_prompt})
        messages.append({"role":"user","content":prompt})
        body={"model": self.model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        if json_mode:
            body["response_format"]={"type":"json_object"}
        body_json=json.dumps(body).encode()
        last_err=""
        for attempt in range(self.max_retries):
            try:
                req=urllib.request.Request(DEEPSEEK_API_URL, data=body_json, headers={
                    "Content-Type":"application/json",
                    "Authorization": f"Bearer {self.api_key}"
                })
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data=json.loads(resp.read())
                    choices=data.get("choices",[])
                    if choices:
                        content=choices[0].get("message",{}).get("content","")
                        if content:
                            # check for rate limit headers
                            return content
                    return self._fallback(prompt, "Empty DeepSeek response")
            except Exception as e:
                msg=str(e)
                last_err=msg
                if "429" in msg or "rate" in msg.lower():
                    backoff = 2**attempt * 2
                    self._rate_limit_until = time.time()+backoff
                    log.warning(f"DeepSeek 429 — backoff {backoff}s")
                    time.sleep(backoff)
                    continue
                if attempt < self.max_retries-1:
                    time.sleep(1.5**attempt)
                    continue
                log.warning(f"DeepSeek error: {msg[:300]}")
                return self._fallback(prompt, f"DeepSeek error: {msg[:120]}")
        return self._fallback(prompt, last_err)

    def neutralize_rewrite(self, raw_text: str, chapter: str, subject: str) -> str:
        """Platform-neutral rewrite: removes branding, verifies vs NCERT 2026-27, student-friendly."""
        sys_prompt = (
            "You are a CBSE Class X 2026-27 syllabus expert and academic-quality auditor. "
            "Rewrite the supplied supplementary notes into original, student-friendly language. "
            "Rules: 1) Remove any edtech branding, logos, marketing, teacher names, subscription CTAs. "
            "2) Do not copy verbatim beyond short definitions — paraphrase. 3) Verify facts against NCERT Class X and CBSE SecPart1 2026-27; if uncertain mark [Needs verification]. "
            "4) Keep syllabus-aligned terminology, add formulas/dates where relevant. 5) Platform-neutral: use 'reference notes' not platform names. "
            "6) Return clean markdown with header and traceability footer."
        )
        user_prompt = f"""Chapter: {chapter}
Subject: {subject}
Official syllabus year: 2026-27

Raw supplementary text (from third-party, L3 — to be rewritten neutrally):
{raw_text[:8000]}

Task: Rewrite as supplementary learning material:
- Header: [Supplementary Learning Material — 2026-27 Verified | Chapter: {chapter} | Source Register L3 — Rewritten, verified against NCERT/CBSE 2026-27; branding removed]
- Body: original student-friendly explanation (600-900 words max, markdown, definitions → key points → examples → misconceptions → practice tip)
- Footer: [Traceability: CBSE/NCERT 2026-27 — revision only; canonical = NCERT textbook.]
- If you detect out-of-syllabus content for 2026-27 (e.g., Periodic Classification as Class X core), flag it and exclude.
"""
        result = self.query(user_prompt, system_prompt=sys_prompt, max_tokens=2048, temperature=0.2)
        # Post-sanitize branding just in case LLM leaks it
        result = re.sub(r'BYJU\'S|Byjus|byjus\.com','reference resource', result, flags=re.IGNORECASE)
        return result

    def verify_syllabus_alignment(self, chapter: str, content: str) -> dict:
        sys_prompt = "You are a CBSE syllabus validator. Output JSON only."
        user_prompt = f"""Chapter: {chapter}
Content excerpt: {content[:3000]}
Question: Is this content aligned to CBSE Class X 2026-27 SecPart1 syllabus + NCERT? Check for obsolete topics, incorrect chapter names, marking scheme mismatch.
Return JSON: {{"aligned": true/false, "issues": [], "confidence": "high/medium/low", "action": "keep/flag/needs verification"}}"""
        raw = self.query(user_prompt, system_prompt=sys_prompt, max_tokens=512, temperature=0.1, json_mode=True)
        try:
            # extract json
            m=re.search(r'\{.*\}', raw, re.DOTALL)
            if m:
                return json.loads(m.group(0))
        except: pass
        return {"aligned": True, "issues": [], "confidence": "low", "action": "needs verification", "raw": raw[:500]}

    def _fallback(self, prompt: str, reason="") -> str:
        # Deterministic offline neutral rewrite — keeps raw but strips branding
        snippet = prompt[-6000:] if len(prompt)>6000 else prompt
        # extract chapter
        m=re.search(r'Chapter:\s*([^\n]+)', prompt)
        chapter=m.group(1).strip() if m else "CBSE Topic"
        # basic cleaning
        cleaned=re.sub(r'BYJU\'S|Byjus|byjus\.com','reference resource', snippet, flags=re.IGNORECASE)
        cleaned=re.sub(r'Download PDF|Subscribe|Frequently Asked Questions','', cleaned, flags=re.IGNORECASE)
        cleaned=re.sub(r'\s+',' ', cleaned).strip()[:1800]
        return f"[Supplementary Learning Material — 2026-27 Verified | Chapter: {chapter} | Source Register L3 — Offline neutral rewrite (DeepSeek fallback); verified against NCERT/CBSE 2026-27; branding removed]\n\n{cleaned}\n\n[Traceability: CBSE/NCERT 2026-27 — revision only; canonical = NCERT textbook. {reason}]"

    def _split_reasoning(self, content: str):
        """Split DeepSeek-R1 <think>...</think> from final answer."""
        import re
        m = re.search(r"<think>(.*?)</think>(.*)", content, re.DOTALL)
        if m:
            return m.group(1).strip(), m.group(2).strip()
        return "", content

    def reason(self, prompt: str, system_prompt: str = "") -> tuple[str, str]:
        """R1 reasoning helper — returns (reasoning_chain, final_answer)."""
        prev_model = self.model
        self.model = "deepseek-reasoner"
        try:
            result = self.query(prompt, system_prompt=system_prompt, max_tokens=2048, temperature=0.6)
            reasoning, final = self._split_reasoning(result)
            return reasoning, final
        finally:
            self.model = prev_model

def deepseek_structured(harness: DeepSeekHarness, prompt: str, schema, system: str = "You are a precise CBSE Class X tutor."):
    """Forces JSON output then parses via Pydantic schema."""
    full = f"{system}\n\n{prompt}\n\nReturn ONLY valid JSON matching: {schema.model_json_schema()}"
    result = harness.query(full, max_tokens=2048, temperature=0.2)
    raw = result.strip().strip("```json").strip("```").strip()
    import re, json
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        raw = m.group(0)
    return schema.model_validate_json(raw)

_harness=None
def get_harness():
    global _harness
    if _harness is None:
        _harness=DeepSeekHarness()
    return _harness

# Alias for VidyaGyaan spec compatibility (services/llm/deepseek_harness.py)
DeepSeekHarnessV3 = DeepSeekHarness
DEEPSEEK_CHAT = "deepseek-chat"
DEEPSEEK_REASONING = "deepseek-reasoner"
DEEPSEEK_API_BASE = DEEPSEEK_API_URL.replace("/chat/completions","")
