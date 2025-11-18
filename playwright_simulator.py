import asyncio
import time
import random
import json
import websockets
from playwright.async_api import async_playwright
from simulator import AdvancedBehaviorDetector

class PlaywrightAgentSimulator:
    def __init__(self, human_like=True):
        self.human_like = human_like
        self.session_log = []
        self.detector = AdvancedBehaviorDetector()
        
    async def simulate_typing(self, page, selector, text):
        element = page.locator(selector)
        for char in text:
            await element.type(char)
            delay = random.uniform(80, 300) if self.human_like else random.uniform(10, 50)
            await asyncio.sleep(delay / 1000)
            self.session_log.append(("keystroke", time.time()))
    
    async def simulate_mouse_move(self, page, x, y):
        if self.human_like:
            # Human-like curved movement
            current = await page.evaluate("() => ({ x: window.mouseX || 0, y: window.mouseY || 0 })")
            steps = 10
            for i in range(steps):
                jitter_x = random.uniform(-2, 2)
                jitter_y = random.uniform(-2, 2)
                intermediate_x = current['x'] + (x - current['x']) * (i / steps) + jitter_x
                intermediate_y = current['y'] + (y - current['y']) * (i / steps) + jitter_y
                await page.mouse.move(intermediate_x, intermediate_y)
                await asyncio.sleep(random.uniform(10, 30) / 1000)
        else:
            # Bot-like direct movement
            await page.mouse.move(x, y)
        
        self.session_log.append(("mouse_move", (x, y), time.time()))
    
    async def browse_and_purchase(self, page):
        # Navigate to login
        await page.goto("file:///Users/aarij.hussaan/development/agent_detector_docker/agent_detector/mock_ecommerce.html")
        self.session_log.append(("page_view", "home", time.time()))
        
        if self.human_like:
            await asyncio.sleep(random.uniform(1, 3))
        
        # Login
        await self.simulate_typing(page, "#username", "testuser")
        await self.simulate_typing(page, "#password", "password123")
        
        login_btn = page.locator("button:has-text('Login')")
        await self.simulate_mouse_move(page, 100, 200)
        await login_btn.click()
        self.session_log.append(("login", time.time()))
        
        if self.human_like:
            await asyncio.sleep(random.uniform(1, 2))
        
        # Browse products
        self.session_log.append(("page_view", "products", time.time()))
        
        # Add to cart
        add_btn = page.locator("button:has-text('Add to Cart')").first
        await self.simulate_mouse_move(page, 200, 300)
        await add_btn.click()
        self.session_log.append(("add_to_cart", time.time()))
        
        if self.human_like:
            await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Checkout
        checkout_btn = page.locator("button:has-text('Checkout')")
        await self.simulate_mouse_move(page, 150, 400)
        await checkout_btn.click()
        self.session_log.append(("checkout", time.time()))
        
        return self.session_log

async def send_to_dashboard(detection_result, session_data):
    try:
        async with websockets.connect("ws://localhost:8080/ws") as websocket:
            message = {
                "type": "agent_detection",
                "result": detection_result,
                "session_data": session_data,
                "timestamp": time.time()
            }
            await websocket.send(json.dumps(message))
    except Exception as e:
        print(f"Failed to send to dashboard: {e}")

async def run_simulation():
    detector = AdvancedBehaviorDetector()
    
    # Train with some baseline human sessions
    human_sessions = []
    for _ in range(5):
        simulator = PlaywrightAgentSimulator(human_like=True)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            session = await simulator.browse_and_purchase(page)
            human_sessions.append(session)
            await browser.close()
    
    detector.train(human_sessions)
    
    # Test with both human and bot sessions
    test_cases = [
        ("Human", True),
        ("Bot", False),
        ("Human", True),
        ("Bot", False)
    ]
    
    for label, is_human in test_cases:
        simulator = PlaywrightAgentSimulator(human_like=is_human)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            session = await simulator.browse_and_purchase(page)
            prediction = detector.detect(session)
            
            print(f"Actual: {label}, Predicted: {prediction}")
            
            # Send to dashboard
            await send_to_dashboard(prediction, {
                "actual": label,
                "session_length": len(session),
                "features": detector.extract_features(session)
            })
            
            await browser.close()
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_simulation())