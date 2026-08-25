#!/usr/bin/env python3
"""
noise_gate.py — token-optimized filter for noisy commands
Used by .opencode/plugins/noise-gate.js hook.
Keeps: errors, failures, final summary. Drops: progress bars, download logs.
If output is short (<60 lines) → passthrough untouched.
Usage: python tools/noise_gate.py <raw_file>  OR  cat raw | python tools/noise_gate.py
"""
import sys, re, os

KEEP_RE = re.compile(
    r"(?i)(error|err!|fail|failed|failure|exception|traceback|panic|fatal|warning|warn\s*:|passed|failed|skipped|test suites|tests?:\s*\d|ok\s*\(|done|built|successfully|added\s+\d+\s+package|audited|summary|coverage|elapsed|time\s*:|assert)"
)
# Final-summary-ish lines (last 15 always kept anyway, but this catches earlier summaries)
SUMMARY_RE = re.compile(r"(?i)^\s*(tests|test suites|time|duration|build|done|summary|result|passed|failed|ok|coverage).*\d")
PROGRESS_RE = re.compile(r"(Downloading|Fetching|Installing|Progress|█|▏|▎|▍|▌|▋|▊|▉|\b\d{1,3}%\b.*\|)")
SHORT_THRESHOLD_LINES = 60
SHORT_THRESHOLD_BYTES = 5000
TAIL_KEEP = 15

def filter_lines(lines):
    if len(lines) < SHORT_THRESHOLD_LINES and sum(len(l) for l in lines) < SHORT_THRESHOLD_BYTES:
        return lines, "passthrough (short output)"
    kept_idx = set()
    for i, line in enumerate(lines):
        if KEEP_RE.search(line):
            kept_idx.add(i)
        elif PROGRESS_RE.search(line):
            continue
        elif SUMMARY_RE.search(line):
            kept_idx.add(i)
    # tail: keep only tail lines that are errors/summary or not progress spam
    for i in range(max(0, len(lines)-TAIL_KEEP), len(lines)):
        if i in kept_idx:
            continue
        line = lines[i]
        if PROGRESS_RE.search(line) and not KEEP_RE.search(line):
            continue
        kept_idx.add(i)
    if not kept_idx:
        return lines[-TAIL_KEEP:], "fallback tail"
    result = [lines[i] for i in sorted(kept_idx)]
    return result, f"filtered {len(lines)} -> {len(result)} lines ({len(result)*100//max(len(lines),1)}% kept)"

def main():
    # Fix Windows cp1252 encoding for block chars
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    raw_path = sys.argv[1] if len(sys.argv) > 1 else None
    if raw_path and os.path.exists(raw_path):
        with open(raw_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
        src = raw_path
    else:
        data = sys.stdin.read()
        lines = data.splitlines()
        src = "stdin"
    filtered, note = filter_lines(lines)
    print(f"[noise-gate] {note} | source: {src} | full log kept at {raw_path or 'stdin'}")
    for l in filtered:
        print(l)
    if len(filtered) < len(lines):
        print(f"[noise-gate] dropped {len(lines)-len(filtered)} noisy lines (progress/install spam). Full log: {raw_path}")

if __name__ == "__main__":
    main()
