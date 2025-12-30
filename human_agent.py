#!/usr/bin/env python3
"""
Human-like Agent using realistic behavioral patterns to evade detection.
"""

import asyncio
import json
import time
import random
import math
from typing import List, Dict, Tuple
import httpx

class HumanLikeAgent:
    def __init__(self, headless=False):
        self.headless = headless
        self.session_id = str(time.time()).replace('.', '')
        self.collector_url = "http://localhost:8080/collect"
        self.challenge_url = "http://localhost:8080/challenge"
        
    async def send_telemetry(self, mouse_events: List[Dict], key_events: List[Dict], 
                            amount: str, beneficiary: str, new_beneficiary: bool = False,
                            paste_count: int = 0):
        """Send behavioral telemetry to collector"""
        payload = {
            "session_id": self.session_id,
            "ts": time.time(),
            "channel": "web",
            "env": {
                "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "lang": "en-US",
                "tz": "America/New_York",
                "platform": "MacIntel",
                "hwc": 8,
                "screen": {"w": 1920, "h": 1080, "dpr": 1}
            },
            "behavior": {
                "mouse": mouse_events[-800:],
                "keys": key_events[-400:],
                "paste_count": paste_count
            },
            "journey": {
                "amount": amount,
                "beneficiary": beneficiary,
                "new_beneficiary": new_beneficiary
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.collector_url, json=payload)
            return response.json()

    def _generate_mouse_path(self, start: Tuple[float, float], 
                            end: Tuple[float, float]) -> List[Dict]:
        """Generate realistic mouse movement with minimal curve"""
        mouse_events = []
        base_time = time.time() * 1000
        cumulative_time = 0
        
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx*dx + dy*dy)
        steps = max(25, int(distance / 4))
        
        for i in range(steps):
            t = i / steps
            x = start[0] + dx * t + random.gauss(0, 1.2)
            y = start[1] + dy * t + random.gauss(0, 1.2)
            
            dt = random.uniform(18, 40)
            cumulative_time += dt
            
            mouse_events.append({
                "x": round(x, 2),
                "y": round(y, 2),
                "t": base_time + cumulative_time,
                "dt": dt
            })
        
        return mouse_events

    def _generate_keystroke_events(self, text: str, base_time: float) -> List[Dict]:
        """Generate realistic keystroke events with natural timing"""
        events = []
        current_time = base_time
        
        for char in text:
            iki = random.uniform(120, 280)
            current_time += iki
            dwell = random.uniform(50, 130)
            
            events.append({
                "k": char,
                "t": current_time,
                "dwell": dwell
            })
        
        return events

    async def solve_challenge(self, path_spec: Dict) -> bool:
        """Solve behavioral challenge by following the path"""
        start = (path_spec["start"]["x"], path_spec["start"]["y"])
        end = (path_spec["end"]["x"], path_spec["end"]["y"])
        c1 = (path_spec["c1"]["x"], path_spec["c1"]["y"])
        c2 = (path_spec["c2"]["x"], path_spec["c2"]["y"])
        
        trail = []
        base_time = time.time() * 1000
        
        for i in range(101):
            t = i / 100.0
            mt = 1 - t
            x = (mt**3 * start[0] + 3 * mt**2 * t * c1[0] + 
                 3 * mt * t**2 * c2[0] + t**3 * end[0])
            y = (mt**3 * start[1] + 3 * mt**2 * t * c1[1] + 
                 3 * mt * t**2 * c2[1] + t**3 * end[1])
            
            deviation = (random.gauss(0, 1.5), random.gauss(0, 1.5))
            x += deviation[0]
            y += deviation[1]
            
            trail.append({
                "x": round(x, 2),
                "y": round(y, 2),
                "t": base_time + i * random.uniform(20, 35)
            })
        
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        payload = {
            "session_id": self.session_id,
            "ts": time.time(),
            "path_spec": path_spec,
            "trail": trail,
            "env_flags": {
                "headless": self.headless,
                "proxy_vpn_tor": False,
                "lang_mismatch": False
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.challenge_url, json=payload)
            result = response.json()
            return result.get("passed", False)

    async def run_transaction(self, beneficiary: str, amount: str, new_beneficiary: bool = False):
        """Execute a complete transaction with human-like behavior"""
        print(f"🤖 Starting human-like transaction: {beneficiary} → {amount}")
        
        await asyncio.sleep(random.uniform(2, 4))
        
        base_time = time.time() * 1000
        mouse_events = []
        key_events = []
        
        mouse_events.extend(self._generate_mouse_path((100, 100), (300, 200)))
        await asyncio.sleep(random.uniform(0.5, 1.2))
        
        mouse_events.extend(self._generate_mouse_path((300, 200), (300, 300)))
        await asyncio.sleep(random.uniform(0.5, 1.2))
        
        key_events.extend(self._generate_keystroke_events(beneficiary, base_time))
        await asyncio.sleep(random.uniform(0.8, 1.5))
        
        key_events.extend(self._generate_keystroke_events(amount, base_time + 6000))
        await asyncio.sleep(random.uniform(1.0, 2.5))
        
        result = await self.send_telemetry(mouse_events, key_events, amount, beneficiary, 
                                          new_beneficiary, paste_count=0)
        
        print(f"📊 Decision: {result.get('decision', {}).get('action', 'unknown')}")
        
        if result.get("decision", {}).get("action") == "step_up_behavior_challenge":
            print("🧩 Solving behavioral challenge...")
            path_spec = {
                "start": {"x": 40, "y": 100},
                "end": {"x": 1880, "y": 100},
                "c1": {"x": 300, "y": 50},
                "c2": {"x": 1600, "y": 150}
            }
            passed = await self.solve_challenge(path_spec)
            print(f"✅ Challenge {'passed' if passed else 'failed'}")
        
        return result


async def main():
    agent = HumanLikeAgent(headless=False)
    
    result = await agent.run_transaction(
        beneficiary="john.doe@example.com",
        amount="10000",
        new_beneficiary=False
    )
    
    print(f"\n📋 Final Result: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
