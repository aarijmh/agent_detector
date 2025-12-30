#!/usr/bin/env python3
"""
CDP-based Agent - Direct Chrome DevTools Protocol control for native browser automation.
Bypasses Playwright/Selenium detection by controlling the browser directly.
"""

import asyncio
import json
import time
import random
import math
from typing import Dict, List, Tuple
import websockets
import httpx

class CDPAgent:
    """Chrome DevTools Protocol agent for native browser control"""
    
    def __init__(self, port: int = 9222):
        self.port = port
        self.session_id = str(time.time()).replace('.', '')
        self.collector_url = "http://localhost:8080/collect"
        self.challenge_url = "http://localhost:8080/challenge"
        self.ws = None
        self.msg_id = 0
        
    async def _get_ws_url(self) -> str:
        """Get WebSocket URL from Chrome"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    # Get list of tabs
                    response = await client.get(f"http://localhost:{self.port}/json")
                    tabs = response.json()
                    
                    # Find first available tab or create new one
                    for tab in tabs:
                        if tab.get("type") == "page" and "webSocketDebuggerUrl" in tab:
                            print(f"✓ Connected to Chrome tab on port {self.port}")
                            return tab["webSocketDebuggerUrl"]
                    
                    # Create new tab if none available
                    response = await client.put(f"http://localhost:{self.port}/json/new")
                    tab = response.json()
                    if "webSocketDebuggerUrl" in tab:
                        print(f"✓ Created new Chrome tab on port {self.port}")
                        return tab["webSocketDebuggerUrl"]
                    
                    raise ValueError("No webSocketDebuggerUrl available")
            except httpx.ConnectError:
                if attempt < max_retries - 1:
                    print(f"Connection attempt {attempt + 1}/{max_retries}: Chrome not responding on port {self.port}. Retrying...")
                    await asyncio.sleep(2)
                else:
                    print(f"\n❌ Cannot connect to Chrome on port {self.port}")
                    print(f"   Chrome is not running with remote debugging enabled.")
                    print(f"   Start Chrome with: chrome --remote-debugging-port={self.port} --user-data-dir=/tmp/chrome-debug")
                    raise
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}. Retrying...")
                    await asyncio.sleep(1)
                else:
                    print(f"\n❌ Failed to connect to Chrome on port {self.port}")
                    print(f"   Error: {e}")
                    print(f"   Make sure Chrome is running with: chrome --remote-debugging-port={self.port}")
                    raise
    
    async def _cdp_call(self, method: str, params: Dict = None, wait_response: bool = True) -> Dict:
        """Make a CDP method call"""
        if not self.ws:
            ws_url = await self._get_ws_url()
            self.ws = await websockets.connect(ws_url)
            # Enable required domains
            await self.ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
            await self._wait_for_response(1)
            await self.ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))
            await self._wait_for_response(2)
            await self.ws.send(json.dumps({"id": 3, "method": "Input.enable"}))
            await self._wait_for_response(3)
        
        self.msg_id += 1
        payload = {
            "id": self.msg_id,
            "method": method,
            "params": params or {}
        }
        
        try:
            await self.ws.send(json.dumps(payload))
            if wait_response:
                response = await self._wait_for_response(self.msg_id)
                if "error" in response:
                    print(f"CDP error for {method}: {response['error']}")
                return response
            return {}
        except Exception as e:
            print(f"CDP call failed: {e}")
            self.ws = None
            raise
    
    async def _wait_for_response(self, expected_id: int) -> Dict:
        """Wait for specific response ID, ignoring events"""
        while True:
            try:
                response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
                data = json.loads(response)
                
                # Return if this is the response we're waiting for
                if data.get("id") == expected_id:
                    return data
                
                # Ignore events (messages without 'id' field)
                if "id" not in data:
                    continue
            except asyncio.TimeoutError:
                print(f"Timeout waiting for response {expected_id}")
                raise

    async def _inject_stealth_scripts(self):
        """Inject scripts to hide automation indicators"""
        stealth_scripts = [
            "Object.defineProperty(navigator, 'webdriver', { get: () => false });",
            "Object.defineProperty(navigator, 'chrome', { get: () => ({ runtime: {} }) });",
            "Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });",
            "Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });",
        ]
        
        for script in stealth_scripts:
            await self._cdp_call("Runtime.evaluate", {
                "expression": script,
                "userGesture": True
            })

    async def navigate(self, url: str):
        """Navigate to URL"""
        result = await self._cdp_call("Page.navigate", {"url": url})
        print(f"Navigation result: {result}")
        
        if "error" in result:
            print(f"Navigation error: {result['error']}")
            return False
        
        # Wait for navigation to complete
        await asyncio.sleep(2)
        
        # Try basic document check
        try:
            doc_check = await self._cdp_call("Runtime.evaluate", {
                "expression": "typeof document",
                "returnByValue": True
            })
            print(f"Document check: {doc_check}")
            
            title_check = await self._cdp_call("Runtime.evaluate", {
                "expression": "document.title",
                "returnByValue": True
            })
            print(f"Document title: {title_check}")
        except Exception as e:
            print(f"Error checking document: {e}")
        
        print(f"✓ Navigation completed for {url}")
        return True

    async def type_text(self, selector: str, text: str, delay_ms: float = 100):
        """Type text with human-like delays"""
        await self._cdp_call("Runtime.evaluate", {
            "expression": f"document.querySelector('{selector}').focus();"
        })
        
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        for char in text:
            await self._cdp_call("Input.dispatchKeyEvent", {
                "type": "keyDown",
                "text": char,
                "unmodifiedText": char
            })
            
            await asyncio.sleep(random.uniform(delay_ms * 0.5, delay_ms * 1.5) / 1000)
            
            await self._cdp_call("Input.dispatchKeyEvent", {
                "type": "keyUp",
                "text": char,
                "unmodifiedText": char
            })

    async def move_mouse(self, x: float, y: float, steps: int = 20):
        """Move mouse with realistic curve"""
        current_x, current_y = 0, 0
        
        for i in range(steps):
            t = i / steps
            eased_t = t < 0.5 and 4*t**3 or 1-(-2*t+2)**3/2
            
            new_x = current_x + (x - current_x) * eased_t
            new_y = current_y + (y - current_y) * eased_t
            
            new_x += random.gauss(0, 0.5)
            new_y += random.gauss(0, 0.5)
            
            await self._cdp_call("Input.dispatchMouseEvent", {
                "type": "mouseMoved",
                "x": int(new_x),
                "y": int(new_y)
            }, wait_response=False)
            
            await asyncio.sleep(random.uniform(10, 30) / 1000)

    async def click(self, selector: str):
        """Click element with human-like behavior"""
        result = await self._cdp_call("Runtime.evaluate", {
            "expression": f"""
            (function() {{
                const el = document.querySelector('{selector}');
                if (!el) return null;
                const rect = el.getBoundingClientRect();
                return {{ x: rect.left + rect.width/2, y: rect.top + rect.height/2 }};
            }})()
            """,
            "returnByValue": True
        })
        
        if result.get("result", {}).get("result", {}).get("value"):
            pos = result["result"]["result"]["value"]
            
            await self.move_mouse(pos["x"], pos["y"], steps=random.randint(10, 20))
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            await self._cdp_call("Input.dispatchMouseEvent", {
                "type": "mousePressed",
                "x": int(pos["x"]),
                "y": int(pos["y"]),
                "button": "left",
                "clickCount": 1
            }, wait_response=False)
            
            await asyncio.sleep(random.uniform(50, 150) / 1000)
            
            await self._cdp_call("Input.dispatchMouseEvent", {
                "type": "mouseReleased",
                "x": int(pos["x"]),
                "y": int(pos["y"]),
                "button": "left"
            }, wait_response=False)

    async def get_page_content(self) -> str:
        """Get current page HTML"""
        try:
            result = await self._cdp_call("Runtime.evaluate", {
                "expression": "document.documentElement.outerHTML",
                "returnByValue": True
            })
           # print(f"Debug - get_page_content result: {result}")
            return result.get("result", {}).get("result", {}).get("value","")
        except Exception as e:
            print(f"Error getting page content: {e}")
            return ""

    async def wait_for_selector(self, selector: str, timeout: int = 5000):
        """Wait for element to appear"""
        start = time.time()
        while (time.time() - start) * 1000 < timeout:
            result = await self._cdp_call("Runtime.evaluate", {
                "expression": f"!!document.querySelector('{selector}')"
            })
            if result.get("result", {}).get("result",{}).get("value"):
                return True
            await asyncio.sleep(0.1)
        
        # Debug: show what's actually on the page
        html = await self.get_page_content()
        print(f"❌ Selector '{selector}' not found. Page content:")
        #print(html[:500] + "..." if len(html) > 500 else html)
        return False

    async def execute_script(self, script: str) -> any:
        """Execute arbitrary JavaScript"""
        result = await self._cdp_call("Runtime.evaluate", {
            "expression": script,
            "returnByValue": True
        })
        return result.get("result", {}).get("value")

    async def run_transaction(self, beneficiary: str, amount: str):
        """Execute transaction using CDP"""
        print(f"🔧 CDP Agent: Starting transaction {beneficiary} → {amount}")
        
        try:
            await self.navigate("http://localhost:3000")
            await self._inject_stealth_scripts()
            
            # Debug: Print page content
            html = await self.get_page_content()
           # print(f"\n📝 Page content:\n{html}\n")
            
            # Debug: Check what inputs exist
            inputs = await self._cdp_call("Runtime.evaluate", {
                "expression": "Array.from(document.querySelectorAll('input')).map(i => ({tag: i.tagName, name: i.name, id: i.id, type: i.type}))",
                "returnByValue": True
            })
            print(f"Available inputs: {inputs.get('result', {}).get('result',{}).get('value')}")
            
            # Fill beneficiary field
            beneficiary_selectors = [
                "input[name='beneficiary']",
                "input[name=beneficiary]", 
                "[name='beneficiary']"
            ]
            
            for selector in beneficiary_selectors:
                if await self.wait_for_selector(selector, timeout=5000):
                    await self.click(selector)
                    await self.type_text(selector, beneficiary)
                    print("✅ Successfully filled beneficiary field")
                    break
            
            # Fill amount field
            amount_selectors = [
                "input[name='amount']",
                "input[name=amount]",
                "[name='amount']"
            ]
            
            for selector in amount_selectors:
                if await self.wait_for_selector(selector, timeout=5000):
                    await self.click(selector)
                    await self.type_text(selector, amount)
                    print("✅ Successfully filled amount field")
                    break
            
            # Click submit button
            if await self.wait_for_selector("button[type=submit]", timeout=5000):
                await self.click("button[type=submit]")
                print("✅ Successfully clicked Authorize Payment button")
                
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    agent = CDPAgent(port=9222)
    
    try:
        await agent.run_transaction(
            beneficiary="AE 1234 5678 7890 1234",
            amount="25000"
        )
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Ensure Chrome is running with --remote-debugging-port=9222")


if __name__ == "__main__":
    asyncio.run(main())
