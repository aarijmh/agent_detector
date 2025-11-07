
from fastapi import FastAPI

app = FastAPI(title="Models Service")

@app.post('/score')
def score(features: dict):
    bot_ctx = 0.0
    if features.get('ua_len', 0) < 50: bot_ctx += 0.1
    if features.get('flag_headless',0)==1: bot_ctx += 0.5
    if features.get('flag_proxy',0)==1: bot_ctx += 0.3
    if features.get('flag_lang_mismatch',0)==1: bot_ctx += 0.2
    bot_ctx = min(1.0, bot_ctx)

    tremor = features.get('tremor', 0.0)
    ikd_std = features.get('ikd_std', 0.0)
    human_motoric = max(0.0, min(1.0, 0.5*min(1.0, tremor) + 0.5*min(1.0, ikd_std/120.0)))

    ctx = 0.0
    if features.get('new_beneficiary',0)==1: ctx += 0.3
    if features.get('amount',0) > 10000: ctx += 0.4
    if features.get('paste_count',0) >= 1: ctx += 0.2

    risk = 0.35*bot_ctx + 0.30*(1-human_motoric) + 0.35*ctx
    return {'scores': {'bot_context': round(bot_ctx,3), 'human_motoric': round(human_motoric,3), 'contextual_risk': round(ctx,3)}, 'risk_score': round(risk,3)}
