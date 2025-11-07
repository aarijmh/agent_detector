
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os, json, httpx, time, math, statistics

FEATURE_SVC = os.getenv('FEATURE_SVC', 'http://feature_svc:8000')
MODELS_SVC = os.getenv('MODELS_SVC', 'http://models_svc:8000')
POLICY_SVC = os.getenv('POLICY_SVC', 'http://policy_svc:8000')
EVENTS_FILE = os.getenv('EVENTS_FILE', '/data/events.jsonl')

app = FastAPI(title="Collector")
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

async def pipeline(event: dict):
    async with httpx.AsyncClient(timeout=5.0) as client:
        f = (await client.post(f"{FEATURE_SVC}/featurize", json=event)).json()
        s = (await client.post(f"{MODELS_SVC}/score", json=f)).json()
        d = (await client.post(f"{POLICY_SVC}/decide", json=s)).json()
        return f, s, d

@app.post('/collect')
async def collect(event: dict):
    t0 = time.time()
    try:
        features, scored, decision = await pipeline(event)
        record = {
            'kind': 'attempt',
            'ts': event.get('ts'),
            'session_id': event.get('session_id'),
            'channel': event.get('channel'),
            'features': features,
            'scores': scored.get('scores', {}),
            'risk_score': scored.get('risk_score'),
            'decision': decision,
            'latency_ms': int((time.time()-t0)*1000)
        }
        os.makedirs(os.path.dirname(EVENTS_FILE), exist_ok=True)
        with open(EVENTS_FILE, 'a') as f:
            f.write(json.dumps(record) + '')
        return JSONResponse({ 'ok': True, **record })
    except Exception as e:
        return JSONResponse({ 'ok': False, 'error': str(e) }, status_code=500)

# ---- Behavioral Challenge Verification ----

def _nearest_dist(p, samples):
    best = 1e9
    for s in samples:
        dx = p['x']-s['x']; dy = p['y']-s['y']
        d = (dx*dx+dy*dy)**0.5
        if d < best: best = d
    return best

@app.post('/challenge')
async def challenge(payload: dict):
    # payload: {session_id, ts, path_spec: {start,end,c1,c2}, trail:[{x,y,t}], env_flags:{} }
    ts = payload.get('ts')
    trail = payload.get('trail', [])
    flags = payload.get('env_flags') or {}
    # Sample bezier path the same way client did
    ps = payload.get('path_spec') or {}
    start, end, c1, c2 = ps.get('start'), ps.get('end'), ps.get('c1'), ps.get('c2')
    samples = []
    if start and end and c1 and c2:
        for k in range(0,101):
            t = k/100.0
            x = (1-t)**3*start['x'] + 3*(1-t)**2*t*c1['x'] + 3*(1-t)*t**2*c2['x'] + t**3*end['x']
            y = (1-t)**3*start['y'] + 3*(1-t)**2*t*c1['y'] + 3*(1-t)*t**2*c2['y'] + t**3*end['y']
            samples.append({'x':x,'y':y})
    # Compute adherence and motoric jitter
    if not trail:
        return JSONResponse({'passed': False, 'reason': 'no_trail'})
    dists = [_nearest_dist(p, samples) for p in trail]
    median_dev = sorted(dists)[len(dists)//2]
    ts_arr = [p['t'] for p in trail]
    xs = [p['x'] for p in trail]
    ys = [p['y'] for p in trail]
    if len(ts_arr) < 3:
        return JSONResponse({'passed': False, 'reason': 'too_short'})
    dt = [max(1, ts_arr[i]-ts_arr[i-1]) for i in range(1, len(ts_arr))]
    dx = [xs[i]-xs[i-1] for i in range(1, len(xs))]
    dy = [ys[i]-ys[i-1] for i in range(1, len(ys))]
    vel = [ (dx[i]**2+dy[i]**2)**0.5 / (dt[i]/1000.0) for i in range(len(dt)) ]
    mean_v = sum(vel)/len(vel)
    std_v = statistics.pstdev(vel) if len(vel)>1 else 0.0
    tremor = std_v / (mean_v + 1e-6)

    # Simple decision thresholds
    passed = (median_dev <= 12.0) and (tremor >= 0.2)

    record = {
        'kind': 'challenge',
        'ts': ts,
        'session_id': payload.get('session_id'),
        'adherence_px_median': round(median_dev,2),
        'tremor': round(tremor,3),
        'flags': flags,
        'passed': passed
    }
    os.makedirs(os.path.dirname(EVENTS_FILE), exist_ok=True)
    with open(EVENTS_FILE, 'a') as f:
        f.write(json.dumps(record) + '')

    return JSONResponse({ 'passed': passed, 'metrics': record })

@app.get('/')
def root():
    return {"status":"collector up"}
