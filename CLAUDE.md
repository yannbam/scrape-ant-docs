# Anthropic Documentation Scraper

## Purpose

Scrape all available Anthropic documentation into a local copy with a directory structure and filenames that are **immediately navigable by Claude Code or agents**.

The goal: Claude can run `ls` on the scraped output, see the structure and filenames, and know exactly where to find specific documentation without grep/search guesswork.

## Usage

```bash
python scrape-ant-docs.py OUTPUT-PATH
python scrape-ant-docs.py --help
```

## Output Structure

```
OUTPUT-PATH/
  Claude-API-and-Agent-SDK/   # platform.claude.com (Python+TypeScript SDKs only)
  MCP/                        # modelcontextprotocol.io
  Claude-Code/                # code.claude.com
```

## Sources

| Site | Output Dir | Index URL |
|------|------------|-----------|
| platform.claude.com | Claude-API-and-Agent-SDK | llms.txt |
| modelcontextprotocol.io | MCP | llms.txt |
| code.claude.com | Claude-Code | llms.txt |

## Implementation Notes

- Fetches URLs from each site's `llms.txt` index
- Filters platform.claude.com to Python+TypeScript SDKs only (skips Go/Java/Kotlin/Ruby)
- Uses `docs_map.md` to organize Claude-Code docs into sections
- Purges only our directories on re-run (safe for shared output dirs)
- Line-buffered output for real-time progress when piped
- Graceful CTRL-C handling
