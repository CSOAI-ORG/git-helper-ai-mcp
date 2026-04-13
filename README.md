# git-helper-ai-mcp

MCP server for Git analysis tools.

## Tools

- **parse_diff** — Parse unified diffs into structured data
- **generate_commit_message** — Generate commit messages from diffs
- **analyze_branch** — Analyze git log for author stats and commit types
- **changelog_generator** — Generate changelogs from git logs

## Usage

```bash
pip install mcp
python server.py
```

## Rate Limits

50 calls/day per tool (free tier).
