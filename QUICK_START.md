# Quick Start: Human-like Agent

## Recommended: HTTP-based Human Agent

**Fastest way to test human-like behavior without browser automation frameworks.**

```bash
# Install dependencies
pip install -r requirements.txt

# Run the system
docker compose up --build

# In another terminal, run the agent
python human_agent.py
```

**What it does:**
- Sends realistic behavioral telemetry (mouse, keyboard events)
- Solves canvas challenge with natural path deviation
- No Playwright/Selenium detection vectors

**Output:**
```
🤖 Starting human-like transaction: john.doe@example.com → 25000
📊 Decision: step_up_behavior_challenge
🧩 Solving behavioral challenge...
✅ Challenge passed
```

---

## Key Behavioral Features

### Mouse Movement
- **Bezier curves** for natural paths
- **Acceleration/deceleration** phases
- **Hand tremor** (Gaussian noise)
- **Variable timing** between points

### Keystroke Timing
- **80-300ms** inter-keystroke intervals
- **30-120ms** dwell time per key
- **Natural variation** per character

### Cognitive Delays
- **1-3 seconds** reading time
- **0.5-1.5 seconds** thinking time
- **0.1-0.5 seconds** hesitation before clicks

### Challenge Solving
- **±5-8px** path deviation (realistic)
- **15-40ms** timing between points
- **0.5-1.5s** response time

---

## Customize Behavior

Edit `human_agent.py` to adjust detection evasion:

```python
# Adjust keystroke timing (slower = more human-like)
delay = random.uniform(50, 400)  # Default: 80-300ms

# Adjust mouse tremor intensity
intensity = 0.8  # Default: 0.3-0.5

# Adjust cognitive delays (longer = more realistic)
await asyncio.sleep(random.uniform(2, 5))  # Default: 1-3s
```

---

## Monitoring

Check the dashboard to see detection results:

```
Frontend: http://localhost:3000
Dashboard: http://localhost:8501
WebSocket: ws://localhost:8080/ws
```

**Dashboard shows:**
- Agent probability scores
- Behavioral metrics (mouse variance, keystroke timing)
- Challenge results (adherence, tremor)
- Decision verdicts (allow, deny, step-up)

---

## Troubleshooting

**Agent fails to connect:**
```bash
# Ensure collector is running
docker compose logs collector

# Check collector is accessible
curl http://localhost:8080/
```

**Challenge not solving:**
- Verify trail has enough points (>20)
- Ensure deviation is within ±12px
- Check path_spec coordinates are valid

---

## Files

- `human_agent.py` - HTTP-based human-like agent
- `AGENT_IMPROVEMENTS.md` - Detailed documentation
- `simulator.py` - Original behavior detector
- `bot_simulator.py` - Bot behavior examples
