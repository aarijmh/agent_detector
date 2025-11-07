
from fastapi import FastAPI
import numpy as np

app = FastAPI(title="Feature Service")

def mouse_features(m):
    if not m: return {"mean_vel":0,"tremor":0,"curv":0}
    xs = np.array([p.get("x",0) for p in m]); ys = np.array([p.get("y",0) for p in m]); ts = np.array([p.get("t",0) for p in m])
    dt = np.diff(ts)/1000.0
    if dt.size==0: return {"mean_vel":0,"tremor":0,"curv":0}
    dt[dt==0]=1e-3
    dx = np.diff(xs); dy = np.diff(ys)
    vel = np.sqrt(dx*dx+dy*dy)/dt
    mean_vel = float(np.mean(vel)) if len(vel)>0 else 0
    tremor = float(np.std(vel)/(np.mean(vel)+1e-6))
    angle = np.arctan2(dy, dx)
    dang = np.abs(np.diff(angle))
    curv = float(np.mean(dang)) if len(dang)>0 else 0
    return {"mean_vel":round(mean_vel,4), "tremor":round(tremor,4), "curv":round(curv,4)}

def keystroke_features(k):
    if not k: return {"ikd_mean":0,"ikd_std":0,"backspace_rate":0}
    ts = np.array([p.get("t",0) for p in k])
    ikd = np.diff(ts)
    ikd_mean = float(np.mean(ikd)) if len(ikd)>0 else 0
    ikd_std = float(np.std(ikd)) if len(ikd)>0 else 0
    backspace_rate = float(sum(1 for p in k if p.get("k")=="Backspace")/max(1,len(k)))
    return {"ikd_mean":round(ikd_mean,2),"ikd_std":round(ikd_std,2),"backspace_rate":round(backspace_rate,4)}

@app.post('/featurize')
def featurize(event: dict):
    m = event.get("behavior",{}).get("mouse",[])
    k = event.get("behavior",{}).get("keys",[])
    f_mouse = mouse_features(m)
    f_keys = keystroke_features(k)
    env = event.get("env",{})
    journey = event.get("journey",{})
    flags = (env.get('flags') or {})
    out = {**f_mouse, **f_keys,
           "paste_count": int(event.get("behavior",{}).get("paste_count",0)),
           "ua_len": len(env.get("ua","")),
           "flag_headless": int(bool(flags.get("headless", False))),
           "flag_proxy": int(bool(flags.get("proxy_vpn_tor", False))),
           "flag_lang_mismatch": int(bool(flags.get("lang_mismatch", False))),
           "amount": float(journey.get("amount",0) or 0),
           "new_beneficiary": int(journey.get("new_beneficiary",False))}
    return out
