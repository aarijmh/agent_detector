
from fastapi import FastAPI

app = FastAPI(title="Policy Service")

@app.post('/decide')
def decide(scored: dict):
    scores = scored.get('scores', {}) or {}
    r = float(scored.get('risk_score',0))

    # Tuned thresholds
    if r <= 0.20:
        action = 'allow'
    elif r <= 0.45:
        action = 'step_up_webauthn'
    elif r <= 0.92:
        action = 'step_up_behavior_challenge'
    else:
        action = 'deny'

    # Hard block condition
    if scores.get('contextual_risk',0) >= 0.70 and scores.get('bot_context',0) >= 0.80:
        action = 'deny'

    reasons = []
    if scores.get('contextual_risk',0) >= 0.5: reasons.append('high_contextual_risk')
    if scores.get('human_motoric',1) < 0.3: reasons.append('low_human_motoric')
    if scores.get('bot_context',0) > 0.5: reasons.append('bot_context_signals')
    if action == 'deny' and scores.get('contextual_risk',0) >= 0.70 and scores.get('bot_context',0) >= 0.80:
        reasons.append('hard_block_high_bot_and_context')

    return { 'action': action, 'reasons': reasons[:4] }
