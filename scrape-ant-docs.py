#!/usr/bin/env python3
"""
Anthropic Documentation Scraper

Scrapes documentation from three Anthropic sources into a navigable directory structure.
"""

import re
import shutil
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

USER_AGENT = "AnthropicDocsScraper/1.0 (https://github.com/anthropics)"

# ============================================================================
# CONFIGURATION (the only hardcoded values per SCRAPER-SPEC.md)
# ============================================================================

SOURCES = [
    # (dir_name, llms_url, strip_prefix)
    ("Claude-API-and-Agent-SDK", "https://platform.claude.com/llms.txt", "https://platform.claude.com/docs/en/"),
    ("MCP", "https://modelcontextprotocol.io/llms.txt", "https://modelcontextprotocol.io/"),
    ("Claude-Code", "https://code.claude.com/docs/llms.txt", "https://code.claude.com/docs/en/"),
]

# Directory names we create (for selective purging)
SOURCE_DIRS = [name for name, _, _ in SOURCES]

DOCS_MAP_URL = "https://code.claude.com/docs/en/claude_code_docs_map.md"
SDK_SKIP = re.compile(r"^api/(go|java|kotlin|ruby)/")


# ============================================================================
# UTILITIES
# ============================================================================

def fetch(url: str) -> str:
    """Fetch URL content as UTF-8 text."""
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def save(path: Path, content: str) -> None:
    """Write content to path, creating directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def extract_urls(text: str) -> list:
    """Extract unique markdown link URLs ending in .md, preserving order."""
    urls = re.findall(r'\[.*?\]\((https://[^)]+\.md)\)', text)
    return list(dict.fromkeys(urls))  # deduplicate while preserving order


def normalize(name: str) -> str:
    """Convert section name to directory name: 'Getting Started' -> 'getting-started'"""
    return re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-'))


def parse_docs_map(text: str) -> dict:
    """Parse docs_map.md into {filename: section_dir} mapping."""
    mapping = {}
    section = None
    for line in text.splitlines():
        # Detect section header: ## Section Name (but not ### subsection)
        if line.startswith("## ") and not line.startswith("### "):
            section = normalize(line[3:].strip())
        # Detect file reference: ### [filename](url)
        elif line.startswith("### [") and section:
            if m := re.match(r"### \[([^\]]+)\]", line):
                mapping[m.group(1)] = section
    return mapping


def derive_path(url: str, strip: str, docs_map: dict = None) -> Path:
    """Derive local output path from URL."""
    # Strip the prefix to get relative path
    rel = url.removeprefix(strip)

    # For code.claude.com: use docs_map to determine directory
    if docs_map is not None:
        stem = Path(rel).stem
        section = docs_map.get(stem, "misc")
        return Path(section) / f"{stem}.md"

    return Path(rel)


# ============================================================================
# MAIN
# ============================================================================

def show_help():
    """Display brief help message."""
    print("""Anthropic Documentation Scraper

Usage: python scrape.py OUTPUT-PATH

Scrapes docs from platform.claude.com, modelcontextprotocol.io, and code.claude.com
into a navigable directory structure.

Arguments:
  OUTPUT-PATH   Output directory (required)

Options:
  -h, --help    Show this help message
""")


def main() -> int:
    # Enable line buffering for piped output (fixes tee buffering issue)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    # Parse arguments
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "-h" in sys.argv or "--help" in sys.argv:
        show_help()
        return 0

    if not args:
        print("Error: OUTPUT-PATH is required\n", file=sys.stderr)
        show_help()
        return 1

    output_dir = Path(args[0])

    print("Anthropic Documentation Scraper")
    print(f"Output: {output_dir}/\n")

    # Purge only our specific directories (not the entire output dir)
    for dir_name in SOURCE_DIRS:
        target = output_dir / dir_name
        if target.exists():
            print(f"Purging {target}/...")
            shutil.rmtree(target)

    totals = {"ok": 0, "fail": 0, "skip": 0}
    results = []

    for i, (name, llms_url, strip) in enumerate(SOURCES, 1):
        print(f"[{i}/{len(SOURCES)}] {name}")

        # Fetch llms.txt and extract URLs
        try:
            urls = extract_urls(fetch(llms_url))
        except (URLError, HTTPError) as e:
            print(f"  ERROR: Failed to fetch llms.txt: {e}", file=sys.stderr)
            results.append((name, 0, 1, 0))
            totals["fail"] += 1
            continue

        print(f"  Found {len(urls)} URLs")

        # Fetch docs_map for Claude-Code
        docs_map = None
        if name == "Claude-Code":
            try:
                docs_map = parse_docs_map(fetch(DOCS_MAP_URL))
            except (URLError, HTTPError) as e:
                print(f"  WARNING: Failed to fetch docs_map.md, using misc/: {e}", file=sys.stderr)
                docs_map = {}

        ok = fail = skip = 0
        for j, url in enumerate(urls, 1):
            # Derive output path
            rel_path = derive_path(url, strip, docs_map)
            out_path = output_dir / name / rel_path

            # SDK language filter (Claude-API-and-Agent-SDK only)
            if name == "Claude-API-and-Agent-SDK" and SDK_SKIP.match(str(rel_path)):
                print(f"  [{j}/{len(urls)}] SKIP {rel_path}")
                skip += 1
                continue

            # Download and save
            try:
                content = fetch(url)
                save(out_path, content)
                print(f"  [{j}/{len(urls)}] OK   {rel_path}")
                ok += 1
            except Exception as e:
                print(f"  [{j}/{len(urls)}] FAIL {rel_path}: {e}", file=sys.stderr)
                fail += 1

        print(f"  -> {ok} OK, {fail} FAIL, {skip} SKIP\n")
        results.append((name, ok, fail, skip))
        totals["ok"] += ok
        totals["fail"] += fail
        totals["skip"] += skip

    # Summary
    print("=" * 60)
    print("Summary:")
    for name, ok, fail, skip in results:
        print(f"  {name}: {ok} OK, {fail} FAIL, {skip} SKIP")
    print(f"\nTOTAL: {totals['ok']} OK, {totals['fail']} FAIL, {totals['skip']} SKIP")

    # Verify no empty files
    empty_files = [f for f in output_dir.rglob("*.md") if f.stat().st_size == 0]
    if empty_files:
        print(f"\nERROR: {len(empty_files)} empty files found:", file=sys.stderr)
        for f in empty_files[:5]:
            print(f"  {f}", file=sys.stderr)
        if len(empty_files) > 5:
            print(f"  ... and {len(empty_files) - 5} more", file=sys.stderr)
        return 1

    print("\nDone!")
    return 1 if totals["fail"] else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user (CTRL-C)")
        sys.exit(130)  # Standard exit code for SIGINT
