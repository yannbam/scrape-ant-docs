#!/usr/bin/env bash
# =============================================================================
# Simple Anthropic Documentation Scraper
# Downloads all docs from llms.txt files + Claude Code navigation
# =============================================================================

set -euo pipefail

OUTPUT_DIR="scraped-docs"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 Anthropic Documentation Scraper"
echo "Output directory: $OUTPUT_DIR"
echo ""

# -----------------------------------------------------------------------------
# 1. Platform Claude (Anthropic API/SDK docs)
# -----------------------------------------------------------------------------
echo "📚 [1/3] Scraping platform.claude.com (Anthropic API/SDK docs)..."
mkdir -p "$OUTPUT_DIR/platform-claude-com"

PLATFORM_URLS=$(curl -sL "https://platform.claude.com/llms.txt" | grep -oP 'https://platform\.claude\.com/docs/en/[^)]+\.md')
PLATFORM_COUNT=$(echo "$PLATFORM_URLS" | wc -l)
echo "   Found $PLATFORM_COUNT pages"

i=0
echo "$PLATFORM_URLS" | while read -r url; do
    i=$((i + 1))
    # Convert URL path to filename: /docs/en/agent-sdk/overview.md → agent-sdk_overview.md
    filename=$(echo "$url" | sed 's|https://platform.claude.com/docs/en/||; s|/|_|g')

    if curl -sL "$url" -o "$OUTPUT_DIR/platform-claude-com/$filename" --fail 2>/dev/null; then
        echo "   [$i/$PLATFORM_COUNT] ✓ $filename"
    else
        echo "   [$i/$PLATFORM_COUNT] ✗ FAILED: $filename"
    fi
done
echo -e "   ${GREEN}✓ Platform docs complete${NC}"

# -----------------------------------------------------------------------------
# 2. Model Context Protocol docs
# -----------------------------------------------------------------------------
echo ""
echo "📚 [2/3] Scraping modelcontextprotocol.io (MCP docs)..."
mkdir -p "$OUTPUT_DIR/modelcontextprotocol-io"

MCP_URLS=$(curl -sL "https://modelcontextprotocol.io/llms.txt" | grep -oP 'https://modelcontextprotocol\.io/[^)]+\.md')
MCP_COUNT=$(echo "$MCP_URLS" | wc -l)
echo "   Found $MCP_COUNT pages"

i=0
echo "$MCP_URLS" | while read -r url; do
    i=$((i + 1))
    # Convert URL path to filename
    filename=$(echo "$url" | sed 's|https://modelcontextprotocol.io/||; s|/|_|g')

    if curl -sL "$url" -o "$OUTPUT_DIR/modelcontextprotocol-io/$filename" --fail 2>/dev/null; then
        echo "   [$i/$MCP_COUNT] ✓ $filename"
    else
        echo "   [$i/$MCP_COUNT] ✗ FAILED: $filename"
    fi
done
echo -e "   ${GREEN}✓ MCP docs complete${NC}"

# -----------------------------------------------------------------------------
# 3. Claude Code docs
# -----------------------------------------------------------------------------
echo ""
echo "📚 [3/3] Scraping code.claude.com (Claude Code docs)..."
mkdir -p "$OUTPUT_DIR/code-claude-com"

## TO BE IMPLEMENTED

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "📊 SCRAPING COMPLETE"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Output: $OUTPUT_DIR/"
echo ""
echo "Files by source:"
find "$OUTPUT_DIR" -name "*.md" -type f | cut -d'/' -f2 | sort | uniq -c
echo ""
echo "Total files: $(find "$OUTPUT_DIR" -name "*.md" -type f | wc -l)"
echo "Total size:  $(du -sh "$OUTPUT_DIR" | cut -f1)"
echo ""
echo "✅ Done!"
