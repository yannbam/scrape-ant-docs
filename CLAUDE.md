# Anthropic Documentation Scraper

## Purpose

Scrape all available Anthropic documentation into a local copy with a directory structure and filenames that are **immediately navigable by Claude Code or agents**.

The goal: Claude can run `ls` on the scraped output, see the structure and filenames, and know exactly where to find specific documentation without grep/search guesswork.

## Current State

**`scrape-all-docs.sh`** - Basic scraper that downloads from llms.txt URLs. Outputs to `scraped-docs/` (gitignored).

**`llms-txt-sources/`** - Manually downloaded snapshot of the raw source files for reference/analysis. Not auto-generated.

## Open Questions

### 1. llms.txt vs llms-full.txt

- `llms.txt` provides URL index → requires fetching each .md file individually
- `llms-full.txt` contains all content inline → could parse/split programmatically

Which approach produces better results? The full.txt might have formatting/ordering that's useful.

### 2. Optimal Directory Structure

The structure must be:
- Programmatically extractable from the sources
- Self-documenting (Claude understands organization from filenames alone)
- Consistent across all three doc sources

Current approach flattens paths with underscores (`agent-sdk/overview.md` → `agent-sdk_overview.md`). Is hierarchical better?

### 3. claude_code_docs_map.md

Found at `code.claude.com/docs/en/claude_code_docs_map.md`. Contains navigation structure.

Unknown: Is this auto-generated from the same source as llms.txt, or does it contain additional organizational hints that could inform our directory structure?

## Sources

| Site | Index | Full Content |
|------|-------|--------------|
| platform.claude.com | llms.txt (55K) | llms-full.txt (27M) |
| modelcontextprotocol.io | llms.txt (5K) | llms-full.txt (848K) |
| code.claude.com | llms.txt (8K) | llms-full.txt (651K) |
