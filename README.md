<div align="center">

# Git Helper Ai MCP

**Git Helper AI MCP Server — Git analysis tools.**

[![PyPI](https://img.shields.io/pypi/v/meok-git-helper-ai-mcp)](https://pypi.org/project/meok-git-helper-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Git Helper AI MCP Server — Git analysis tools.

## Tools

| Tool | Description |
|------|-------------|
| `parse_diff` | Parse a unified diff and extract structured change information. |
| `generate_commit_message` | Generate a commit message from a diff. Styles: conventional, simple, detailed. |
| `analyze_branch` | Analyze git log output. Expects format: hash|author|date|message (one per line). |
| `changelog_generator` | Generate a changelog from git log. Expects: hash|author|date|message per line. |

## Installation

```bash
pip install meok-git-helper-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "git-helper-ai": {
      "command": "python",
      "args": ["-m", "meok_git_helper_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
