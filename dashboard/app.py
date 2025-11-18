
import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.graph_objects as go

st.set_page_config(page_title='Trust Demo Dashboard', layout='wide')
st.title('Layer-by-Layer Security – Local Demo')

EVENTS_PATH = Path('/data/events.jsonl')

@st.cache_data(ttl=2)
def load_events():
    if not EVENTS_PATH.exists():
        return pd.DataFrame()
    rows = []
    with open(EVENTS_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                # skip partial/corrupt lines
                continue
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    return df

with st.sidebar:
    st.markdown("**How to use**")
    st.markdown("1. Open frontend at **http://localhost:3000**")
    st.markdown("2. Submit payment; watch attempt appear here.")
    st.markdown("3. If step-up prompts, complete the behavioral challenge.")
    st.markdown("4. Toggle simulator flags to see Bot Context change.")
    st.divider()
    # Get all available event kinds from data
    all_kinds = ['attempt', 'challenge', 'behavioral_analysis', 'contextual_challenge']
    kind_filter = st.multiselect('Show event kinds', options=all_kinds, default=all_kinds)
    if st.button('Refresh'):
        st.cache_data.clear()

try:
    df = load_events()
except Exception as e:
    st.error(f'Error loading events: {e}')
    df = pd.DataFrame()

if df.empty:
    st.info('No events yet. Submit a payment from http://localhost:3000')
else:
    if 'ts' in df.columns:
        try:
            df['ts'] = pd.to_datetime(df['ts'], unit='ms', errors='coerce', utc=True)
            df = df.sort_values('ts', ascending=False)
        except Exception:
            # Fallback to simple timestamp handling
            df['ts'] = pd.to_datetime(df['ts'], errors='coerce')
            df = df.sort_values('ts', ascending=False)

    if kind_filter:
        df = df[df['kind'].isin(kind_filter)]

    colA, colB, colC, colD = st.columns(4)
    attempts = df[df['kind']=='attempt'] if 'kind' in df.columns else pd.DataFrame()
    challenges = df[df['kind'].isin(['challenge', 'contextual_challenge'])] if 'kind' in df.columns else pd.DataFrame()
    behavioral = df[df['kind']=='behavioral_analysis'] if 'kind' in df.columns else pd.DataFrame()
    
    with colA:
        st.metric('Total Events', len(df))
    with colB:
        st.metric('Attempts', len(attempts))
    with colC:
        st.metric('Challenges', len(challenges))
    with colD:
        agent_detected = len(behavioral[behavioral['verdict'] == 'agent']) if not behavioral.empty and 'verdict' in behavioral.columns else 0
        st.metric('Agents Detected', agent_detected)

    if not attempts.empty:
        attempts = attempts.copy()
        attempts['action'] = attempts['decision'].apply(lambda d: d.get('action') if isinstance(d, dict) else None)
        st.subheader('Recent Attempts')
        st.dataframe(attempts[['ts','risk_score','action','latency_ms','scores']].head(20), use_container_width=True)
        latest = attempts.iloc[0]
        st.subheader('Latest Attempt – Layer Scores')
        scores = latest.get('scores', {}) if isinstance(latest.get('scores'), dict) else {}
        c1,c2,c3 = st.columns(3)
        c1.metric('Bot Context', scores.get('bot_context',0))
        c2.metric('Human Motoric', scores.get('human_motoric',0))
        c3.metric('Contextual Risk', scores.get('contextual_risk',0))
        st.json(latest.get('decision', {}))
        with st.expander('Raw Features'):
            st.json(latest.get('features', {}))

    # Show behavioral analysis results
    if not behavioral.empty:
        st.subheader('Agent Detection Results')
        display_cols = ['ts', 'session_id', 'verdict', 'agent_probability', 'confidence']
        available_cols = [col for col in display_cols if col in behavioral.columns]
        st.dataframe(behavioral[available_cols].head(20), use_container_width=True)
        
        # Show latest detection details
        latest_behavioral = behavioral.iloc[0]
        st.subheader('Latest Detection Analysis')
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Verdict', latest_behavioral.get('verdict', 'unknown').upper())
        with col2:
            st.metric('Agent Probability', f"{latest_behavioral.get('agent_probability', 0):.3f}")
        with col3:
            st.metric('Confidence', f"{latest_behavioral.get('confidence', 0):.3f}")
        
        with st.expander('Detailed Analysis'):
            st.json({
                'keystroke_analysis': latest_behavioral.get('keystroke_analysis', {}),
                'mouse_analysis': latest_behavioral.get('mouse_analysis', {}),
                'timing_analysis': latest_behavioral.get('timing_analysis', {}),
                'automation_analysis': latest_behavioral.get('automation_analysis', {})
            })
    
    if not challenges.empty:
        st.subheader('Recent Challenges')
        # Handle both old and new challenge formats
        challenge_cols = ['ts', 'session_id', 'passed']
        if 'challenge_type' in challenges.columns:
            challenge_cols.append('challenge_type')
        if 'adherence_px_median' in challenges.columns:
            challenge_cols.append('adherence_px_median')
        if 'tremor' in challenges.columns:
            challenge_cols.append('tremor')
        if 'accuracy' in challenges.columns:
            challenge_cols.append('accuracy')
        
        available_challenge_cols = [col for col in challenge_cols if col in challenges.columns]
        st.dataframe(challenges[available_challenge_cols].head(20), use_container_width=True)

        # Static replay for canvas challenges only
        canvas_challenges = challenges[challenges['kind'] == 'challenge'] if 'kind' in challenges.columns else challenges
        if not canvas_challenges.empty:
            latest_chal = canvas_challenges.iloc[0]
            with st.expander('Replay latest canvas challenge (static plot)'):
                ps = latest_chal.get('path_spec') if isinstance(latest_chal.get('path_spec'), dict) else None
                trail = latest_chal.get('trail_sample') if isinstance(latest_chal.get('trail_sample'), list) else []
                if ps and trail:
                    # Reconstruct bezier samples
                    def bezier_points(start, end, c1, c2, steps=100):
                        xs, ys = [], []
                        for k in range(steps+1):
                            t = k/steps
                            x = (1-t)**3*start['x'] + 3*(1-t)**2*t*c1['x'] + 3*(1-t)*t**2*c2['x'] + t**3*end['x']
                            y = (1-t)**3*start['y'] + 3*(1-t)**2*t*c1['y'] + 3*(1-t)*t**2*c2['y'] + t**3*end['y']
                            xs.append(x); ys.append(y)
                        return xs, ys
                    xs, ys = bezier_points(ps['start'], ps['end'], ps['c1'], ps['c2'])
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', name='Ideal Path', line=dict(color='#22d3ee')))
                    fig.add_trace(go.Scatter(x=[p['x'] for p in trail], y=[p['y'] for p in trail], mode='lines+markers', name='Your Trail', line=dict(color='#10b981'), marker=dict(size=4)))
                    fig.update_layout(height=350, yaxis=dict(autorange='reversed'), margin=dict(l=10,r=10,t=30,b=10))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info('Replay data not available for the latest canvas challenge.')
