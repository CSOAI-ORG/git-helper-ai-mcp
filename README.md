# Git Helper Ai

> By [MEOK AI Labs](https://meok.ai) — MEOK AI Labs MCP Server

Git Helper AI MCP Server — Git analysis tools.

## Installation

```bash
pip install git-helper-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install git-helper-ai-mcp
```

## Tools

### `parse_diff`
Parse a unified diff and extract structured change information.

**Parameters:**
- `diff_text` (str)

### `generate_commit_message`
Generate a commit message from a diff. Styles: conventional, simple, detailed.

**Parameters:**
- `diff_text` (str)
- `style` (str)

### `analyze_branch`
Analyze git log output. Expects format: hash|author|date|message (one per line).

**Parameters:**
- `log_text` (str)

### `changelog_generator`
Generate a changelog from git log. Expects: hash|author|date|message per line.

**Parameters:**
- `log_text` (str)
- `version` (str)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/git-helper-ai-mcp](https://github.com/CSOAI-ORG/git-helper-ai-mcp)
- **PyPI**: [pypi.org/project/git-helper-ai-mcp](https://pypi.org/project/git-helper-ai-mcp/)

## License

MIT — MEOK AI Labs
