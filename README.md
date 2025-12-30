# Agent Detector – Human vs Bot Detection System

A comprehensive behavioral analysis system that detects automated agents vs human users through multi-layer risk scoring, real-time WebSocket feeds, and interactive challenges.

## 🎯 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.8+
- Modern web browser

### Run Everything
```bash
docker compose up --build
```

Then open:
- **Frontend**: http://localhost:3000 (Payment form + simulator)
- **Dashboard**: http://localhost:8501 (Real-time analytics)
- **WebSocket**: ws://localhost:8081/ws (Live event stream)

### Run Human-like Agent
```bash
# In another terminal
pip install -r requirements.txt
python human_agent.py
```

## 📋 Project Structure

```
agent_detector/
├── collector/          # Event collection & WebSocket server
├── feature_svc/        # Feature extraction from behavioral events
├── models_svc/         # Risk scoring (bot context, human motoric, contextual risk)
├── policy_svc/         # Decision logic (allow, step-up, deny)
├── dashboard/          # Streamlit analytics dashboard
├── frontend/           # HTML/JS payment form + challenge UI
├── human_agent.py      # HTTP-based human-like agent simulator
├── bot_simulator.py    # Bot behavior examples
├── cdp_agent.py        # Chrome DevTools Protocol agent
├── playwright_simulator.py # Playwright-based automation simulator
├── debug_chrome.py     # Chrome debugging port connectivity checker
├── docker-compose.yml  # Service orchestration
└── requirements.txt    # Python dependencies
```

## 🏗️ Architecture

### Services

**Collector** (Port 8081)
- Receives behavioral events (mouse, keyboard, environment)
- Orchestrates feature extraction → scoring → policy decision
- Broadcasts results via WebSocket
- Stores events to `/data/events.jsonl`

**Feature Service**
- Extracts behavioral metrics from raw events
- Computes mouse velocity, keystroke timing, paste counts, etc.

**Models Service**
- Scores three risk dimensions:
  - **Bot Context**: Headless browser, proxy/VPN, language mismatch
  - **Human Motoric**: Mouse curves, keystroke timing, hand tremor
  - **Contextual Risk**: Amount, new beneficiary, transaction patterns

**Policy Service**
- Applies decision thresholds:
  - `allow` ≤ 0.20
  - `step_up_webauthn` ≤ 0.45
  - `step_up_behavior_challenge` ≤ 0.92
  - `deny` > 0.92
  - **Hard block**: if `contextual_risk ≥ 0.70` AND `bot_context ≥ 0.80` → `deny`

**Dashboard** (Port 8501)
- Real-time event monitoring
- Layer-by-layer score visualization
- Challenge replay (canvas path vs user trail)
- Agent detection results

**Frontend** (Port 3000)
- Payment authorization form
- Behavioral challenge canvas (drag-to-trace)
- Simulator flags (headless, proxy, language mismatch)
- Live WebSocket event feed

## 🧪 Experiment Scenarios

