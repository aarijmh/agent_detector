#!/usr/bin/env python3
"""
Bot Simulator - Demonstrates different types of automated behavior
that the agent detection system should catch.
"""

import requests
import time
import json
import random

COLLECTOR_URL = "http://localhost:8080"

def simulate_perfect_bot():
    """Simulates a bot with perfect timing and movements"""
    print("🤖 Simulating Perfect Bot...")
    
    # Perfect keystroke timing
    keystrokes = []
    for i, key in enumerate(['h', 'e', 'l', 'l', 'o']):
        ts = 1000 + i * 100  # Exactly 100ms apart
        keystrokes.append({
            'key': key,
            'ts': ts,
            'dwell': 50  # Exactly 50ms dwell time
        })
    
    # Perfect linear mouse movement
    mouse_movements = []
    for i in range(20):
        mouse_movements.append({
            'x': 100 + i * 10,  # Perfect linear movement
            'y': 100,
            't': 1000 + i * 50
        })
    
    # Perfect timing events
    timing_events = [
        {'type': 'click', 'ts': 1000, 'x': 100, 'y': 100},
        {'type': 'click', 'ts': 1100, 'x': 200, 'y': 100}  # Exactly 100ms apart
    ]
    
    response = requests.post(f"{COLLECTOR_URL}/behavioral_analysis", json={
        'ts': int(time.time() * 1000),
        'session_id': 'bot_perfect',
        'keystrokes': keystrokes,
        'mouse_movements': mouse_movements,
        'timing_events': timing_events,
        'env_flags': {
            'headless': True,
            'webdriver': True,
            'user_agent': 'HeadlessChrome/91.0.4472.124',
            'plugins_enabled': False
        }
    })
    
    result = response.json()
    print(f"Agent Probability: {result['agent_probability']}")
    print(f"Verdict: {result['verdict']}")
    return result

def simulate_human_like():
    """Simulates more human-like behavior with natural variations"""
    print("👤 Simulating Human-like Behavior...")
    
    # Variable keystroke timing
    keystrokes = []
    base_time = 1000
    for i, key in enumerate(['h', 'e', 'l', 'l', 'o']):
        # Add natural variation
        delay = random.randint(80, 200)
        dwell = random.randint(30, 120)
        base_time += delay
        keystrokes.append({
            'key': key,
            'ts': base_time,
            'dwell': dwell
        })
    
    # Natural mouse movement with curves
    mouse_movements = []
    for i in range(50):
        # Add some curve and jitter
        x = 100 + i * 5 + random.randint(-3, 3)
        y = 100 + random.randint(-5, 5)
        t = 1000 + i * random.randint(20, 80)
        mouse_movements.append({'x': x, 'y': y, 't': t})
    
    # Variable timing events
    timing_events = [
        {'type': 'click', 'ts': 1000, 'x': 100, 'y': 100},
        {'type': 'click', 'ts': 1000 + random.randint(300, 800), 'x': 200, 'y': 100}
    ]
    
    response = requests.post(f"{COLLECTOR_URL}/behavioral_analysis", json={
        'ts': int(time.time() * 1000),
        'session_id': 'human_like',
        'keystrokes': keystrokes,
        'mouse_movements': mouse_movements,
        'timing_events': timing_events,
        'env_flags': {
            'headless': False,
            'webdriver': False,
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'plugins_enabled': True
        }
    })
    
    result = response.json()
    print(f"Agent Probability: {result['agent_probability']}")
    print(f"Verdict: {result['verdict']}")
    return result

def test_contextual_challenges():
    """Test different contextual challenge responses"""
    print("🧩 Testing Contextual Challenges...")
    
    # Test spatial challenge - bot responds too quickly
    spatial_response = requests.post(f"{COLLECTOR_URL}/contextual_challenge", json={
        'ts': int(time.time() * 1000),
        'session_id': 'bot_spatial',
        'type': 'spatial',
        'response': {
            'order': [0, 1, 2, 3, 4],  # Perfect order
            'response_time_ms': 50  # Too fast for human
        },
        'expected': {'order': [0, 1, 2, 3, 4]}
    })
    
    spatial_result = spatial_response.json()
    print(f"Spatial Challenge - Passed: {spatial_result['passed']}")
    
    # Test emotional challenge - human-like response
    emotional_response = requests.post(f"{COLLECTOR_URL}/contextual_challenge", json={
        'ts': int(time.time() * 1000),
        'session_id': 'human_emotional',
        'type': 'emotional',
        'response': {
            'selected': 'happy',
            'response_time_ms': 1200  # Reasonable human time
        },
        'expected': {'correct': 'happy'}
    })
    
    emotional_result = emotional_response.json()
    print(f"Emotional Challenge - Passed: {emotional_result['passed']}")

def main():
    print("🔍 Agent Detection Demo - Bot Simulator")
    print("=" * 50)
    
    try:
        # Test different behavior patterns
        bot_result = simulate_perfect_bot()
        print()
        
        human_result = simulate_human_like()
        print()
        
        test_contextual_challenges()
        print()
        
        print("📊 Summary:")
        print(f"Perfect Bot detected as: {bot_result['verdict']} ({bot_result['agent_probability']})")
        print(f"Human-like detected as: {human_result['verdict']} ({human_result['agent_probability']})")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to collector service.")
        print("Make sure the demo is running: docker compose up --build")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()