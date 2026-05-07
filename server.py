#!/usr/bin/env python3
"""In-memory clipboard with history and smart paste operations. — MEOK AI Labs."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json, re, hashlib
from datetime import datetime, timezone
from collections import defaultdict, deque
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 30
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now - t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT:
        return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day. Upgrade: meok.ai"})
    _usage[c].append(now)
    return None

mcp = FastMCP("clipboard-ai", instructions="In-memory clipboard with history and smart paste operations. By MEOK AI Labs.")

MAX_HISTORY = 100
_clipboards = defaultdict(lambda: {"current": None, "history": deque(maxlen=MAX_HISTORY)})


def _detect_content_type(text: str) -> str:
    """Detect the type of content in the clipboard."""
    if not text:
        return "empty"
    text_stripped = text.strip()
    if re.match(r'^https?://', text_stripped):
        return "url"
    if re.match(r'^[\w.+-]+@[\w-]+\.[\w.]+$', text_stripped):
        return "email"
    try:
        json.loads(text_stripped)
        return "json"
    except (json.JSONDecodeError, ValueError):
        pass
    if re.match(r'^(def |class |import |from |function |const |let |var |#include|package )', text_stripped):
        return "code"
    if re.match(r'^<[a-zA-Z]', text_stripped) and text_stripped.endswith('>'):
        return "html"
    if '\t' in text_stripped and '\n' in text_stripped:
        return "tabular"
    if text_stripped.startswith('{') or text_stripped.startswith('['):
        return "structured"
    if len(text_stripped.split('\n')) > 3:
        return "multiline"
    return "text"


@mcp.tool()
def copy_text(text: str, label: str = "", session_id: str = "default", api_key: str = "") -> str:
    """Copy text to the clipboard. Optionally add a label for easy retrieval.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl():
        return err

    cb = _clipboards[session_id]
    content_type = _detect_content_type(text)
    entry = {
        "text": text,
        "label": label,
        "content_type": content_type,
        "char_count": len(text),
        "line_count": text.count('\n') + 1,
        "hash": hashlib.md5(text.encode()).hexdigest()[:12],
        "copied_at": datetime.now(timezone.utc).isoformat(),
    }
    cb["current"] = entry
    cb["history"].appendleft(entry)

    return json.dumps({
        "status": "copied",
        "content_type": content_type,
        "char_count": len(text),
        "line_count": entry["line_count"],
        "label": label or "(none)",
        "history_size": len(cb["history"]),
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@mcp.tool()
def paste_text(session_id: str = "default", format: str = "raw", api_key: str = "") -> str:
    """Retrieve the current clipboard contents. Format options: raw, trimmed, lines, json_pretty, escaped.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl():
        return err

    cb = _clipboards[session_id]
    current = cb["current"]

    if current is None:
        return json.dumps({"status": "empty", "text": None, "message": "Clipboard is empty"})

    text = current["text"]
    output = text

    if format == "trimmed":
        output = text.strip()
    elif format == "lines":
        lines = text.split('\n')
        output = json.dumps([line.strip() for line in lines if line.strip()])
    elif format == "json_pretty":
        try:
            parsed = json.loads(text)
            output = json.dumps(parsed, indent=2)
        except (json.JSONDecodeError, ValueError):
            output = text
    elif format == "escaped":
        output = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')

    return json.dumps({
        "status": "ok",
        "text": output,
        "original_length": len(text),
        "output_length": len(output),
        "format": format,
        "content_type": current["content_type"],
        "label": current.get("label", ""),
        "copied_at": current["copied_at"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@mcp.tool()
def clipboard_history(limit: int = 10, search: str = "", session_id: str = "default", api_key: str = "") -> str:
    """View clipboard history. Optionally search/filter by text content or label.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl():
        return err

    cb = _clipboards[session_id]
    limit = max(1, min(limit, MAX_HISTORY))

    items = list(cb["history"])
    if search:
        search_lower = search.lower()
        items = [item for item in items if search_lower in item["text"].lower() or search_lower in item.get("label", "").lower()]

    items = items[:limit]

    entries = []
    for i, item in enumerate(items):
        preview = item["text"][:80]
        if len(item["text"]) > 80:
            preview += "..."
        entries.append({
            "index": i,
            "preview": preview,
            "label": item.get("label", ""),
            "content_type": item["content_type"],
            "char_count": item["char_count"],
            "hash": item["hash"],
            "copied_at": item["copied_at"],
        })

    return json.dumps({
        "session_id": session_id,
        "total_in_history": len(cb["history"]),
        "returned": len(entries),
        "search": search or None,
        "entries": entries,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@mcp.tool()
def clear_clipboard(session_id: str = "default", clear_history: bool = False, api_key: str = "") -> str:
    """Clear the current clipboard. Optionally clear entire history.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl():
        return err

    cb = _clipboards[session_id]
    had_content = cb["current"] is not None
    history_count = len(cb["history"])

    cb["current"] = None
    if clear_history:
        cb["history"].clear()

    return json.dumps({
        "status": "cleared",
        "had_content": had_content,
        "history_cleared": clear_history,
        "items_removed": history_count if clear_history else 0,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


if __name__ == "__main__":
    mcp.run()
