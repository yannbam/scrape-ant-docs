# Analysis: Hardcoded vs Dynamic

## First Principles Question

What is the MINIMUM information needed to scrape documentation that CANNOT be discovered at runtime?

---

## Layer 1: Entry Points (MUST be hardcoded)

These are the "bootstrap" URLs - you can't discover them dynamically:

```
platform.claude.com    → https://platform.claude.com/llms.txt
modelcontextprotocol.io → https://modelcontextprotocol.io/llms.txt
code.claude.com        → https://code.claude.com/docs/llms.txt
```

Also for code.claude.com:
```
docs_map.md → https://code.claude.com/docs/en/claude_code_docs_map.md
```

**TOTAL: 4 URLs that must be known in advance**

---

## Layer 2: URL Parsing (MUST understand format)

The llms.txt format uses markdown links: `[title](url)`

Regex pattern: `\[.*?\]\((https://[^)]+\.md)\)`

This is a STANDARD format - not source-specific.
**ONE pattern works for all three sources.**

---

## Layer 3: Path Transformation (CAN be algorithmic)

**platform.claude.com**:
- URL: `https://platform.claude.com/docs/en/agent-sdk/overview.md`
- Strip prefix: `/docs/en/`
- Result: `agent-sdk/overview.md`

The prefix `/docs/en/` could be:
- Hardcoded per source, OR
- Discovered by finding common prefix in all URLs

**modelcontextprotocol.io**:
- URL: `https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle.md`
- No stripping needed - use path directly
- Result: `specification/2025-11-25/basic/lifecycle.md`

**code.claude.com**:
- URL: `https://code.claude.com/docs/en/hooks.md`
- Strip prefix: `/docs/en/`
- But URLs are FLAT - need docs_map.md for directory structure

---

## Layer 4: Directory Derivation for code.claude.com

docs_map.md format:
```
## Section Name

### [filename](url)
```

Algorithm:
1. Parse docs_map.md
2. Extract section headers (## lines)
3. For each ### [name](url), associate with current section
4. Transform section name: "Getting started" → "getting-started"
5. Files not found in map → "misc/"

**NO hardcoding of section names or file lists needed!**

---

## Layer 5: SDK Language Filtering (POLICY, not data)

This is a USER PREFERENCE, not intrinsic to the data.

Options:
1. Command-line argument: `--sdk-langs python,typescript`
2. Config variable
3. Default to "all" if not specified

Detection: Files matching pattern `api/{language}_*` where language ∈ {python, typescript, go, java, kotlin, ruby}

**Can be parameterized, not hardcoded**

---

## Summary: What MUST be hardcoded?

### Absolute Minimum:
1. **Source entry points** (4 URLs)
2. **URL extraction regex** (1 pattern, shared)
3. **Output directory name per source** (3 strings)

### Everything else is DYNAMIC:
- File lists → parsed from llms.txt
- Directory structure → derived from URL paths or docs_map.md
- Section names → parsed from docs_map.md
- Section-to-directory transform → algorithmic (lowercase, hyphenate)
- Unmapped files → automatic fallback to misc/
- SDK filtering → parameterized

---

## The Elegant Design

```
SOURCES = [
  {
    name: "platform-claude-com",
    llms_url: "https://platform.claude.com/llms.txt",
    strip_prefix: "/docs/en/"
  },
  {
    name: "modelcontextprotocol-io",
    llms_url: "https://modelcontextprotocol.io/llms.txt",
    strip_prefix: ""
  },
  {
    name: "code-claude-com",
    llms_url: "https://code.claude.com/docs/llms.txt",
    strip_prefix: "/docs/en/",
    docs_map_url: "https://code.claude.com/docs/en/claude_code_docs_map.md"
  }
]
```

That's ~10 hardcoded strings total. Everything else flows from there.
