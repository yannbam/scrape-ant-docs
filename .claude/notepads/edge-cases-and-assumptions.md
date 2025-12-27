# Edge Cases and Assumptions Analysis

## Challenging the Dynamic Design

### Assumption 1: llms.txt format is stable
**Risk**: Low - this is a standard format
**Mitigation**: Regex is simple, could be overridden per source if needed

### Assumption 2: docs_map.md format is stable
**Risk**: Low - auto-generated, simple structure
**Mitigation**: Parser is straightforward (## sections, ### [file](url))

### Assumption 3: Section names → directory names transformation
**Risk**: Medium - special characters?
**Example**: "C++ Guide" → "c++-guide" → INVALID
**Mitigation**: Sanitize to [a-z0-9-] only

Transformation algorithm:
```
section_to_dirname(name):
  1. lowercase
  2. replace spaces with hyphens
  3. remove any character not in [a-z0-9-]
  4. collapse multiple hyphens
```

### Assumption 4: SDK language detection via URL path
**Current pattern**: `api/python_*`, `api/go_*`
**Risk**: Medium - if pattern changes
**Better approach**: Make the PATTERN configurable, not the language list

```
sdk_filter_pattern: "api/({langs})_"
sdk_langs: "python|typescript"  # or "all" for no filtering
```

### Assumption 5: strip_prefix is stable
**Observation**: `/docs/en/` is the English language path
**Risk**: Low if we only want English
**Flexibility**: Could parameterize: `--lang en`

---

## What CAN'T be dynamic?

1. **Source existence** - You can't discover sources you don't know about
2. **Entry point URLs** - The bootstrap problem
3. **Output directory names** - User expectation (could be derived from domain, but explicit is clearer)

---

## Refined Configuration Model

```
SOURCE_CONFIG = {
  "platform-claude-com": {
    "llms_url": "https://platform.claude.com/llms.txt",
    "url_prefix_strip": "https://platform.claude.com/docs/en/",
    "sdk_filter": {
      "pattern": "^api/(go|java|kotlin|ruby)_",
      "action": "exclude"
    }
  },
  "modelcontextprotocol-io": {
    "llms_url": "https://modelcontextprotocol.io/llms.txt",
    "url_prefix_strip": "https://modelcontextprotocol.io/"
  },
  "code-claude-com": {
    "llms_url": "https://code.claude.com/docs/llms.txt",
    "url_prefix_strip": "https://code.claude.com/docs/en/",
    "docs_map_url": "https://code.claude.com/docs/en/claude_code_docs_map.md",
    "unmapped_dir": "misc"
  }
}
```

**Key insight**: The SDK filter is an EXCLUSION pattern, not an inclusion list.
This is more future-proof - if a new language is added, it gets excluded by default.

Wait, that's backwards. We want Python and TypeScript only.

Better: INCLUSION pattern
```
"sdk_filter": {
  "pattern": "^api/(?!python_|typescript_)[a-z]+_",
  "action": "exclude"
}
```

Or even simpler - just specify what to KEEP:
```
"sdk_keep_pattern": "^api/(python_|typescript_|[^_]+$)"
```

This keeps:
- api/python_*
- api/typescript_*
- api/anything-without-underscore (base API docs)

---

## Final Hardcoded Count

**Truly hardcoded (per source):**
- llms_url (1 string)
- url_prefix_strip (1 string)
- output_dir_name (1 string)

**Optional per source:**
- docs_map_url (code.claude.com only)
- sdk_filter pattern (platform.claude.com only)
- unmapped_dir name (code.claude.com only)

**Shared/algorithmic:**
- URL extraction regex (1 pattern)
- Section-to-dirname transformation (algorithm)
- Directory creation (automatic from paths)
