#!/usr/bin/env python3
"""
OpenClaw Browser Relay Client Plugin
Drop-in replacement for Playwright-based browser control

Usage:
  from openclaw_browser_relay import BrowserRelay
  
  browser = BrowserRelay()
  await browser.connect()
  
  # Navigate
  await browser.navigate("https://example.com")
  
  # Screenshot
  result = await browser.screenshot()
  
  # Click
  await browser.click("button#submit")
  
  # Type
  await browser.type("input#search", "hello")
  
  # Evaluate JS
  result = await browser.eval("document.title")
  
  await browser.close()
"""
import asyncio
import json
import uuid
import base64
import os
from typing import Optional, Dict, Any, List
import websockets

class BrowserRelay:
    def __init__(self, ws_url: str = "ws://localhost:19000", timeout: int = 30):
        self.ws_url = ws_url
        self.timeout = timeout
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self._pending: Dict[str, asyncio.Future] = {}
        
    async def connect(self) -> bool:
        """Connect to the Browser Relay server"""
        try:
            self.ws = await websockets.connect(self.ws_url, open_timeout=10)
            
            # Identify as agent
            await self.ws.send(json.dumps({
                "type": "agent",
                "version": "1.0.0"
            }))
            
            # Wait for welcome message
            welcome = await asyncio.wait_for(self.ws.recv(), timeout=5)
            welcome_data = json.loads(welcome)
            
            self.connected = True
            print(f"[BrowserRelay] ✅ Connected to {self.ws_url}")
            
            if not welcome_data.get("extension_online", False):
                print("[BrowserRelay] ⚠️ Warning: No Chrome extension connected")
                print("[BrowserRelay] 💡 Please install the OpenClaw Browser Relay extension")
            
            return True
            
        except Exception as e:
            print(f"[BrowserRelay] ❌ Connection failed: {e}")
            return False
    
    async def close(self):
        """Close the connection"""
        self.connected = False
        if self.ws:
            await self.ws.close()
            print("[BrowserRelay] 🔌 Disconnected")
    
    async def _send_command(self, action: str, params: Optional[Dict] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Send a command to the extension and wait for response"""
        if not self.connected or not self.ws:
            raise ConnectionError("Not connected to Browser Relay server")
        
        request_id = str(uuid.uuid4())
        cmd = {
            "action": action,
            "request_id": request_id,
            "timeout": timeout or self.timeout,
            **(params or {})
        }
        
        loop = asyncio.get_event_loop()
        fut = loop.create_future()
        self._pending[request_id] = fut
        
        try:
            await self.ws.send(json.dumps(cmd))
            result = await asyncio.wait_for(fut, timeout=timeout or self.timeout)
            
            if not result.get("ok", False):
                print(f"[BrowserRelay] ⚠️ Command '{action}' warning: {result.get('error', 'Unknown error')}")
            
            return result
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"Command '{action}' timed out after {timeout or self.timeout}s")
        finally:
            self._pending.pop(request_id, None)
    
    async def status(self) -> Dict[str, Any]:
        """Get current browser status"""
        return await self._send_command("status")
    
    async def navigate(self, url: str, wait_for_load: bool = True, timeout: int = 30000) -> Dict[str, Any]:
        """Navigate to a URL"""
        return await self._send_command("navigate", {
            "url": url,
            "waitForLoad": wait_for_load,
            "timeout": timeout
        })
    
    async def screenshot(self, format: str = "png", quality: int = 100, save_path: Optional[str] = None) -> Dict[str, Any]:
        """Take a screenshot of the current tab"""
        result = await self._send_command("screenshot", {
            "format": format,
            "quality": quality
        })
        
        if result.get("ok") and save_path and result.get("data"):
            # Save screenshot to file
            data = result["data"]
            b64 = data.split(",", 1)[1] if "," in data else data
            with open(save_path, "wb") as f:
                f.write(base64.b64decode(b64))
            result["saved_to"] = save_path
            print(f"[BrowserRelay] 📸 Screenshot saved to: {save_path}")
        
        return result
    
    async def get_url(self) -> Dict[str, Any]:
        """Get current tab URL and title"""
        return await self._send_command("get_url")
    
    async def get_text(self, selector: Optional[str] = None) -> Dict[str, Any]:
        """Get text content from the page"""
        return await self._send_command("get_text", {"selector": selector})
    
    async def get_html(self, selector: str = "body") -> Dict[str, Any]:
        """Get HTML content from the page"""
        return await self._send_command("get_html", {"selector": selector})
    
    async def click(self, selector: str, wait_for_navigation: bool = False) -> Dict[str, Any]:
        """Click an element"""
        return await self._send_command("click", {
            "selector": selector,
            "waitForNavigation": wait_for_navigation
        })
    
    async def click_xy(self, x: int, y: int) -> Dict[str, Any]:
        """Click at specific coordinates"""
        return await self._send_command("click_xy", {"x": x, "y": y})
    
    async def click_text(self, text: str, exact: bool = False) -> Dict[str, Any]:
        """Click element containing text"""
        return await self._send_command("click_text", {"text": text, "exact": exact})
    
    async def type(self, selector: str, text: str, clear: bool = True, delay: int = 0) -> Dict[str, Any]:
        """Type text into an input field"""
        return await self._send_command("type", {
            "selector": selector,
            "text": text,
            "clear": clear,
            "delay": delay  # ms between characters for slow typing
        })
    
    async def eval(self, code: str) -> Dict[str, Any]:
        """Execute JavaScript code"""
        return await self._send_command("eval", {"code": code})
    
    async def scroll(self, x: int = 0, y: int = 500, behavior: str = "smooth") -> Dict[str, Any]:
        """Scroll the page"""
        return await self._send_command("scroll", {"x": x, "y": y, "behavior": behavior})
    
    async def wait(self, ms: int = 1000) -> Dict[str, Any]:
        """Wait for specified milliseconds"""
        return await self._send_command("wait", {"ms": ms})
    
    async def list_tabs(self) -> Dict[str, Any]:
        """List all tabs in current window"""
        return await self._send_command("list_tabs")
    
    async def switch_tab(self, tab_id: Optional[int] = None, index: Optional[int] = None) -> Dict[str, Any]:
        """Switch to a different tab"""
        params = {}
        if tab_id is not None:
            params["tabId"] = tab_id
        elif index is not None:
            params["index"] = index
        return await self._send_command("switch_tab", params)
    
    async def close_tab(self, tab_id: Optional[int] = None) -> Dict[str, Any]:
        """Close a tab (defaults to current)"""
        return await self._send_command("close_tab", {"tabId": tab_id} if tab_id else {})
    
    async def new_tab(self, url: str = "about:blank", active: bool = True) -> Dict[str, Any]:
        """Open a new tab"""
        return await self._send_command("new_tab", {"url": url, "active": active})
    
    async def get_cookies(self, url: Optional[str] = None) -> Dict[str, Any]:
        """Get cookies for current or specified URL"""
        return await self._send_command("get_cookies", {"url": url} if url else {})
    
    async def set_cookies(self, cookies: List[Dict], url: Optional[str] = None) -> Dict[str, Any]:
        """Set cookies"""
        return await self._send_command("set_cookies", {"cookies": cookies, "url": url})
    
    async def download(self, url: str, filename: Optional[str] = None, save_as: bool = False) -> Dict[str, Any]:
        """Download a file"""
        return await self._send_command("download", {
            "url": url,
            "filename": filename,
            "saveAs": save_as
        })


# Convenience functions for direct use
async def connect(ws_url: str = "ws://localhost:9999") -> BrowserRelay:
    """Connect to Browser Relay and return instance"""
    browser = BrowserRelay(ws_url)
    await browser.connect()
    return browser


# CLI interface
if __name__ == "__main__":
    import sys
    
    async def cli():
        if len(sys.argv) < 2:
            print(__doc__)
            sys.exit(1)
        
        browser = BrowserRelay()
        if not await browser.connect():
            sys.exit(1)
        
        try:
            action = sys.argv[1]
            args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
            
            if hasattr(browser, action):
                result = await getattr(browser, action)(**args)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"Unknown action: {action}")
                sys.exit(1)
        finally:
            await browser.close()
    
    asyncio.run(cli())
