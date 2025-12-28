# Ultrathink Page 3: Edge Cases & Robustness

## Edge Cases Analyzed

### 1. URL Prefix Mismatch
**Risk**: What if a URL doesn't start with the expected strip prefix?
**Analysis**: `str.removeprefix()` returns the original string if no match.
**Impact**: Path would include full URL → immediate visible error on save.
**Verdict**: ✅ Fails visibly, not silently.

### 2. docs_map.md Missing Entries
**Risk**: File in llms.txt not found in docs_map.md.
**Solution**: Fall back to "misc/" directory.
**Example**: `unknown.md` → `code-claude-com/misc/unknown.md`
**Verdict**: ✅ Handled by design.

### 3. SDK Filter Logic
**Pattern**: `^api/(go|java|kotlin|ruby)/`
**Verified against actual data**:
- `api/overview.md` → no language prefix → KEEP ✅
- `api/go/messages/create.md` → go/ → SKIP ✅
- `api/python/messages/create.md` → python/ → KEEP ✅
- `api/typescript/messages/create.md` → typescript/ → KEEP ✅
**Verdict**: ✅ Correct logic.

### 4. docs_map.md Format Edge Cases
**"# null" header on line 1**: Ignored (we look for `## ` sections).
**"## Document Structure" section**: Has no `### [file]` entries, doesn't pollute mapping.
**Verdict**: ✅ Parsing is robust.

### 5. Network Failures
**Handled by**: try/except around fetch() + save()
**Behavior**: Log to stderr, increment fail counter, continue
**Exit code**: Non-zero if any failures
**Verdict**: ✅ Per spec requirements.

### 6. Empty Files After Download
**Risk**: Download succeeds but content is empty (edge case).
**Solution**: Post-download verification loop checks file sizes.
**Verdict**: ✅ Verified at end.

### 7. Duplicate URLs in llms.txt
**Risk**: Same URL listed multiple times.
**Solution**: `dict.fromkeys()` preserves order, removes duplicates.
**Verdict**: ✅ Deduplicated.

## Assumptions That Are Safe

1. **All docs are UTF-8**: Anthropic uses modern tooling, this is safe.
2. **Clean filenames**: Official docs don't have weird characters.
3. **HTTPS only**: All sources use HTTPS, urllib handles this.
4. **No rate limiting**: ~500 small requests to Anthropic's own docs = fine.

## Things We Explicitly DON'T Handle (and why)

1. **Retries**: Simple scraper, not production service. Fail = fail.
2. **Concurrent downloads**: Adds complexity, minimal time savings.
3. **Progress bars**: Simple print statements are sufficient.
4. **Caching**: Run it fresh each time, it's fast.

## The Simplicity Principle

Every potential "improvement" I considered adding would:
- Add complexity without proportional value
- Make the script harder to understand
- Violate the KISS principle

The current design handles all realistic failure modes while staying under 120 lines.

---

Ready to write the final implementation plan.
