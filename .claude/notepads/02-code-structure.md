# Ultrathink Page 2: Code Structure

## The Skeleton

```python
#!/usr/bin/env python3
"""Anthropic Documentation Scraper - downloads docs with navigable structure."""

import re, sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

# ============================================================================
# CONFIGURATION (the only hardcoded values per SCRAPER-SPEC.md)
# ============================================================================

SOURCES = {
    "platform-claude-com": {
        "llms": "https://platform.claude.com/llms.txt",
        "strip": "https://platform.claude.com/docs/en/",
    },
    "modelcontextprotocol-io": {
        "llms": "https://modelcontextprotocol.io/llms.txt",
        "strip": "https://modelcontextprotocol.io/",
    },
    "code-claude-com": {
        "llms": "https://code.claude.com/docs/llms.txt",
        "strip": "https://code.claude.com/docs/en/",
    },
}

DOCS_MAP_URL = "https://code.claude.com/docs/en/claude_code_docs_map.md"
SDK_SKIP = re.compile(r"^api/(go|java|kotlin|ruby)/")
OUTPUT_DIR = Path("scraped-docs")

# ============================================================================
# UTILITIES
# ============================================================================

def fetch(url): ...
def save(path, content): ...
def extract_urls(text): ...
def normalize(name): ...
def parse_docs_map(text): ...

# ============================================================================
# MAIN
# ============================================================================

def main():
    # ... process each source
    # ... print summary
    # ... verify and exit

if __name__ == "__main__":
    sys.exit(main())
```

## Function Bodies (Minimal)

### fetch(url) → str
```python
def fetch(url):
    """Fetch URL content as UTF-8 text."""
    with urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8")
```

### save(path, content)
```python
def save(path, content):
    """Write content to path, creating directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
```

### extract_urls(text) → list[str]
```python
def extract_urls(text):
    """Extract markdown link URLs ending in .md"""
    return re.findall(r'\[.*?\]\((https://[^)]+\.md)\)', text)
```

Wait - this returns duplicates. Need dedup:
```python
def extract_urls(text):
    """Extract unique markdown link URLs ending in .md"""
    return list(dict.fromkeys(re.findall(r'\[.*?\]\((https://[^)]+\.md)\)', text)))
```

### normalize(name) → str
```python
def normalize(name):
    """'Getting Started' → 'getting-started'"""
    return re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-'))
```

### parse_docs_map(text) → dict
```python
def parse_docs_map(text):
    """Parse docs_map.md into {filename: section_dir} mapping."""
    mapping = {}
    section = None
    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            section = normalize(line[3:].strip())
        elif line.startswith("### [") and section:
            if m := re.match(r"### \[([^\]]+)\]", line):
                mapping[m.group(1)] = section
    return mapping
```

## Main Loop - Two Approaches

### Approach A: Inline everything (very compact)
```python
def main():
    print("Anthropic Documentation Scraper\n")

    totals = {"ok": 0, "fail": 0, "skip": 0}

    for i, (name, cfg) in enumerate(SOURCES.items(), 1):
        print(f"[{i}/3] {name}")

        urls = extract_urls(fetch(cfg["llms"]))
        docs_map = parse_docs_map(fetch(DOCS_MAP_URL)) if name == "code-claude-com" else None

        ok = fail = skip = 0
        for j, url in enumerate(urls, 1):
            # Derive path
            rel = url.removeprefix(cfg["strip"])
            if docs_map:
                stem = Path(rel).stem
                rel = f"{docs_map.get(stem, 'misc')}/{stem}.md"
            path = OUTPUT_DIR / name / rel

            # SDK filter (platform only)
            if name == "platform-claude-com" and SDK_SKIP.match(rel):
                print(f"  [{j}/{len(urls)}] SKIP {rel}")
                skip += 1
                continue

            # Download
            try:
                save(path, fetch(url))
                print(f"  [{j}/{len(urls)}] OK   {rel}")
                ok += 1
            except Exception as e:
                print(f"  [{j}/{len(urls)}] FAIL {rel}: {e}", file=sys.stderr)
                fail += 1

        print(f"  → {ok} OK, {fail} FAIL, {skip} SKIP\n")
        totals["ok"] += ok
        totals["fail"] += fail
        totals["skip"] += skip

    # Summary
    print(f"TOTAL: {totals['ok']} OK, {totals['fail']} FAIL, {totals['skip']} SKIP")

    # Verify no empty files
    empty = [f for f in OUTPUT_DIR.rglob("*.md") if f.stat().st_size == 0]
    if empty:
        print(f"ERROR: {len(empty)} empty files found", file=sys.stderr)
        return 1

    return 1 if totals["fail"] else 0
```

This is ~45 lines for main(). Total script: ~90 lines.

**Too compact?** Maybe. The inner loop is doing a lot.

### Approach B: Extract path derivation (slightly more readable)
```python
def derive_path(url, strip, docs_map):
    """Derive local path from URL."""
    rel = url.removeprefix(strip)
    if docs_map:
        stem = Path(rel).stem
        return Path(docs_map.get(stem, "misc")) / f"{stem}.md"
    return Path(rel)
```

Then main becomes:
```python
path = derive_path(url, cfg["strip"], docs_map)
```

More readable. Let's go with B.

## The Beautiful Insight

The entire script is ~100-120 lines:
- 20 lines: imports + config
- 30 lines: 5 utility functions
- 50 lines: main loop with progress output
- 10 lines: summary + verification

No classes. No complex abstractions. Just clear, linear code.

---

Next: Think about edge cases and potential issues
