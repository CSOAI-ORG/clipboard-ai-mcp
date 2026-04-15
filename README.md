# Clipboard AI MCP Server

> By [MEOK AI Labs](https://meok.ai) — Clipboard history and smart paste operations

## Installation

```bash
pip install clipboard-ai-mcp
```

## Usage

```bash
python server.py
```

## Tools

### `get_clipboard`
Get current clipboard contents.

### `set_clipboard`
Set clipboard contents.

**Parameters:**
- `text` (str): Text to copy to clipboard

### `clipboard_history`
View clipboard history.

**Parameters:**
- `limit` (int): Number of entries (default 10)

### `smart_paste`
Smart paste with format conversion.

**Parameters:**
- `format` (str): Output format (default 'plain')

## Authentication

Free tier: 30 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
