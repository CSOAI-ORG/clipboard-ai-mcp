<div align="center">

# Clipboard Ai MCP

**MCP server for clipboard ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-clipboard-ai-mcp)](https://pypi.org/project/meok-clipboard-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Clipboard Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `copy_text` | Copy text to the clipboard. Optionally add a label for easy retrieval. |
| `paste_text` | Retrieve the current clipboard contents. Format options: raw, trimmed, lines, js |
| `clipboard_history` | View clipboard history. Optionally search/filter by text content or label. |
| `clear_clipboard` | Clear the current clipboard. Optionally clear entire history. |

## Installation

```bash
pip install meok-clipboard-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "clipboard-ai": {
      "command": "python",
      "args": ["-m", "meok_clipboard_ai_mcp.server"]
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
