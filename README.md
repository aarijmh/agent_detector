
# Trust Demo – Local Only (Extended)

Spin up a **local** demo to visualize detection layers for human vs agent on a payment authorization form, now with a **behavioral step-up challenge** and **transport flags**.

## Prerequisites
- Docker & Docker Compose

## Quick Start
```bash
docker compose up --build
```
- Frontend: http://localhost:3000
- Collector API (health): http://localhost:8080/
- Dashboard: http://localhost:8501

## Try It
1. Open the frontend and submit a payment normally.
2. Paste the beneficiary and set a **high amount** (e.g., `25000`).
3. Toggle **Headless / Proxy / Lang mismatch** and submit again.
4. If you see `step_up_behavior_challenge`, complete the canvas task.
5. Watch the **Dashboard** update for attempts and challenges.

## Architecture
- **frontend (nginx)** – static HTML/JS with telemetry + challenge UI.
- **collector (FastAPI)** – orchestrates feature → model → policy; verifies challenge; writes events to `data/events.jsonl`.
- **feature_svc (FastAPI)** – extracts behavioral & context features.
- **models_svc (FastAPI)** – computes per-layer scores + overall risk.
- **policy_svc (FastAPI)** – maps risk → action with reasons.
- **dashboard (Streamlit)** – visualizes attempts, challenges, and layers.

## New in Extended Version
- **Behavioral Challenge** (Bezier tracking): server verifies **path adherence** and **human jitter**.
- **Transport Flags** (UI simulator): `headless`, `proxy/vpn`, `lang mismatch` influence **Bot Context**.

## Cleanup
```bash
docker compose down -v
```

## Optional Bot Script
See previous instructions or use Playwright to simulate constant typing.
