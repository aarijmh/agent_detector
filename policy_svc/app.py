
from fastapi import FastAPI

app = FastAPI(title="Policy Service")

@app.post('/decide')
def decide(scored: dict):
    r = float(scored.get('risk_score',0))
    if r <= 0.25:
        action = 'allow'
    elif r <= 0.65:
        action = 'step_up_webauthn'
    elif r <= 0.90:
        action = 'step_up_behavior_challenge'
    else:
        action = 'deny'

    reasons = []
    scores = scored.get('scores', {})
    if scores.get('contextual_risk',0) >= 0.5: reasons.append('high_contextual_risk')
    if scores.get('human_motoric',1) < 0.3: reasons.append('low_human_motoric')
    if scores.get('bot_context',0) > 0.5: reasons.append('bot_context_signals')

    return { 'action': action, 'reasons': reasons[:3] }
