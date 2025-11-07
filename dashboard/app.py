
import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title='Trust Demo Dashboard', layout='wide')
st.title('Layer-by-Layer Security – Local Demo')

EVENTS_PATH = Path('/data/events.jsonl')

@st.cache_data(ttl=3)
def load_events():
    if not EVENTS_PATH.exists():
        return pd.DataFrame()
    rows = []
    with open(EVENTS_PATH, 'r') as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
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
    kind_filter = st.multiselect('Show event kinds', options=['attempt','challenge'], default=['attempt','challenge'])
    if st.button('Refresh'):
        st.cache_data.clear()

df = load_events()
if df.empty:
    st.info('No events yet. Submit a payment from http://localhost:3000')
else:
    if 'ts' in df.columns:
        df['ts'] = pd.to_datetime(df['ts'], errors='coerce')
        df = df.sort_values('ts', ascending=False)

    if kind_filter:
        df = df[df['kind'].isin(kind_filter)]

    colA, colB, colC, colD = st.columns(4)
    attempts = df[df['kind']=='attempt'] if 'kind' in df.columns else pd.DataFrame()
    challenges = df[df['kind']=='challenge'] if 'kind' in df.columns else pd.DataFrame()
    with colA:
        st.metric('Attempt Events', len(attempts))
    with colB:
        st.metric('Avg Risk (Attempts)', round(attempts['risk_score'].mean(),3) if not attempts.empty else 0)
    with colC:
        st.metric('Challenge Events', len(challenges))
    with colD:
        pass_rate = (challenges['passed'].mean()*100.0) if not challenges.empty else 0.0
        st.metric('Challenge Pass Rate', f"{pass_rate:.1f}%")

    if not attempts.empty:
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

    if not challenges.empty:
        st.subheader('Recent Challenges')
        st.dataframe(challenges[['ts','session_id','passed','adherence_px_median','tremor','flags']].head(20), use_container_width=True)
