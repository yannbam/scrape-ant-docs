# Anthropic Documentation Scraper Specification

## Design Principle

**Maximize dynamic behavior. Minimize hardcoding.**

The scraper must work without modification when:
- New documentation files are added
- Section names change
- Directory structures evolve
- New SDK languages are added

Only the absolute minimum should be hardcoded.

---

## Hardcoded Configuration (The Only Literals)

```bash
# Source configurations - THE ONLY HARDCODED DATA
SOURCES=(
  "platform-claude-com|https://platform.claude.com/llms.txt|https://platform.claude.com/docs/en/"
  "modelcontextprotocol-io|https://modelcontextprotocol.io/llms.txt|https://modelcontextprotocol.io/"
  "code-claude-com|https://code.claude.com/docs/llms.txt|https://code.claude.com/docs/en/"
)

# code.claude.com additionally needs:
DOCS_MAP_URL="https://code.claude.com/docs/en/claude_code_docs_map.md"

# Language filter 

From the different language examples on platform.claude.com only keep Python and Typescript

SDK_KEEP_LANGS="python|typescript"  # Set to ".*" to keep all
```

**Total hardcoded strings: 10** (3 per source + 1 docs_map URL + 1 filter pattern)

---

## Dynamic Behavior Specification

### 1. URL Extraction (Shared Algorithm)

Parse llms.txt using standard markdown link format:
```
Pattern: \[.*?\]\((https://[^)]+\.md)\)
```

This pattern works for ALL sources without modification.

### 2. Path Derivation (Per-Source Algorithm)

For each extracted URL, derive the output path:
```
output_path = url.removePrefix(strip_prefix)
```

**Example** (illustrative only):
- URL: `https://platform.claude.com/docs/en/agent-sdk/overview.md`
- Strip: `https://platform.claude.com/docs/en/`
- Result: `agent-sdk/overview.md`

The directory structure emerges naturally from the URL paths.

### 3. code.claude.com Directory Derivation (Special Case)

URLs for code.claude.com are flat (no subdirectories). Directory structure must be derived from `docs_map.md`.

**Algorithm:**
1. Fetch and parse docs_map.md
2. Build mapping: `filename → section_name` from the structure:
   ```
   ## Section Name
   ### [filename](url)
   ```
3. Transform section names to directory names:
   ```
   section_to_dirname(name):
     lowercase → replace spaces with hyphens → keep only [a-z0-9-]
   ```
4. Files not found in docs_map.md → place in `misc/` directory

**Example** (illustrative only):
- docs_map.md contains: `## Getting started` followed by `### [quickstart](...)`
- Result: `getting-started/quickstart.md`

### 4. SDK Language Filtering (Optional Policy)

For platform.claude.com API reference, filter by SDK language.

**Algorithm:**
```
if path matches "^api/[a-z]+_" AND NOT matches "^api/(SDK_KEEP_LANGS)_":
    skip this file
```

This keeps:
- All non-SDK-prefixed API docs (base reference)
- Only the specified SDK language variants

Set `SDK_KEEP_LANGS=".*"` to disable filtering and keep all languages.

---

## Implementation Requirements

### Must Be Dynamic:
- File lists (discovered from llms.txt at runtime)
- Directory creation (from URL paths)
- Section-to-directory mapping (parsed from docs_map.md)
- Unmapped file handling (automatic fallback)

### Must NOT Be Hardcoded:
- Individual file names or paths
- Section names or their mappings
- File counts or expected sizes
- Any content that could change when docs are updated

### Error Handling:
- Log failed downloads, continue processing
- Report summary: successful, failed, skipped
- Non-zero exit on any failures

---

## Output Structure

The output structure is EMERGENT from the source data, not predefined.

```
scraped-docs/
├── platform-claude-com/    # Structure mirrors URL paths
├── modelcontextprotocol-io/  # Structure mirrors URL paths
└── code-claude-com/        # Structure derived from docs_map.md
    └── misc/               # Unmapped files (auto-created if needed)
```

---

## Verification (Runtime Checks)

After scraping, verify:
1. No empty files (all downloaded files have content)
2. All extracted URLs were either downloaded or explicitly skipped
3. Directory structure was created successfully

Do NOT verify against hardcoded file counts - these will change.
