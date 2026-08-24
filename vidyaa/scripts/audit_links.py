import re, pathlib, json, sys
from urllib.parse import urlparse

idx = pathlib.Path(r"C:\Windows\System32\newopenai\index.html").read_text(encoding="utf-8")
# Find all href and src
hrefs = re.findall(r'href="([^"]+)"', idx)
srcs = re.findall(r'src="([^"]+)"', idx)
all_links = hrefs + srcs
print(f"Total href/src found: {len(all_links)}")
for l in all_links[:30]:
    print(" ", l)

# Check for orphan/broken patterns
orphan = [l for l in all_links if l.strip()=="#" or l.strip()=="" or l.startswith("javascript:")]
print(f"\nOrphan links (# or empty): {len(orphan)}")
for o in orphan:
    print("  ORPHAN:", repr(o))

# Check internal file links (relative) that should exist
root = pathlib.Path(r"C:\Windows\System32\newopenai")
broken = []
for link in all_links:
    if link.startswith("http") or link.startswith("//") or link.startswith("data:") or link.startswith("mailto:"):
        continue
    # strip query/hash
    clean = link.split("?")[0].split("#")[0]
    if not clean or clean == "/":
        continue
    # relative path
    p = root / clean.lstrip("/")
    if not p.exists():
        # check if it's an anchor like reference/VidyaGyaan.html -> should exist
        broken.append(link)

print(f"\nBroken internal links (file not found): {len(broken)}")
for b in broken[:20]:
    print("  BROKEN:", b)

# Check corpora existence
for f in ["packages/cbse_corpus/maths_2026_27.json","packages/cbse_corpus/science_2026_27.json","packages/cbse_corpus/social_2026_27.json","packages/cbse_corpus/english_2026_27.json","packages/cbse_corpus/hindi_2026_27.json","reference/VidyaGyaan.html"]:
    exists = (root/f).exists()
    print(f"  {'OK' if exists else 'MISSING'} {f}")

# Check youtube videos not orphan
for fname in ["maths_2026_27.json","science_2026_27.json","social_2026_27.json"]:
    p = root/"packages/cbse_corpus"/fname
    data = json.loads(p.read_text(encoding="utf-8"))
    for ch in data["chapters"]:
        vids = ch.get("youtubeVideos",[])
        for v in vids:
            if v.get("orphan"):
                print(f"  ORPHAN VIDEO {fname} {ch['id']} {v['id']}")
            if not v.get("id") or len(v["id"])!=11:
                print(f"  BROKEN VIDEO ID {fname} {ch['id']} {v.get('id')}")

# Check UI/UX enterprise: count cards, check design tokens
print("\nUI/UX checks:")
# Check for inline styles vs tokens
if "var(--" in idx:
    print("  OK: Uses CSS variables (design tokens)")
else:
    print("  WARN: No CSS variables")
# Check for responsive
if "@media" in idx:
    print("  OK: Responsive media queries")
# Check for accessibility (aria, alt)
if 'aria-label' in idx or 'role=' in idx:
    print("  OK: Accessibility attributes")
print("Done")
