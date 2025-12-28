# Anthropic Documentation Scraper

```
Usage: python scrape-ant-docs.py OUTPUT-PATH

Scrapes docs from platform.claude.com, modelcontextprotocol.io, and code.claude.com
into a navigable directory structure.

Arguments:
  OUTPUT-PATH   Output directory (required)

Options:
  -h, --help    Show this help message
```

## Output Structure

```
OUTPUT-PATH/
├── Claude-API-and-Agent-SDK/   # platform.claude.com
├── MCP/                        # modelcontextprotocol.io
└── Claude-Code/                # code.claude.com
```

---

```
                                    .md .md .md
                                   /   |   \
                              .md-/    |    \-.md
                                 /     |     \
            .---------------.   /      |      \   .---------------.
           / platform.claude \ /       |       \ / code.claude.com \
          '-------. .-------'|    .-------.    |'-------. .-------'
                   \|/       |   /         \   |       \|/
         .md--\  /--|--\  /--|--/           \--|--\  /--|--\  /--.md
               \/   |   \/   | /   _______   \ |   \/   |   \/
         .md--/\    |   /\   |/   /       \   \|   /\   |    /\--.md
              /  \--|--/  \--|   |  ^   ^  |   |--/  \--|--/  \
         .md-/      |      \ |   |    v    |   | /      |      \-.md
                    |       \|   |  \___/  |   |/       |
         .md--------+        \   |         |   /        +--------.md
                    |         \  \_________/  /         |
                    |          \             /          |
                    |           '-----+-----'           |
                    |                 |                 |
                    |            _____|_____            |
                    |           /           \           |
                    |          / modelcontext\          |
                    |         /   protocol.io \         |
                    |        '--------+--------'        |
                    |                 |                 |
                  .md                .md               .md

          ~ Claude, the 12-armed documentation harvester ~
```

---

*Crafted with curiosity and care,*
*—Claude* 🐾

