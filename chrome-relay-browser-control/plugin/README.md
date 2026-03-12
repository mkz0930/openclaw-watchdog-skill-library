# OpenClaw Browser Relay

让 AI 直接控制你已打开的 Chrome 浏览器，保留登录状态、Cookie、扩展插件，无需重新登录。

## 架构

```
AI Agent (Linux)
    │  WebSocket ws://localhost:19000
    ▼
relay server (server/server.py)
    │  WebSocket (Chrome Extension)
    ▼
Chrome Extension (extension/)
    │  Chrome Extension API
    ▼
Windows Chrome Browser
```

## 快速开始

### 第一步：启动 relay server（Linux/WSL）

```bash
cd server
pip install websockets
python3 server.py
```

输出：
```
🚀 OpenClaw Browser Relay Server
📡 Listening on: ws://localhost:19000
Waiting for connections...
```

> WSL 用户注意：Chrome 扩展需要连接 WSL 的 IP，不是 localhost。
> 查看 WSL IP：`ip addr show eth0 | grep "inet "`
> 然后修改 `extension/background.js` 第一行：`const WS_URL = "ws://172.x.x.x:19000";`

### 第二步：安装 Chrome 扩展（Windows）

1. 打开 Chrome → 地址栏输入 `chrome://extensions/`
2. 右上角开启**开发者模式**
3. 点击**加载已解压的扩展程序**
4. 选择本项目的 `extension/` 目录
5. 扩展图标出现在工具栏，徽章变绿 ✅ = 连接成功

### 第三步：AI 发送命令

```python
import asyncio, json, uuid, websockets

async def send_cmd(action, **kwargs):
    async with websockets.connect('ws://localhost:19000') as ws:
        await ws.send(json.dumps({'type': 'agent', 'version': '1.0.0'}))
        await ws.recv()  # welcome
        rid = str(uuid.uuid4())
        await ws.send(json.dumps({'action': action, 'request_id': rid, **kwargs}))
        return json.loads(await asyncio.wait_for(ws.recv(), timeout=30))

# 导航
asyncio.run(send_cmd('navigate', url='https://www.amazon.com'))

# 点击文字
asyncio.run(send_cmd('click_text', text='卖家精灵', exact=False))

# 截图
result = asyncio.run(send_cmd('screenshot', format='jpeg', quality=60))

# 读取页面文本
result = asyncio.run(send_cmd('get_text', selector='body'))
```

## 支持的命令

| 命令 | 参数 | 说明 |
|------|------|------|
| `navigate` | `url` | 跳转到指定 URL |
| `get_url` | — | 获取当前 URL 和标题 |
| `click` | `selector` | CSS 选择器点击 |
| `click_text` | `text`, `exact` | 按文字内容点击 |
| `click_xy` | `x`, `y` | 按坐标点击 |
| `type` | `selector`, `text` | 输入文字 |
| `get_text` | `selector`（可选） | 读取页面文本 |
| `get_html` | `selector`（可选） | 读取页面 HTML |
| `screenshot` | `format`, `quality` | 截图（返回 base64） |
| `scroll` | `x`, `y` | 滚动页面 |
| `wait` | `ms` | 等待毫秒 |
| `list_tabs` | — | 列出所有标签页 |
| `switch_tab` | `tab_id` 或 `index` | 切换标签页 |
| `new_tab` | `url` | 新建标签页 |
| `eval` | `code` | 执行 JavaScript（受 CSP 限制） |

## 注意事项

- **CSP 限制**：亚马逊等网站会拦截 `eval` 命令，改用 `click` / `get_text` / `screenshot`
- **扩展图标**：AI 无法点击 Chrome 工具栏的扩展图标，需用户手动操作
- **WSL IP**：每次重启 WSL 后 IP 可能变化，需更新 `background.js` 中的 `WS_URL`
- **端口**：server.py 监听 `19000`，background.js 也需配置为 `19000`

## 文件结构

```
├── extension/          # Chrome 扩展源码
│   ├── manifest.json   # 扩展配置（权限声明）
│   ├── background.js   # Service Worker，处理 WebSocket 和命令执行
│   ├── popup.html      # 点击扩展图标时显示的状态页
│   └── icon*.png       # 图标
├── server/
│   └── server.py       # WebSocket relay server（Python）
├── client/
│   └── browser_relay_plugin.py  # Python 客户端封装库
└── start-server.bat    # Windows 一键启动脚本
```

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 扩展徽章红色 | server 未启动 | 运行 `python3 server/server.py` |
| `No extension connected` | 扩展未连接 | 检查 background.js 的 WS_URL 是否正确 |
| `eval` 被拦截 | 页面 CSP 限制 | 改用 `click` / `get_text` |
| 命令超时 | 页面加载慢 | 增加 `timeout` 参数 |
| WSL 连不上 | IP 用了 localhost | 改为 WSL 实际 IP（`ip addr show eth0`）|
