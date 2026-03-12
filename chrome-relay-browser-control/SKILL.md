---
name: Chrome Relay Browser Control
slug: chrome-relay-browser-control
version: 1.0.0
description: Control Windows Chrome browser via OpenClaw Browser Relay extension. Navigate pages, click elements, extract data, and operate third-party extensions like SellerSprite.
changelog: Initial release based on real session with Horse (2026-03-12). Covers relay setup, navigation, click strategies, screenshot workflow, and data extraction.
metadata: {"clawdbot":{"emoji":"🌐","requires":{"bins":["python3"],"paths":["/home/claw/.openclaw/extensions/openclaw-browser-relay/"]},"os":["linux"]}}
---

## Setup

On first use, read `setup.md` for relay server startup and Chrome extension pairing.

## When to Use

User wants AI to control their Windows Chrome browser — navigate URLs, click buttons, fill forms, extract page data, or operate Chrome extensions (e.g. SellerSprite / 卖家精灵).

## Architecture

```
OpenClaw (Linux) ──WebSocket──▶ relay server (port 19000)
                                       │
                               Chrome Extension (Windows)
                                       │
                               Windows Chrome Browser
```

The relay server bridges Linux AI commands to the Windows Chrome extension via WebSocket.

## Quick Reference

| Goal | Command pattern |
|------|----------------|
| Navigate to URL | `navigate` + url |
| Click by text | `click_text` + text |
| Click by coordinates | `click_xy` + x, y |
| Click by CSS selector | `click` + selector |
| Take screenshot | `screenshot` |
| Read page text | `get_text` |
| Check current URL | `get_url` |

## Core Rules

### 1. Always Verify Extension Connected First

Before any browser action, confirm the Chrome extension badge is green.

Ask user: "Chrome 插件徽章变绿了吗？" — only proceed after confirmation.

### 2. Use the Python WebSocket Client

All commands go through the relay server at `ws://localhost:19000`.

```python
import asyncio, json, uuid, websockets

async def send_cmd(action, **kwargs):
    async with websockets.connect('ws://localhost:19000') as ws:
        await ws.send(json.dumps({'type': 'agent', 'version': '1.0.0'}))
        await ws.recv()  # welcome message
        rid = str(uuid.uuid4())
        cmd = {'action': action, 'request_id': rid, **kwargs}
        await ws.send(json.dumps(cmd))
        return json.loads(await asyncio.wait_for(ws.recv(), timeout=30))

# Usage
result = asyncio.run(send_cmd('navigate', url='https://www.amazon.com'))
result = asyncio.run(send_cmd('click_text', text='卖家精灵', exact=False))
result = asyncio.run(send_cmd('screenshot', format='jpeg', quality=40))
```

Use venv: `/home/claw/.openclaw/workspace/.venv/bin/python3`

### 3. Click Strategy (in order of preference)

1. **click_text** — most reliable for visible text buttons
2. **click** with CSS selector — for checkboxes, inputs, known selectors
3. **click_xy** — last resort when text/selector fails; ask user for position hint

> ⚠️ Chrome extension toolbar icons CANNOT be clicked via relay. User must click them manually.

### 4. Screenshot Workflow

When unsure of page state or click result:
1. Take screenshot → save to `/home/claw/.openclaw/workspace/chrome_ssN.jpg`
2. Send via `message` tool to user's Feishu
3. Ask user to confirm or provide position hint

```python
result = asyncio.run(send_cmd('screenshot', format='jpeg', quality=40))
import base64
with open('/home/claw/.openclaw/workspace/chrome_ss.jpg', 'wb') as f:
    f.write(base64.b64decode(result['data'].split(',')[1]))
```

### 5. CSP Limitations

Amazon and many sites block `eval` via Content Security Policy.

- ❌ `eval` — blocked on amazon.com
- ✅ `click`, `click_text`, `click_xy`, `get_text`, `get_url`, `screenshot` — all work

### 6. Data Extraction

Use `get_text` to read SellerSprite / extension-injected data from DOM:

```python
result = asyncio.run(send_cmd('get_text', selector='body'))
text = result.get('text', '')
lines = [l.strip() for l in text.split('\n') if l.strip()]
# Parse lines for sales data, BSR, price, date listed, etc.
```

> Note: `get_html` on large pages (Amazon) may timeout. Use `get_text` instead.

## SellerSprite Workflow (卖家精灵)

Standard flow for extracting Amazon search data:

```
1. navigate  →  https://www.amazon.com/s?k={keyword}
2. click_text →  "卖家精灵"          (activates panel)
3. click      →  input[type="checkbox"]  (select all)
4. click_text →  "导出"              (export data)
5. get_text   →  body                (read injected data)
```

Key data fields injected by SellerSprite per product:
- BSR, 销量(父), 销售额, 价格, 评分, 评分数, 上架时间, 毛利率, FBA

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `tabs: []` | Extension not connected | Ask user to click Attach in extension |
| `running: false` | relay server down | Restart server (see setup.md) |
| click_xy returns undefined | Coordinates out of bounds | Ask user for position, try smaller x values |
| get_html timeout | Page too large | Use get_text instead |
| eval blocked | CSP restriction | Use click/get_text/screenshot |
