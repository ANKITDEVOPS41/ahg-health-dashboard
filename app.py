import base64
import io
import json
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
import plotly.graph_objects as go
import qrcode
import streamlit as st

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AHG · Personal Health Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset & base ── */
* { box-sizing: border-box; }

[data-testid="stAppViewContainer"] {
    background: #060E1A;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #0B1525; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 1.8rem 2.2rem 2rem 2.2rem !important;
    max-width: 1280px;
}

/* ── Typography ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ── Hero header ── */
.ahg-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.4rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.ahg-title {
    font-size: 1.95rem;
    font-weight: 700;
    color: #F0F6FF;
    letter-spacing: -0.02em;
    margin: 0;
    line-height: 1.2;
}
.ahg-subtitle {
    font-size: 0.92rem;
    color: #6B8CAE;
    margin-top: 5px;
    letter-spacing: 0.01em;
}
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(34, 197, 94, 0.12);
    color: #4ADE80;
    border: 1px solid rgba(74, 222, 128, 0.25);
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    white-space: nowrap;
}
.live-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #4ADE80;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}
.alert-badge {
    background: rgba(239, 68, 68, 0.12);
    color: #F87171;
    border: 1px solid rgba(248, 113, 113, 0.25);
}

/* ── Section labels ── */
.section-label {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #4A7FA8;
    margin: 1.4rem 0 0.7rem 0;
}

/* ── Glass cards ── */
.glass {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
}
.glass-light {
    background: rgba(255,255,255,0.97);
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
}

