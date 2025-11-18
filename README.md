
# Trust Demo – Local Only (WS + Replay + Tuned Policy)

This package adds:
- **WebSocket feed** (`/ws`) to broadcast events in real time.
- **Behavioral challenge replay**:
  - Frontend: "Replay" button replays your drag path on the canvas.
  - Dashboard: Static Plotly replay of the latest challenge (ideal path vs your trail).
- **Tuned policy thresholds** with a hard-block rule.

## Run
```bash
docker compose up --build
```
- Frontend: http://localhost:3000
- Dashboard: http://localhost:8501
- WS: ws://localhost:8080/ws

## New thresholds (policy)
- `allow` ≤ **0.20**
- `step_up_webauthn` ≤ **0.45**
- `step_up_behavior_challenge` ≤ **0.92**
- `deny` > **0.92**
- **Hard block**: if `contextual_risk ≥ 0.70` **and** `bot_context ≥ 0.80` → `deny`

## Trigger the challenge
Toggle **Headless / Proxy / Lang mismatch**, paste the beneficiary, set amount to **25000**, submit. Complete the canvas task, then hit **Replay** to watch your path.

## Cleanup
```bash
docker compose down -v
```
