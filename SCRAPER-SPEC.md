# Anthropic Documentation Scraper Specification

This document specifies the complete scraper implementation for downloading Anthropic documentation into a navigable local directory structure.

## Source Selection

**Use `llms.txt` files** (not `llms-full.txt`) for all three documentation sources:

| Source | llms.txt URL | Doc count |
|--------|--------------|-----------|
| platform.claude.com | https://platform.claude.com/llms.txt | ~530 |
| modelcontextprotocol.io | https://modelcontextprotocol.io/llms.txt | ~43 |
| code.claude.com | https://code.claude.com/docs/llms.txt | ~48 |

**Rationale**: llms.txt preserves section groupings and has complete URL lists. llms-full.txt loses section structure and is missing 1 document.

---

## Output Directory Structure

```
scraped-docs/
├── platform-claude-com/
│   ├── api/
│   │   ├── beta/
│   │   │   └── messages/
│   │   │       └── ...
│   │   └── ...
│   ├── agent-sdk/
│   ├── build-with-claude/
│   └── ...
├── modelcontextprotocol-io/
│   ├── specification/
│   │   └── 2025-11-25/
│   │       └── ...
│   ├── docs/
│   ├── community/
│   ├── clients.md          (root-level files stay at root)
│   └── examples.md
└── code-claude-com/
    ├── getting-started/
    ├── build-with-claude-code/
    ├── deployment/
    ├── administration/
    ├── configuration/
    ├── reference/
    ├── resources/
    └── misc/               (unmapped files)
```

---

## Directory Naming Convention

- **Lowercase with hyphens**: `Build with Claude Code` → `build-with-claude-code/`
- **Preserve original filenames**: `hooks-guide.md` stays as `hooks-guide.md`

---

## Source-Specific Rules

### 1. platform.claude.com

**URL pattern**: `https://platform.claude.com/docs/en/{path}.md`

**Directory derivation**: Strip `/docs/en/` prefix, use remaining path as directory structure.

**Example**:
- `https://platform.claude.com/docs/en/agent-sdk/overview.md` → `agent-sdk/overview.md`
- `https://platform.claude.com/docs/en/api/beta/messages/create.md` → `api/beta/messages/create.md`

**Root-level files**: Keep at root (e.g., `intro.md`, `get-started.md`)

**SDK Language Filtering**: Only download Python and TypeScript API examples.

Filter rules for API reference files:
- **KEEP**: Files without SDK language prefix (base API docs)
- **KEEP**: Files with `python_` or `typescript_` in path
- **SKIP**: Files with `go_`, `java_`, `kotlin_`, `ruby_` in path

Affected paths:
```
api/go_*           → SKIP
api/java_*         → SKIP
api/kotlin_*       → SKIP
api/ruby_*         → SKIP
api/python_*       → KEEP
api/typescript_*   → KEEP
api/*              → KEEP (no language prefix)
```

### 2. modelcontextprotocol.io

**URL pattern**: `https://modelcontextprotocol.io/{path}.md`

**Directory derivation**: Use path directly as directory structure.

**Example**:
- `https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle.md` → `specification/2025-11-25/basic/lifecycle.md`
- `https://modelcontextprotocol.io/docs/develop/build-server.md` → `docs/develop/build-server.md`

**Version paths**: KEEP version dates in paths (e.g., `2025-11-25/`) - this is important information.

**Root-level files**: Keep at root (e.g., `clients.md`, `examples.md`)

### 3. code.claude.com

**URL pattern**: `https://code.claude.com/docs/en/{filename}.md`

**Directory derivation**: URLs are flat (no subdirectories). Derive directory from `docs_map.md` section headers.

**docs_map.md location**: https://code.claude.com/docs/en/claude_code_docs_map.md

**Section-to-directory mapping**:

| docs_map.md Section | Directory Name |
|---------------------|----------------|
| Getting started | `getting-started/` |
| Build with Claude Code | `build-with-claude-code/` |
| Deployment | `deployment/` |
| Administration | `administration/` |
| Configuration | `configuration/` |
| Reference | `reference/` |
| Resources | `resources/` |

**File-to-section mapping** (derived from docs_map.md):

```
getting-started/
  overview.md
  quickstart.md
  common-workflows.md
  claude-code-on-the-web.md

build-with-claude-code/
  sub-agents.md
  plugins.md
  skills.md
  output-styles.md
  hooks-guide.md
  headless.md
  github-actions.md
  gitlab-ci-cd.md
  mcp.md
  migration-guide.md
  troubleshooting.md

deployment/
  third-party-integrations.md
  amazon-bedrock.md
  google-vertex-ai.md
  network-config.md
  llm-gateway.md
  devcontainer.md
  sandboxing.md

administration/
  setup.md
  iam.md
  security.md
  data-usage.md
  monitoring-usage.md
  costs.md
  analytics.md
  plugin-marketplaces.md

configuration/
  settings.md
  vs-code.md
  jetbrains.md
  terminal-config.md
  model-config.md
  memory.md
  statusline.md

reference/
  cli-reference.md
  interactive-mode.md
  slash-commands.md
  checkpointing.md
  hooks.md
  plugins-reference.md

resources/
  legal-and-compliance.md
```

**Unmapped files** (in llms.txt but not in docs_map.md) → `misc/`:
```
misc/
  chrome.md
  desktop.md
  discover-plugins.md
  microsoft-foundry.md
  slack.md
```

**Handling unmapped files programmatically**:
1. Parse docs_map.md to build file→section mapping
2. For each file in llms.txt, check if it exists in mapping
3. If not found, place in `misc/` directory

---

## Implementation Algorithm

```
1. For each source (platform, mcp, code):
   a. Fetch llms.txt
   b. Extract all .md URLs using regex
   c. Apply source-specific filtering (SDK languages for platform)
   d. For each URL:
      - Derive output path based on source rules
      - Create directory structure if needed
      - Download .md file to output path
   e. Report success/failure counts

2. Special handling for code.claude.com:
   a. Fetch and parse docs_map.md FIRST
   b. Build filename→section lookup table
   c. Use lookup for directory assignment
   d. Fallback to misc/ for unmapped files
```

---

## URL Extraction Patterns

```bash
# platform.claude.com
grep -oP 'https://platform\.claude\.com/docs/en/[^)]+\.md'

# modelcontextprotocol.io
grep -oP 'https://modelcontextprotocol\.io/[^)]+\.md'

# code.claude.com
grep -oP 'https://code\.claude\.com/docs/en/[^)]+\.md'
```

---

## Expected Output Statistics

After filtering:

| Source | Approx Files | Size |
|--------|--------------|------|
| platform-claude-com | ~200-250 (after SDK filtering) | ~10-15M |
| modelcontextprotocol-io | ~43 | ~1.2M |
| code-claude-com | ~48 | ~800K |

---

## Error Handling

- Log failed downloads but continue processing
- Report summary at end: successful, failed, skipped (filtered)
- Non-zero exit code if any downloads failed

---

## Verification

After scraping, verify:
1. No empty directories
2. All files have content (>0 bytes)
3. File counts match expected (after filtering)
4. Directory structure is correct (spot check)
