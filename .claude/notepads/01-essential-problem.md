# Ultrathink Page 1: The Essential Problem

## What Are We Really Doing?

Strip away the details. The core operation is:

```
INDEX → URLS → PATHS → FILES
```

Every source follows this exact pattern:
1. Fetch an index file (llms.txt)
2. Extract URLs from the index
3. Transform each URL into a local path
4. Download content to that path

## The Three Sources Are More Similar Than Different

| Source | Strip Prefix | Path Transform | Filter |
|--------|--------------|----------------|--------|
| platform | `/docs/en/` | identity | SDK langs |
| mcp | `/` | identity | none |
| code | `/docs/en/` | docs_map lookup | none |

**Key insight**: All three strip a prefix. Only one rewrites the directory. Only one filters.

## The Minimal Data Model

```python
Source = (name, llms_url, strip_prefix, path_rewriter, filter)
```

Where:
- `path_rewriter`: Optional[Callable[[Path], Path]]
- `filter`: Optional[Callable[[Path], bool]]

But wait... do we need callables? Let's think simpler.

## Even Simpler: Just Handle code.claude.com Specially

The spec already calls out code.claude.com as a "special case".
What if we embraced that instead of abstracting it away?

```python
for source in SOURCES:
    urls = extract(fetch(source.llms))
    docs_map = fetch_docs_map() if source.name == "code-claude-com" else None

    for url in urls:
        path = derive_path(url, source.strip, docs_map)
        if not skip_sdk(path, source.name):
            save(path, fetch(url))
```

This is ~10 lines of core logic. No abstractions. Crystal clear.

## Question: Is This Too Simple?

The Plan agent suggested 200+ lines with named functions, types, etc.
But the ACTUAL logic is maybe 50 lines.

What fills the other 150 lines?
- Progress output
- Error handling
- Summary reporting
- Verification

Are those essential? Let's examine...

## What's Truly Required

From SCRAPER-SPEC.md:
1. "Log failed downloads, continue processing" ✓ needed
2. "Report summary: successful, failed, skipped" ✓ needed
3. "Non-zero exit on any failures" ✓ needed
4. "Verify: no empty files" ✓ needed

So we DO need:
- Counters for success/fail/skip
- Print statements for progress
- A verification pass

But we DON'T need:
- Classes
- Complex type hierarchies
- Extensive abstraction

## The Beautiful Realization

The simplest correct implementation IS the most elegant one.
No need to add complexity to "future-proof" - the spec says everything is dynamic already.

---

Next: Sketch the actual code structure
