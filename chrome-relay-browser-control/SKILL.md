---
name: chrome-relay-browser-control
description: "控制 Windows Chrome 插件，打开网页、抓取亚马逊卖家精灵数据。重点：绕过 PortInUseError，用 Python WebSocket 命令。"
---

## 核心方案

### 1. 启动 server（Linux）

```bash
cd /home/claw/.openclaw/extensions/openclaw-browser-relay/server
./start-server.sh
```

### 2. Windows 插件操作

- 打开任意网页

- 图标绿 ✅（非红/闪烁）

### 3. 打开网页（只用 Python）

```python
import asyncio, websockets, json

async def cmd(action, **kwargs):
    async with websockets.connect('ws://localhost:19000') as ws:
        await ws.send(json.dumps({'type': 'agent', 'version': '1.0.0'}))
        await ws.recv()
        rid = str(asyncio.get_event_loop().time())
        await ws.send(json.dumps({'action': action, 'request_id': rid, **kwargs}))
        return json.loads(await asyncio.wait_for(ws.recv(), timeout=30))

# 打开亚马逊
r = asyncio.run(cmd('navigate', url='https://www.amazon.com/s?k=camping'))
```

### 4. 数据抓取

```python
# 激活卖家精灵
await cmd('click_text', text='卖家精灵')

# 读取 DOM 文本
r = await cmd('get_text', selector='body')
print(r.get('text'))
```

---

## ⚠️ 3 个必须绕过的坑

1. **`PortInUseError`**  
   `browser.*` OpenClaw 工具会报错 → 用 Python WS 命令代替

2. **`cdpHttp: false`**  
   表示插件没附加标签页 → 在 Windows 插件里点击「附加当前标签页」

3. **server 崩了**  
   用 `monitor.sh` 保活，或手动重启

---

## ✅ 验证流程

1. `ss -tlnp | grep :19000` → 看是否有 python3 监听
2. `python3 test_relay.py` → 看是否返回 `extension_online: true`
3. Windows 插件图标绿 ✅ + 弹窗显示 `connected`
