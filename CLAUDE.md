# Anthropic Documentation Scraper

## Purpose

Scrape all available Anthropic documentation into a local copy with a directory structure and filenames that are **immediately navigable by Claude Code or agents**.

The goal: Claude can run `ls` on the scraped output, see the structure and filenames, and know exactly where to find specific documentation without grep/search guesswork.

## Current State

**Scraper needs reimplementation** based on new specification.

- `SCRAPER-SPEC.md` - **Complete implementation specification** (all decisions made)
- `scrape-all-docs.sh` - Old version, needs rewrite per spec
- `scraped-docs/` - Old output (will be replaced)
- `llms-txt-sources/` - Raw source files for reference

## Key Decisions (documented in SCRAPER-SPEC.md)

1. **Source**: Use `llms.txt` (not llms-full.txt) - preserves section structure
2. **Directory structure**: Hierarchical, lowercase-hyphenated
3. **platform.claude.com**: Use URL paths, filter to Python+TypeScript SDKs only
4. **modelcontextprotocol.io**: Use URL paths directly (keep version dates)
5. **code.claude.com**: Derive directories from docs_map.md sections, unmapped→misc/

## Next Task

Implement scraper per `SCRAPER-SPEC.md`.

## Sources

| Site | Index | Full Content |
|------|-------|--------------|
| platform.claude.com | llms.txt (55K) | llms-full.txt (27M) |
| modelcontextprotocol.io | llms.txt (5K) | llms-full.txt (848K) |
| code.claude.com | llms.txt (8K) | llms-full.txt (651K) |