/* ── Metric cards ── */
.metric-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 1.1rem 1.3rem;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}
.mc-teal::before   { background: linear-gradient(90deg, #14B8A6, #0EA5E9); }
.mc-blue::before   { background: linear-gradient(90deg, #3B82F6, #8B5CF6); }
.mc-amber::before  { background: linear-gradient(90deg, #F59E0B, #EF4444); }
.metric-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #6B8CAE;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 2.4rem;
    font-weight: 700;
    color: #F0F6FF;
    line-height: 1;
    letter-spacing: -0.02em;
}
.metric-unit {
    font-size: 0.95rem;
    color: #6B8CAE;
    font-weight: 400;
    margin-left: 4px;
}
.metric-footer {
    margin-top: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.status-pill {
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 999px;
    letter-spacing: 0.04em;
}
.sp-normal   { background: rgba(74,222,128,0.15);  color: #4ADE80; }
.sp-elevated { background: rgba(251,191,36,0.15);  color: #FBBF24; }
.sp-critical { background: rgba(248,113,113,0.15); color: #F87171; }
.trend-tag {
    font-size: 0.72rem;
    color: #6B8CAE;
}

/* ── Risk assessment card ── */
.risk-card {
    background: rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    border-left: 4px solid;
}
.rc-low    { border-color: #22C55E; }
.rc-medium { border-color: #F59E0B; }
.rc-high   { border-color: #EF4444; }
.risk-score-num {
    font-size: 3.2rem;
    font-weight: 800;
    color: #F0F6FF;
    line-height: 1;
    letter-spacing: -0.03em;
}
.risk-score-denom {
    font-size: 1.2rem;
    color: #6B8CAE;
    font-weight: 400;
}
.risk-level-pill {
    display: inline-block;
    font-size: 0.8rem;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 999px;
    margin-top: 8px;
    margin-bottom: 10px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.rp-low    { background: rgba(34,197,94,0.15);  color: #4ADE80;  border: 1px solid rgba(74,222,128,0.3); }
.rp-medium { background: rgba(245,158,11,0.15); color: #FBBF24;  border: 1px solid rgba(251,191,36,0.3); }
.rp-high   { background: rgba(239,68,68,0.15);  color: #F87171;  border: 1px solid rgba(248,113,113,0.3); }
.risk-rec-text {
    font-size: 0.9rem;
    color: #94B8D4;
    line-height: 1.65;
    margin-top: 4px;
}

/* ── Profile card ── */
.profile-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
}
.profile-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 0.88rem;
}
.profile-row:last-child { border-bottom: none; }
.pk { color: #6B8CAE; }
.pv { color: #D4E8F5; font-weight: 500; text-align: right; max-width: 58%; }

/* ── Alert banner ── */
.alert-banner {
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 1.2rem;
    display: flex;
    gap: 12px;
    align-items: flex-start;
}
.ab-high   { background: rgba(239,68,68,0.1);   border: 1px solid rgba(239,68,68,0.25);   }
.ab-medium { background: rgba(245,158,11,0.1);  border: 1px solid rgba(245,158,11,0.25);  }
.ab-icon { font-size: 1rem; margin-top: 1px; }
.ab-title { font-size: 0.88rem; font-weight: 700; }
.ab-body  { font-size: 0.82rem; margin-top: 2px; opacity: 0.85; }
.ab-high   .ab-title, .ab-high   .ab-body { color: #F87171; }
.ab-medium .ab-title, .ab-medium .ab-body { color: #FBBF24; }

/* ── Reason items ── */
.reason-item {
    font-size: 0.84rem;
    color: #C8DCF0;
    padding: 8px 10px;
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    margin-bottom: 6px;
    border-left: 2px solid rgba(59,130,246,0.5);
    line-height: 1.5;
}
.no-flag {
    font-size: 0.85rem;
    color: #6B8CAE;
    padding: 8px 0;
}

/* ── Timeline ── */
.tl-step {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
    align-items: flex-start;
}
.tl-num {
    width: 22px; height: 22px;
    border-radius: 50%;
    background: rgba(59,130,246,0.2);
    color: #60A5FA;
    font-size: 0.72rem;
    font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
}
.tl-text {
    font-size: 0.84rem;
    color: #B0CDE5;
    line-height: 1.55;
}

/* ── Panel card ── */
.panel-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    height: 100%;
}
.panel-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #4A7FA8;
    margin-bottom: 12px;
}
.rec-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #4A7FA8;
    margin-bottom: 4px;
    margin-top: 12px;
}
.rec-label:first-child { margin-top: 0; }
.rec-text {
    font-size: 0.9rem;
    color: #B0CDE5;
    line-height: 1.65;
}
.escalation-yes {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
    background: rgba(239,68,68,0.12);
    color: #F87171;
    border: 1px solid rgba(239,68,68,0.2);
}
.escalation-no {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
    background: rgba(34,197,94,0.1);
    color: #4ADE80;
    border: 1px solid rgba(74,222,128,0.2);
}

/* ── Handoff table ── */
.handoff-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 7px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 0.87rem;
    gap: 12px;
}
.handoff-row:last-child { border-bottom: none; }
.hk { color: #6B8CAE; flex-shrink: 0; min-width: 130px; }
.hv { color: #D4E8F5; font-weight: 500; text-align: right; }

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 1.4rem 0;
}

/* ── Streamlit widget overrides ── */
div[data-testid="stButton"] > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #D4E8F5 !important;
    border-radius: 10px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.15s !important;
}
div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.2) !important;
}

/* active preset button highlight */
.active-preset button {
    background: rgba(59,130,246,0.18) !important;
    border-color: rgba(59,130,246,0.45) !important;
    color: #93C5FD !important;
}

/* plotly transparent bg */
.js-plotly-plot .plotly .main-svg {
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DEMO CASES
# ─────────────────────────────────────────────
CASES: Dict[str, Dict] = {
    "Stable Baseline": {
        "id": "AHG-001", "name": "Aarav Mehta", "age": 29, "gender": "Male",
        "conditions": ["None"], "symptoms": ["None"],
        "hr":   [78, 79, 80, 81, 82, 82],
        "spo2": [98, 98, 97, 97, 97, 97],
        "temp": [98.2, 98.2, 98.3, 98.3, 98.4, 98.4],
    },
    "Early Warning": {
        "id": "AHG-002", "name": "Riya Sharma", "age": 34, "gender": "Female",
        "conditions": ["Asthma"], "symptoms": ["Mild fatigue", "Cough"],
        "hr":   [88, 91, 94, 97, 99, 101],
        "spo2": [97, 96, 95, 95, 94, 94],
        "temp": [98.5, 98.8, 99.0, 99.2, 99.5, 99.8],
    },
    "Critical Escalation": {
        "id": "AHG-003", "name": "John Doe", "age": 55, "gender": "Male",
        "conditions": ["Diabetes", "Hypertension"],
        "symptoms": ["Fever", "Cough", "Shortness of breath"],
        "hr":   [96, 102, 108, 112, 115, 118],
        "spo2": [95, 93, 92, 91, 90, 89],
        "temp": [99.0, 99.6, 100.1, 100.5, 100.9, 101.2],
    },
}


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def last(lst): return lst[-1]

def trend_dir(lst: List[float], higher_is_worse: bool) -> str:
    d = lst[-1] - lst[0]
    if abs(d) < 0.4: return "Stable"
    if higher_is_worse: return "Worsening" if d > 0 else "Improving"
    return "Worsening" if d < 0 else "Improving"

def compute_risk(hr, spo2, temp, ht, st, tt) -> Tuple[int, str, List[str]]:
    score, reasons = 0, []
    if spo2 < 92:   score += 45; reasons.append("Oxygen saturation critically low")
    elif spo2 < 95: score += 20; reasons.append("Oxygen saturation below ideal baseline")
    if temp >= 101:  score += 30; reasons.append("Fever in critical zone")
    elif temp >= 99.5: score += 15; reasons.append("Rising body temperature detected")
    if hr >= 115:   score += 25; reasons.append("Heart rate in high-risk zone")
    elif hr >= 100: score += 12; reasons.append("Heart rate elevated")
    if st == "Worsening": score += 15; reasons.append("Oxygen trend worsening over time")
    if tt == "Worsening": score += 10; reasons.append("Temperature trend rising over time")
    if ht == "Worsening": score += 8;  reasons.append("Heart rate trend worsening over time")
    score = min(score, 100)
    level = "HIGH" if score >= 60 else "MEDIUM" if score >= 30 else "LOW"
    return score, level, reasons

def get_rec(level: str) -> str:
    if level == "HIGH":   return "Immediate clinical evaluation advised. Prioritize doctor review and transfer to clinic triage."
    if level == "MEDIUM": return "Close monitoring advised. Recheck vitals soon. Visit clinic if pattern persists or worsens."
    return "Continue routine monitoring. No immediate escalation required."

def metric_status(metric, val) -> Tuple[str, str]:
    if metric == "hr":
        if val >= 115: return "Critical", "sp-critical"
        if val >= 100: return "Elevated", "sp-elevated"
        return "Normal", "sp-normal"
    if metric == "spo2":
        if val < 92: return "Critical", "sp-critical"
        if val < 95: return "Warning",  "sp-elevated"
        return "Normal", "sp-normal"
    if val >= 101:  return "Critical", "sp-critical"
    if val >= 99.5: return "Elevated", "sp-elevated"
    return "Normal", "sp-normal"

def trend_badge_html(direction: str) -> str:
    color = {"Worsening": "#F87171", "Improving": "#4ADE80", "Stable": "#6B8CAE"}[direction]
    arrow = {"Worsening": "↑", "Improving": "↓", "Stable": "→"}[direction]
    return f'<span style="color:{color};font-size:0.78rem;font-weight:600;">{arrow} {direction}</span>'

def build_qr(payload: dict) -> str:
    """Generate QR and return as base64 PNG data URI for reliable st.markdown rendering."""
    qr = qrcode.QRCode(box_size=8, border=3)
    qr.add_data(json.dumps(payload))
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0B1525", back_color="#ffffff").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"

def build_trend_chart(c: dict) -> go.Figure:
    labels = ["T-5", "T-4", "T-3", "T-2", "T-1", "Now"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=c["hr"], mode="lines+markers", name="Heart Rate",
        line=dict(color="#3B82F6", width=2.5),
        marker=dict(size=6, color="#3B82F6"),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.05)"
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=c["spo2"], mode="lines+markers", name="SpO2",
        line=dict(color="#14B8A6", width=2.5),
        marker=dict(size=6, color="#14B8A6"),
        fill="tozeroy", fillcolor="rgba(20,184,166,0.05)"
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=c["temp"], mode="lines+markers", name="Temperature",
        line=dict(color="#F59E0B", width=2.5),
        marker=dict(size=6, color="#F59E0B"),
        fill="tozeroy", fillcolor="rgba(245,158,11,0.05)"
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(
            orientation="h", y=-0.15,
            font=dict(size=11, color="#6B8CAE"),
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            tickfont=dict(size=11, color="#6B8CAE"),
            linecolor="rgba(255,255,255,0.1)"
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            tickfont=dict(size=11, color="#6B8CAE"),
            linecolor="rgba(255,255,255,0.1)"
        ),
        hovermode="x unified",
    )
    return fig


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "case_key" not in st.session_state:
    st.session_state.case_key = "Stable Baseline"
if "qr_shown" not in st.session_state:
    st.session_state.qr_shown = False


# ─────────────────────────────────────────────
# LOAD + COMPUTE
# ─────────────────────────────────────────────
c = CASES[st.session_state.case_key]

hr_now   = last(c["hr"])
spo2_now = last(c["spo2"])
temp_now = last(c["temp"])

ht = trend_dir(c["hr"],   higher_is_worse=True)
st_ = trend_dir(c["spo2"], higher_is_worse=False)
tt = trend_dir(c["temp"],  higher_is_worse=True)

score, level, reasons = compute_risk(hr_now, spo2_now, temp_now, ht, st_, tt)
rec = get_rec(level)

risk_pill_cls = {"LOW": "rp-low", "MEDIUM": "rp-medium", "HIGH": "rp-high"}[level]
risk_card_cls = {"LOW": "rc-low", "MEDIUM": "rc-medium", "HIGH": "rc-high"}[level]


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
badge_html = (
    '<span class="live-badge alert-badge">⚠ Alert Active</span>'
    if level == "HIGH" else
    '<span class="live-badge"><span class="live-dot"></span>Live Monitoring</span>'
)

st.markdown(f"""
<div class="ahg-header">
  <div>
    <div class="ahg-title">Personal Health Dashboard</div>
    <div class="ahg-subtitle">Continuous Monitoring &nbsp;·&nbsp; Early Risk Detection &nbsp;·&nbsp; Portable Health Summary</div>
  </div>
  {badge_html}
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ALERT BANNER
# ─────────────────────────────────────────────
if level == "HIGH":
    flag_preview = " · ".join(reasons[:2]) if reasons else "Critical vitals detected"
    st.markdown(f"""
    <div class="alert-banner ab-high">
      <span class="ab-icon">⚠</span>
      <div>
        <div class="ab-title">Critical health alert — {c["name"]}</div>
        <div class="ab-body">{flag_preview}</div>
      </div>
    </div>""", unsafe_allow_html=True)
elif level == "MEDIUM":
    flag_preview = " · ".join(reasons[:2]) if reasons else "Abnormal trend detected"
    st.markdown(f"""
    <div class="alert-banner ab-medium">
      <span class="ab-icon">◉</span>
      <div>
        <div class="ab-title">Early warning — monitoring closely</div>
        <div class="ab-body">{flag_preview}</div>
      </div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DEMO PRESETS
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Demo Scenario Presets</div>', unsafe_allow_html=True)

p1, p2, p3 = st.columns(3)
with p1:
    active = "active-preset" if st.session_state.case_key == "Stable Baseline" else ""
    st.markdown(f'<div class="{active}">', unsafe_allow_html=True)
    if st.button("Stable Baseline", use_container_width=True, key="btn_stable"):
        st.session_state.case_key = "Stable Baseline"
        st.session_state.qr_shown = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with p2:
    active = "active-preset" if st.session_state.case_key == "Early Warning" else ""
    st.markdown(f'<div class="{active}">', unsafe_allow_html=True)
    if st.button("Early Warning", use_container_width=True, key="btn_warning"):
        st.session_state.case_key = "Early Warning"
        st.session_state.qr_shown = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with p3:
    active = "active-preset" if st.session_state.case_key == "Critical Escalation" else ""
    st.markdown(f'<div class="{active}">', unsafe_allow_html=True)
    if st.button("Critical Escalation", use_container_width=True, key="btn_critical"):
        st.session_state.case_key = "Critical Escalation"
        st.session_state.qr_shown = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PROFILE + AI ASSESSMENT
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Patient Overview</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.65])

with col_left:
    conds = ", ".join(c["conditions"])
    symps = ", ".join(c["symptoms"])
    st.markdown(f"""
    <div class="profile-card">
      <div class="panel-title">Patient Summary</div>
      <div class="profile-row"><span class="pk">Patient ID</span><span class="pv">{c["id"]}</span></div>
      <div class="profile-row"><span class="pk">Name</span><span class="pv">{c["name"]}</span></div>
      <div class="profile-row"><span class="pk">Age / Gender</span><span class="pv">{c["age"]} / {c["gender"]}</span></div>
      <div class="profile-row"><span class="pk">Known conditions</span><span class="pv">{conds}</span></div>
      <div class="profile-row"><span class="pk">Current symptoms</span><span class="pv">{symps}</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown(f"""
    <div class="risk-card {risk_card_cls}">
      <div class="panel-title">AI Health Assessment</div>
      <div class="risk-score-num">{score}<span class="risk-score-denom">/100</span></div>
      <div><span class="risk-level-pill {risk_pill_cls}">{level} RISK</span></div>
      <div class="risk-rec-text">{rec}</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Live Physiological Metrics</div>', unsafe_allow_html=True)

hr_stat, hr_cls     = metric_status("hr",   hr_now)
spo2_stat, spo2_cls = metric_status("spo2", spo2_now)
temp_stat, temp_cls = metric_status("temp", temp_now)

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(f"""
    <div class="metric-card mc-teal">
      <div class="metric-label">Heart Rate</div>
      <div class="metric-value">{hr_now}<span class="metric-unit">BPM</span></div>
      <div class="metric-footer">
        <span class="status-pill {hr_cls}">{hr_stat}</span>
        <span class="trend-tag">{trend_badge_html(ht)}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card mc-blue">
      <div class="metric-label">SpO2</div>
      <div class="metric-value">{spo2_now}<span class="metric-unit">%</span></div>
      <div class="metric-footer">
        <span class="status-pill {spo2_cls}">{spo2_stat}</span>
        <span class="trend-tag">{trend_badge_html(st_)}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card mc-amber">
      <div class="metric-label">Temperature</div>
      <div class="metric-value">{temp_now}<span class="metric-unit">°F</span></div>
      <div class="metric-footer">
        <span class="status-pill {temp_cls}">{temp_stat}</span>
        <span class="trend-tag">{trend_badge_html(tt)}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TREND CHART
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Multi-Signal Trend Analysis</div>', unsafe_allow_html=True)
st.plotly_chart(build_trend_chart(c), use_container_width=True)


# ─────────────────────────────────────────────
# EXPLAINABILITY + TIMELINE
# ─────────────────────────────────────────────
e1, e2 = st.columns(2)

with e1:
    if reasons:
        reasons_html = "".join(f'<div class="reason-item">{r}</div>' for r in reasons)
    else:
        reasons_html = '<div class="no-flag">No significant abnormality detected.</div>'

    st.markdown(f"""
    <div class="panel-card">
      <div class="panel-title">Why the AI flagged this</div>
      {reasons_html}
    </div>
    """, unsafe_allow_html=True)

with e2:
    steps = [
        "Baseline vitals recorded",
        "Trend engine analyzed recent physiological changes",
        *[f"Flag detected: {r}" for r in reasons[:3]],
        f"Composite risk classified as {level}",
    ]
    steps_html = "".join(
        f'<div class="tl-step"><div class="tl-num">{i+1}</div><div class="tl-text">{s}</div></div>'
        for i, s in enumerate(steps)
    )
    st.markdown(f"""
    <div class="panel-card">
      <div class="panel-title">Alert progression timeline</div>
      {steps_html}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RECOMMENDED ACTION + QR
# ─────────────────────────────────────────────
a1, a2 = st.columns([1.65, 1])

with a1:
    esc_html = (
        '<span class="escalation-yes">Clinic escalation recommended</span>'
        if level != "LOW" else
        '<span class="escalation-no">No escalation required</span>'
    )
    st.markdown(f"""
    <div class="panel-card">
      <div class="panel-title">Recommended Action</div>
      <div class="rec-label">Immediate guidance</div>
      <div class="rec-text">{rec}</div>
      <div class="rec-label">Escalation status</div>
      <div style="margin-top:4px;">{esc_html}</div>
    </div>
    """, unsafe_allow_html=True)

with a2:
    st.markdown('<div class="panel-title" style="margin-top:0.2rem;">QR Health Key</div>', unsafe_allow_html=True)

    if st.button("Generate QR Health Key", use_container_width=True):
        st.session_state.qr_shown = True

    if st.session_state.qr_shown:
        payload = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "patient_id": c["id"], "name": c["name"],
            "risk_score": score, "risk_level": level,
            "hr": hr_now, "spo2": spo2_now, "temperature": temp_now,
            "trends": {"hr": ht, "spo2": st_, "temp": tt},
            "recommendation": rec,
            "reasons": reasons,
        }
        qr_data_uri = build_qr(payload)
        st.markdown(f"""
        <div style="text-align:center; padding: 0.5rem 0;">
          <img src="{qr_data_uri}"
               style="width:200px; height:200px; border-radius:12px;
                      border:2px solid rgba(255,255,255,0.12); display:block; margin:0 auto;" />
          <div style="font-size:0.75rem; color:#6B8CAE; margin-top:8px;">
            Scan at clinic · Full health summary encoded
          </div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("View exported payload"):
            st.json(payload)


# ─────────────────────────────────────────────
# CLINIC HANDOFF SUMMARY
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Clinic-Ready Handoff Summary</div>', unsafe_allow_html=True)

handoff_rows = [
    ("Patient",           f"{c['name']} ({c['id']})"),
    ("Risk level",        f"{level} — composite score {score}/100"),
    ("Latest vitals",     f"HR {hr_now} BPM · SpO2 {spo2_now}% · Temp {temp_now}°F"),
    ("Trend summary",     f"HR {ht} · SpO2 {st_} · Temp {tt}"),
    ("Symptoms",          ", ".join(c["symptoms"])),
    ("Recommended action",rec),
]
rows_html = "".join(
    f'<div class="handoff-row"><span class="hk">{k}</span><span class="hv">{v}</span></div>'
    for k, v in handoff_rows
)
st.markdown(f"""
<div class="panel-card">
  {rows_html}
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)