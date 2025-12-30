# Agent Improvements: Human-like Behavior & Native Browser Control

## Overview
This document outlines improvements to make agents behave more like humans and control browsers natively without Playwright/Selenium.

## Key Improvements

### 1. **Human-like Agent** (`human_agent.py`)
Uses HTTP/WebSocket communication instead of browser automation frameworks.

**Features:**
- Realistic mouse movement with Bezier curves
- Natural keystroke timing (80-300ms inter-keystroke intervals)
- Hand tremor simulation (Gaussian noise)
- Cognitive delays (thinking time before actions)
- Acceleration/deceleration phases in mouse movement
- Challenge solving with realistic path deviation

**Usage:**
```bash
python human_agent.py
```

### 2. **CDP Agent** (`cdp_agent.py`)
Direct Chrome DevTools Protocol control for native browser automation.

**Features:**
- Stealth script injection (hides webdriver, chrome, plugins)
- Native input dispatch (keyboard/mouse events)
- Realistic mouse curves with easing functions
- Element interaction with cognitive delays
- No Playwright/Selenium detection vectors

**Setup:**
```bash
# Start Chrome with remote debugging
google-chrome --remote-debugging-port=9222 --no-first-run

# Run agent
python cdp_agent.py
```

### 3. **Behavioral Patterns**

#### Mouse Movement
- **Bezier curves** instead of linear paths
- **Acceleration/deceleration** phases
- **Tremor** (hand shake) with Gaussian distribution
- **Variable timing** between points

#### Keystroke Timing
- **Inter-keystroke interval (IKI)**: 80-300ms (human range)
- **Dwell time**: 30-120ms (key press duration)
- **Natural variation** per character

#### Cognitive Delays
- **Reading time**: 1-3 seconds before action
- **Thinking time**: 0.5-1.5 seconds between actions
- **Hesitation**: 0.1-0.5 seconds before clicks

### 4. **Environment Spoofing**

**Stealth Indicators Hidden:**
```javascript
navigator.webdriver → false
navigator.chrome → { runtime: {} }
navigator.plugins → [1, 2, 3]
navigator.languages → ['en-US', 'en']
```

**User Agent:**
```
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
```

**Screen Properties:**
- Resolution: 1920x1080
- DPR: 1
- Hardware concurrency: 8

### 5. **Challenge Solving**

**Behavioral Challenge (Canvas Path):**
- Follow ideal path with ±5-8px deviation
- Variable timing (15-40ms between points)
- Natural tremor in coordinates
- Realistic response time (0.5-1.5s before submission)

**Metrics Passed:**
- Adherence: ≤12px median deviation
- Tremor: ≥0.2 (natural hand shake)

## Comparison

| Feature | Playwright | Human Agent | CDP Agent |
|---------|-----------|-------------|-----------|
| Detection Risk | High | Low | Very Low |
| Browser Control | Automation | HTTP/WS | Native CDP |
| Mouse Curves | Linear | Bezier | Bezier + Easing |
| Keystroke Timing | Fixed | Variable | Variable |
| Tremor | None | Gaussian | Gaussian |
| Cognitive Delays | None | Yes | Yes |
| Stealth Scripts | Limited | N/A | Full |
| Setup Complexity | Low | Low | Medium |

## Implementation Recommendations

### For Testing Detection System
Use **Human Agent** (`human_agent.py`):
- Simulates realistic behavior without browser control
- Fast iteration and testing
- No browser setup required

### For Production Evasion
Use **CDP Agent** (`cdp_agent.py`):
- Native browser control
- Hardest to detect
- Requires Chrome with debugging port

### Hybrid Approach
Combine both:
1. Use CDP for initial navigation and setup
2. Switch to HTTP/WS for behavioral events
3. Use CDP for challenge solving

## Behavioral Metrics

### Mouse Movement
- **Velocity**: 100-500 px/s (human range)
- **Acceleration**: 50-200 px/s² (natural acceleration)
- **Jitter**: 0.3-2px (hand tremor)

### Keystroke Events
- **IKI**: 80-300ms (human typing)
- **Dwell**: 30-120ms (key press)
- **Variance**: 20-40% (natural variation)

### Timing
- **Page dwell**: 1-6 seconds
- **Click delay**: 0.1-0.5 seconds
- **Form fill**: 0.5-2 seconds per field

## Detection Evasion Techniques

### 1. Avoid Automation Markers
- ✅ No `navigator.webdriver`
- ✅ No `window.chrome.runtime`
- ✅ No missing plugins
- ✅ Proper user agent

### 2. Realistic Timing
- ✅ Variable keystroke intervals
- ✅ Cognitive delays
- ✅ Natural mouse curves
- ✅ Acceleration/deceleration

### 3. Behavioral Realism
- ✅ Hand tremor
- ✅ Path deviation
- ✅ Hesitation before actions
- ✅ Natural reading time

### 4. Environment Consistency
- ✅ Matching screen resolution
- ✅ Consistent user agent
- ✅ Proper timezone
- ✅ Real hardware concurrency

## Testing

### Run Human Agent
```bash
python human_agent.py
```

### Run CDP Agent
```bash
# Terminal 1: Start Chrome
google-chrome --remote-debugging-port=9222

# Terminal 2: Run agent
python cdp_agent.py
```

### Monitor Detection
Check dashboard at `http://localhost:8501` to see:
- Agent probability scores
- Behavioral metrics
- Challenge results
- Decision verdicts

## Future Improvements

1. **Machine Learning**: Train on real user sessions
2. **Adaptive Behavior**: Adjust patterns based on detection feedback
3. **Multi-tab Support**: Simulate realistic browsing patterns
4. **Network Simulation**: Add realistic network delays
5. **Biometric Spoofing**: Simulate fingerprint variations
6. **Session Persistence**: Maintain consistent behavior across sessions

## References

- Chrome DevTools Protocol: https://chromedevtools.github.io/devtools-protocol/
- Human Behavior Metrics: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3074083/
- Keystroke Dynamics: https://en.wikipedia.org/wiki/Keystroke_dynamics
