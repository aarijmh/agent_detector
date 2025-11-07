
# Trust Demo – Local Only (WebSocket Extended)

Adds a **WebSocket** feed to broadcast events in real-time.

## Run
```bash
docker compose up --build
```
- Frontend: http://localhost:3000
- Dashboard: http://localhost:8501
- WS: ws://localhost:8080/ws

## How to see the challenge
- On the frontend, toggle **Headless / Proxy / Lang mismatch**, paste beneficiary, and set amount to **25000**; submit.
- If the policy returns `step_up_behavior_challenge`, a canvas modal opens. Drag the dot along the path. The result is also broadcast via WS and appears in the **Live Events** panel.

## Cleanup
```bash
docker compose down -v
```
