"""Git Helper AI MCP Server — Git analysis tools."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import re
import time
from datetime import datetime
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("git-helper-ai", instructions="MEOK AI Labs MCP Server")
_calls: dict[str, list[float]] = {}
DAILY_LIMIT = 50

def _rate_check(tool: str) -> bool:
    now = time.time()
    _calls.setdefault(tool, [])
    _calls[tool] = [t for t in _calls[tool] if t > now - 86400]
    if len(_calls[tool]) >= DAILY_LIMIT:
        return False
    _calls[tool].append(now)
    return True

@mcp.tool()
def parse_diff(diff_text: str, api_key: str = "") -> dict[str, Any]:
    """Parse a unified diff and extract structured change information."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("parse_diff"):
        return {"error": "Rate limit exceeded (50/day)"}
    files = []
    current_file = None
    additions = deletions = 0
    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            if current_file:
                files.append(current_file)
            m = re.search(r'b/(.+)$', line)
            current_file = {"file": m.group(1) if m else "unknown", "additions": 0, "deletions": 0, "hunks": 0, "changes": []}
        elif line.startswith("@@") and current_file:
            current_file["hunks"] += 1
        elif line.startswith("+") and not line.startswith("+++") and current_file:
            current_file["additions"] += 1
            additions += 1
        elif line.startswith("-") and not line.startswith("---") and current_file:
            current_file["deletions"] += 1
            deletions += 1
    if current_file:
        files.append(current_file)
    # Classify changes
    for f in files:
        ext = f["file"].rsplit(".", 1)[-1] if "." in f["file"] else ""
        f["extension"] = ext
        f["net_change"] = f["additions"] - f["deletions"]
        if f["additions"] > 0 and f["deletions"] == 0:
            f["change_type"] = "added"
        elif f["additions"] == 0 and f["deletions"] > 0:
            f["change_type"] = "removed"
        else:
            f["change_type"] = "modified"
    return {
        "files": [{k: v for k, v in f.items() if k != "changes"} for f in files],
        "file_count": len(files), "total_additions": additions, "total_deletions": deletions,
        "net_change": additions - deletions
    }

@mcp.tool()
def generate_commit_message(diff_text: str, style: str = "conventional", api_key: str = "") -> dict[str, Any]:
    """Generate a commit message from a diff. Styles: conventional, simple, detailed."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("generate_commit_message"):
        return {"error": "Rate limit exceeded (50/day)"}
    parsed = parse_diff.__wrapped__(diff_text) if hasattr(parse_diff, '__wrapped__') else parse_diff(diff_text)
    if "error" in parsed:
        return parsed
    files = parsed.get("files", [])
    if not files:
        return {"error": "No changes found in diff"}
    exts = set(f.get("extension", "") for f in files)
    adds = parsed["total_additions"]
    dels = parsed["total_deletions"]
    # Determine type
    if all(f.get("change_type") == "added" for f in files):
        ctype, verb = "feat", "add"
    elif all(f.get("change_type") == "removed" for f in files):
        ctype, verb = "chore", "remove"
    elif any(e in exts for e in ["test", "spec"]):
        ctype, verb = "test", "update"
    elif any(e in exts for e in ["md", "txt", "rst"]):
        ctype, verb = "docs", "update"
    elif adds > dels * 3:
        ctype, verb = "feat", "add"
    elif dels > adds * 3:
        ctype, verb = "refactor", "remove"
    else:
        ctype, verb = "fix", "update"
    file_names = [f["file"].split("/")[-1] for f in files[:3]]
    scope = files[0]["file"].split("/")[0] if files and "/" in files[0]["file"] else ""
    desc = f"{verb} {', '.join(file_names)}"
    if len(files) > 3:
        desc += f" and {len(files) - 3} more"
    if style == "conventional":
        msg = f"{ctype}({scope}): {desc}" if scope else f"{ctype}: {desc}"
    elif style == "simple":
        msg = desc.capitalize()
    else:
        msg = f"{ctype}: {desc}\n\nChanges:\n" + "\n".join(f"- {f['file']} (+{f['additions']}/-{f['deletions']})" for f in files)
    return {"message": msg, "type": ctype, "scope": scope, "files_changed": len(files), "additions": adds, "deletions": dels}

@mcp.tool()
def analyze_branch(log_text: str, api_key: str = "") -> dict[str, Any]:
    """Analyze git log output. Expects format: hash|author|date|message (one per line)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("analyze_branch"):
        return {"error": "Rate limit exceeded (50/day)"}
    commits = []
    authors: dict[str, int] = {}
    for line in log_text.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("|", 3)
        if len(parts) >= 4:
            h, author, date, msg = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
            commits.append({"hash": h[:8], "author": author, "date": date, "message": msg})
            authors[author] = authors.get(author, 0) + 1
    if not commits:
        return {"error": "No commits parsed. Expected format: hash|author|date|message"}
    # Classify commits
    types: dict[str, int] = {}
    for c in commits:
        msg = c["message"].lower()
        if msg.startswith("feat"): t = "feature"
        elif msg.startswith("fix"): t = "bugfix"
        elif msg.startswith("doc"): t = "docs"
        elif msg.startswith("test"): t = "test"
        elif msg.startswith("refactor"): t = "refactor"
        elif msg.startswith("chore"): t = "chore"
        else: t = "other"
        types[t] = types.get(t, 0) + 1
    top_authors = sorted(authors.items(), key=lambda x: -x[1])
    return {
        "commit_count": len(commits), "authors": dict(top_authors),
        "author_count": len(authors), "commit_types": types,
        "latest_commit": commits[0] if commits else None,
        "oldest_commit": commits[-1] if commits else None
    }

@mcp.tool()
def changelog_generator(log_text: str, version: str = "Unreleased", api_key: str = "") -> dict[str, Any]:
    """Generate a changelog from git log. Expects: hash|author|date|message per line."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("changelog_generator"):
        return {"error": "Rate limit exceeded (50/day)"}
    categories: dict[str, list[str]] = {"Features": [], "Bug Fixes": [], "Documentation": [], "Refactoring": [], "Tests": [], "Other": []}
    for line in log_text.strip().split("\n"):
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        h, author, date, msg = parts[0].strip()[:8], parts[1].strip(), parts[2].strip(), parts[3].strip()
        entry = f"- {msg} ({h})"
        ml = msg.lower()
        if ml.startswith("feat"): categories["Features"].append(entry)
        elif ml.startswith("fix"): categories["Bug Fixes"].append(entry)
        elif ml.startswith("doc"): categories["Documentation"].append(entry)
        elif ml.startswith("refactor"): categories["Refactoring"].append(entry)
        elif ml.startswith("test"): categories["Tests"].append(entry)
        else: categories["Other"].append(entry)
    md_parts = [f"# Changelog\n\n## [{version}]"]
    for cat, entries in categories.items():
        if entries:
            md_parts.append(f"\n### {cat}\n")
            md_parts.extend(entries)
    changelog = "\n".join(md_parts)
    total = sum(len(v) for v in categories.values())
    return {"changelog": changelog, "version": version, "total_entries": total, "categories": {k: len(v) for k, v in categories.items() if v}}

if __name__ == "__main__":
    mcp.run()