### Scenario 1: Normal Human Transaction
1. Open http://localhost:3000
2. Enter beneficiary and amount (e.g., 5000)
3. Type naturally (don't paste)
4. Submit
5. Check dashboard for `allow` decision

### Scenario 2: Trigger Behavioral Challenge
1. Toggle **Headless** or **Proxy/VPN** flags
2. Enter amount ≥ 25000
3. Submit
4. Complete the canvas challenge (drag blue dot along the path)
5. Check dashboard for `step_up_behavior_challenge` decision

### Scenario 3: Hard Block
1. Toggle **Headless** AND **Proxy/VPN**
2. Enter amount ≥ 25000
3. Submit
4. Check dashboard for `deny` decision (hard block triggered)

### Scenario 4: Run Human-like Agent
```bash
python human_agent.py
```
- Sends realistic behavioral telemetry
- Solves challenges automatically
- No browser automation detection vectors

### Scenario 5: Run Bot Simulator
```bash
python bot_simulator.py
```
- Demonstrates bot-like patterns
- Instant clicks, linear mouse paths
- Paste-heavy input

### Scenario 6: Run CDP Agent
```bash
# Start Chrome with debugging enabled
chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

# In another terminal
python cdp_agent.py
```
- Direct Chrome DevTools Protocol control
- Bypasses Playwright/Selenium detection
- Native browser automation without framework markers

### Scenario 7: Run Playwright Simulator
```bash
python playwright_simulator.py
```
- Playwright-based automation testing
- Compares human vs bot behavior patterns
- Includes ML-based detection training

## 📊 Dashboard Features

### Metrics
- **Total Events**: All collected events
- **Attempts**: Payment authorization attempts
- **Challenges**: Behavioral challenges issued
- **Agents Detected**: Automated behavior identified

### Layers
- **Bot Context**: Environment signals (headless, proxy, language)
- **Human Motoric**: Behavioral signals (mouse curves, keystroke timing)
- **Contextual Risk**: Transaction signals (amount, new beneficiary)

### Challenge Replay
- Static Plotly visualization
- Ideal path (cyan) vs user trail (green)
- Metrics: adherence (px), tremor (hand shake)

## 🤖 Agent Types

### HTTP-based Human Agent (`human_agent.py`)

Simulates realistic human behavior via HTTP requests:

### Features
- **Mouse Movement**: Bezier curves with Gaussian tremor
- **Keystroke Timing**: 80-300ms inter-keystroke intervals
- **Cognitive Delays**: 1-3s reading time, 0.5-1.5s thinking time
- **Challenge Solving**: Follows path with ±5-8px deviation

### Usage
```bash
python human_agent.py
```

### Customize HTTP Agent
Edit `human_agent.py` to adjust:
```python
# Keystroke timing (slower = more human-like)
iki = random.uniform(120, 280)  # Default: 80-300ms

# Mouse tremor intensity
deviation = (random.gauss(0, 1.5), random.gauss(0, 1.5))  # Default: 0-2px

# Cognitive delays
await asyncio.sleep(random.uniform(2, 4))  # Default: 1-3s
```

### CDP Agent (`cdp_agent.py`)

Direct Chrome DevTools Protocol control for native browser automation:

#### Features
- **Native Browser Control**: Direct CDP communication, no automation frameworks
- **Stealth Mode**: Injects scripts to hide `navigator.webdriver` and other markers
- **Realistic Interactions**: Human-like mouse curves, keystroke timing, cognitive delays
- **Framework Bypass**: Avoids Playwright/Selenium detection vectors

#### Setup
```bash
# Start Chrome with remote debugging
chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

# Check connectivity (optional)
python debug_chrome.py 9222

# Run CDP agent
python cdp_agent.py
```

#### Customize CDP Agent
Edit `cdp_agent.py` to adjust:
```python
# Mouse movement steps (more = smoother)
steps = random.randint(10, 20)  # Default: 10-20

# Keystroke delays
delay_ms = random.uniform(50, 200)  # Default: 100ms base

# Stealth scripts (add more as needed)
stealth_scripts = [
    "Object.defineProperty(navigator, 'webdriver', { get: () => false });",
    "Object.defineProperty(navigator, 'chrome', { get: () => ({ runtime: {} }) });"
]
```

### Playwright Simulator (`playwright_simulator.py`)

Playwright-based automation with ML detection training:

#### Features
- **Behavior Comparison**: Side-by-side human vs bot simulation
- **ML Training**: Trains detection models on behavioral patterns
- **Session Analysis**: Extracts timing, movement, and interaction features
- **Dashboard Integration**: Sends results to real-time dashboard

#### Usage
```bash
python playwright_simulator.py
```

### Debug Tools

#### Chrome Debug Checker (`debug_chrome.py`)
Verifies Chrome debugging port connectivity:
```bash
python debug_chrome.py 9222
```

Checks:
- Port listening status
- HTTP endpoint accessibility
- WebSocket debugger URL availability

## 🔧 API Endpoints

### Collector

**POST /collect**
```json
{
  "session_id": "1234567890",
  "ts": 1234567890.123,
  "channel": "web",
  "env": {
    "ua": "Mozilla/5.0...",
    "lang": "en-US",
    "tz": "America/New_York",
    "platform": "MacIntel",
    "hwc": 8,
    "screen": {"w": 1920, "h": 1080, "dpr": 1}
  },
  "behavior": {
    "mouse": [{"x": 100, "y": 200, "t": 1234567890123, "dt": 20}],
    "keys": [{"k": "a", "t": 1234567890123, "dwell": 50}],
    "paste_count": 0
  },
  "journey": {
    "amount": "10000",
    "beneficiary": "john.doe@example.com",
    "new_beneficiary": false
  }
}
```

**POST /challenge**
```json
{
  "session_id": "1234567890",
  "ts": 1234567890.123,
  "path_spec": {
    "start": {"x": 40, "y": 100},
    "end": {"x": 1880, "y": 100},
    "c1": {"x": 300, "y": 50},
    "c2": {"x": 1600, "y": 150}
  },
  "trail": [
    {"x": 40, "y": 100, "t": 1234567890123},
    {"x": 100, "y": 105, "t": 1234567890143}
  ],
  "env_flags": {
    "headless": false,
    "proxy_vpn_tor": false,
    "lang_mismatch": false
  }
}
```

**WebSocket /ws**
- Connect: `ws://localhost:8081/ws`
- Receive: Real-time event broadcasts (JSON)
- Send: Keep-alive messages (any text)

## 📈 Event Schema

### Attempt Event
```json
{
  "kind": "attempt",
  "ts": 1234567890.123,
  "session_id": "1234567890",
  "channel": "web",
  "features": {...},
  "scores": {
    "bot_context": 0.15,
    "human_motoric": 0.25,
    "contextual_risk": 0.30
  },
  "risk_score": 0.23,
  "decision": {
    "action": "allow",
    "reason": "risk_score_below_threshold"
  },
  "latency_ms": 145
}
```

### Challenge Event
```json
{
  "kind": "challenge",
  "ts": 1234567890.123,
  "session_id": "1234567890",
  "adherence_px_median": 8.5,
  "tremor": 0.45,
  "flags": {...},
  "passed": true,
  "path_spec": {...},
  "trail_sample": [...]
}
```

## 🧩 Challenge Mechanics

### Canvas Path Challenge
- User drags blue dot along highlighted Bezier curve
- System measures:
  - **Adherence**: Median distance from ideal path (≤12px passes)
  - **Tremor**: Hand shake coefficient (≥0.2 passes)
- Realistic human paths have natural deviation and tremor

### Replay
- Frontend: "Replay" button re-traces user's path
- Dashboard: Static Plotly visualization of ideal vs actual path

## 🔐 Security Considerations

### Detection Signals
- **Headless browser**: `navigator.webdriver`, missing plugins
- **Proxy/VPN**: IP geolocation, DNS leaks
- **Language mismatch**: Accept-Language vs browser locale
- **Bot patterns**: Linear mouse paths, instant clicks, paste-heavy input
- **Unnatural timing**: Keystroke intervals <50ms, no cognitive delays
- **Automation frameworks**: Playwright/Selenium markers, CDP detection
- **Browser fingerprinting**: Missing navigator properties, plugin inconsistencies

### Agent Detection Comparison

| Agent Type | Framework Markers | Stealth Level | Detection Difficulty |
|------------|------------------|---------------|---------------------|
| **HTTP Agent** | None | High | Hard |
| **CDP Agent** | None | Very High | Very Hard |
| **Playwright** | Yes | Low | Easy |
| **Bot Simulator** | None | Very Low | Very Easy |

### Evasion Techniques by Agent Type

#### HTTP Agent (`human_agent.py`)
- No browser automation framework
- Realistic behavioral telemetry generation
- Natural timing patterns
- Challenge solving with path deviation

#### CDP Agent (`cdp_agent.py`)
- Direct browser control via DevTools Protocol
- Stealth script injection
- Framework marker removal
- Native browser API usage

#### Playwright Simulator (`playwright_simulator.py`)
- Standard automation framework (easily detected)
- Useful for testing detection capabilities
- Demonstrates detectable automation patterns

## 🛠️ Development

### Troubleshooting CDP Agent

#### Chrome Not Starting
```bash
# Check if Chrome is running
ps aux | grep chrome

# Kill existing Chrome processes
pkill -f chrome

# Start Chrome with debugging
chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug --no-first-run --no-default-browser-check
```

#### Port Already in Use
```bash
# Check what's using port 9222
lsof -i :9222

# Use different port
python cdp_agent.py  # Edit port in script
```

#### Connection Issues
```bash
# Test connectivity
python debug_chrome.py 9222

# Check Chrome version compatibility
chrome --version
```

#### WebSocket Errors
- Ensure Chrome is started with `--remote-debugging-port`
- Check firewall settings
- Verify no other CDP clients are connected

### Add Custom Feature
Edit `feature_svc/app.py`:
```python
@app.post('/featurize')
async def featurize(event: dict):
    # Extract features from event
    features = {
        'mouse_velocity': compute_velocity(event['behavior']['mouse']),
        'keystroke_iki': compute_iki(event['behavior']['keys']),
        # Add your feature here
    }
    return features
```

### Add Custom Scoring Model
Edit `models_svc/app.py`:
```python
@app.post('/score')
async def score(features: dict):
    scores = {
        'bot_context': score_bot_context(features),
        'human_motoric': score_human_motoric(features),
        'contextual_risk': score_contextual_risk(features),
    }
    return scores
```

### Add Custom Policy Rule
Edit `policy_svc/app.py`:
```python
@app.post('/decide')
async def decide(scored: dict):
    risk_score = scored['risk_score']
    if risk_score > 0.92:
        return {'action': 'deny', 'reason': 'high_risk'}
    # Add your rule here
```

## 📝 Logs & Debugging

### View Collector Logs
```bash
docker compose logs collector -f
```

### View Dashboard Logs
```bash
docker compose logs dashboard -f
```

### View Events File
```bash
docker compose exec collector tail -f /data/events.jsonl
```

### Clear Data
```bash
docker compose down -v
```

## 🚀 Production Deployment

### Environment Variables
```bash
FEATURE_SVC=http://feature_svc:8000
MODELS_SVC=http://models_svc:8000
POLICY_SVC=http://policy_svc:8000
EVENTS_FILE=/data/events.jsonl
```

### Scaling
- Run multiple collector instances behind a load balancer
- Use external database instead of JSONL file
- Deploy services to Kubernetes

### Monitoring
- Export metrics to Prometheus
- Set up alerts for high agent detection rates
- Monitor latency (target: <200ms)

## 📚 References

- [QUICK_START.md](QUICK_START.md) – Human agent setup
- [AGENT_IMPROVEMENTS.md](AGENT_IMPROVEMENTS.md) – Detailed behavioral patterns
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Keystroke Dynamics](https://en.wikipedia.org/wiki/Keystroke_dynamics)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `docker compose up --build`
5. Submit a pull request

## 📄 License

MIT License – See LICENSE file for details

## 🆘 Troubleshooting

### Services won't start
```bash
# Check Docker daemon
docker ps

# Rebuild images
docker compose down -v
docker compose up --build
```

### WebSocket connection fails
```bash
# Verify collector is running
curl http://localhost:8081/

# Check firewall
lsof -i :8081
```

### Challenge not solving
- Verify trail has >20 points
- Ensure deviation is within ±12px
- Check path_spec coordinates are valid

### Dashboard shows no events
- Ensure collector is running
- Submit a payment from frontend
- Check `/data/events.jsonl` exists

---

**Questions?** Check the dashboard at http://localhost:8501 for real-time insights into the detection system.
