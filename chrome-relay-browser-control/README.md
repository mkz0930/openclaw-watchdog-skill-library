# Chrome Relay 浏览器控制（自研插件版）

## ⚠️ 重要说明：这是自研插件，不是官方 relay！

- 官方 relay：`OpenClaw Browser Relay`（拓展商店安装）
- 本插件：自研插件（端口 19000，支持navigate/open等命令）

---

## ✅ 完整工作流（4 步）

### 1️⃣ 启动 Linux server（保活）

```bash
cd /home/claw/.openclaw/extensions/openclaw-browser-relay/server
./start-server.sh
# 自动后台运行 + 10秒监控
# 日志：server.log, monitor.log
```

**验证：**
```bash
ss -tlnp | grep :19000
# 应看到 python3 监听
```

---

### 2️⃣ Windows Chrome 插件配置

1. 安装自研 Chrome 插件（.crx 或开发者模式加载）
2. 打开任意页面（如 `amazon.com`）
3. 点击插件图标 → **关闭“自动重连”**（会掉线！）
4. 手动点击 **「附加当前标签页」**（或直接输入亚马逊 URL）
5. 确认插件图标变绿 ✅（非闪烁）

**验证：**
- Windows Chrome 任务管理器 → 扩展进程
- 或查看插件弹窗是否显示 “已连接 172.25.4.135:19000”

---

### 3️⃣ 打开网页（3种方式）

#### 方式A：针式插件打开（推荐 ✅）

**Windows Chrome 插件里有“打开 URL”按钮 → 点击**

#### 方式B：Python WebSocket 发送 `navigate`（推荐 ✅）

```python
# test_relay.py
import asyncio, websockets, json

async def cmd(action, **kwargs):
    async with websockets.connect('ws://localhost:19000') as ws:
        await ws.send(json.dumps({'type': 'agent', 'version': '1.0.0'}))
        await ws.recv()  # welcome
        rid = str(asyncio.get_event_loop().time())
        await ws.send(json.dumps({'action': action, 'request_id': rid, **kwargs}))
        return json.loads(await asyncio.wait_for(ws.recv(), timeout=30))

# Usage
r = asyncio.run(cmd('navigate', url='https://www.amazon.com/s?k=camping'))
print(r)
```

✅ **已验证可用！**

#### 方式C：Python WebSocket 发送 `open`

```python
# 注意！本插件不支持 'open' 命令
# 只能用 'navigate' 或直接在插件里输入 URL
```

❌ `browser.open` OpenClaw 工具会报 `PortInUseError`（尽管 server 正常）
→ **绕过方式：用 Python 脚本直接发 WS 命令**

---

### 4️⃣ 数据抓取（4种方式）

#### 方式A：直接截图（失败 ❌）

```python
r = asyncio.run(cmd('screenshot', format='jpeg', quality=40))
# 可能返回 ok: true 但 data 为空
# 推荐：在 Windows Chrome 里截屏
```

#### 方式B：读取 DOM 文本（推荐 ✅）

```python
r = asyncio.run(cmd('get_text', selector='body'))
text = r.get('text', '')
# 解析卖家精灵注入的数据
```

#### 方式C：点击按钮（推荐 ✅）

```python
r = asyncio.run(cmd('click_text', text='卖家精灵', exact=False))
# 激活卖家精灵面板
```

#### 方式D：在 Windows Chrome 截图 → 手动发图

Best practice：Windows Chrome 截图 → 微信/飞书发给你 → 你分析数据

---

## ⚠️ 5 个常见坑（实战经验）

| 问题 | 症状 | 解决 |
|------|------|------|
| **1. server 崩了** | `cdpHttp: false`, 插件重连失败 | `./start-server.sh` 重启 |
| **2. 插件重连太多** | 插件弹窗闪 `connecting...` | Windows Chrome 关闭插件重开 |
| **3. `PortInUseError`** | `browser.*` 工具报错，但 Python WS 成功 | **忽略，用 Python 脚本代替** |
| **4. `tabs: []`** | 插件未附加标签页 | 点击插件图标 → 「附加当前标签页」 |
| **5. 端口冲突** | `ss -tlnp` 显示多个 python3 | `pkill -9 -f "server.py"` → 重开 |

---

## 🛠️ 故障排查清单

1. **Linux server 是否运行？**
   ```bash
   ps aux | grep server.py | grep -v grep
   # 应有 python3 server.py 进程
   ```

2. **端口是否监听？**
   ```bash
   ss -tlnp | grep :19000
   # 应有 TCP *:19000 (LISTEN)
   ```

3. **Windows 插件是否Attach？**
   - 插件图标绿 ✅（非红/闪烁）
   - 弹窗显示 `connected to 172.25.4.135:19000`

4. **是否用 `navigate` 打开页面？**
   - ✅ Python `cmd('navigate', url=...)`
   - ✅ Windows 插件按钮打开
   - ❌ 不要用 OpenClaw `browser.open`（会报错）

---

## 📠 相关文件

| 文件 | 说明 |
|------|------|
| `server.py` | WebSocket relay server |
| `background.js` | Chrome extension logic |
| `start-server.sh` | 启动脚本（nohup + monitor.sh） |
| `test_relay.py` | 直接发送命令的测试脚本 |
| `do-amazon.py` | 完整亚马逊抓取示例 |

---

## ✅ 最佳实践

1. **Server 一定要保活**：`nohup python3 server.py & > server.log 2>&1` + `monitor.sh`
2. **第一次用一定要验证**：`python3 test_relay.py` → 看 `welcome` + `extension_online: true`
3. **避免 OpenClaw 工具**：`browser.*` 全部跳过，用 Python WS
4. **截图用 Windows**：插件在 Windows，截图用 `Win+Shift+S`+发图

---

## 📝 备注

- 插件端口：`19000`（固定）
- server IP：`172.25.4.135`（需插件配置匹配）
- 插件协议：自研 WebSocket，不兼容官方 relay
