"""
Streamlit UI for the Fake Job Posting Detector — dark dashboard theme.

Run with:
    streamlit run streamlit_app.py

Requires models/*.pkl to exist (see README) — run the notebook first if
you haven't trained/saved the model yet.
"""

import streamlit as st

from extraction_utils import parse_pasted_posting
from predict import FraudDetector

st.set_page_config(page_title="Fake Job Posting Detector", page_icon="🔍", layout="wide")

# ---------------------------------------------------------------------------
# Palette — lifted from the reference dashboard.
# ---------------------------------------------------------------------------
BG        = "#0c0f16"
PANEL     = "#12151d"
CARD      = "#151923"
BORDER    = "rgba(255,255,255,0.07)"
TEXT      = "#e9e9ee"
SUBTEXT   = "#8b8f9c"
MUTED     = "#5c606c"
TEAL      = "#20e3c2"
PURPLE    = "#8b7cf6"
PINK      = "#ec4c8f"
YELLOW    = "#f4c94c"

# ---------------------------------------------------------------------------
# Global CSS — recolors Streamlit's own widgets instead of faking them,
# so the real inputs/buttons/expander still work but read as dark UI.
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background: {BG};
    }}
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1300px;
    }}
    [data-testid="stSidebar"] {{
        background: {PANEL};
        border-right: 1px solid {BORDER};
    }}
    h1, h2, h3, h4, p, span, label, div {{
        color: {TEXT};
    }}
    .subtle {{ color: {SUBTEXT}; }}

    /* text inputs / textareas / selects */
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div {{
        background: {CARD} !important;
        border: 1px solid {BORDER} !important;
        color: {TEXT} !important;
        border-radius: 8px !important;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {TEAL} !important;
        box-shadow: 0 0 0 1px {TEAL} !important;
    }}
    .stTextInput label, .stTextArea label, .stSelectbox label {{
        font-size: 11px !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: {SUBTEXT} !important;
    }}

    /* buttons — primary (Check posting) vs secondary (Clear all) get
       distinct colors via Streamlit's own kind/testid, not sibling order */
    .stButton button, div[data-testid="stFormSubmitButton"] button {{
        border-radius: 999px !important;
        border: 1px solid {BORDER} !important;
        background: {CARD} !important;
        color: {TEXT} !important;
        font-weight: 600 !important;
    }}
    button[kind="primary"], [data-testid="baseButton-primary"] {{
        background: {TEAL} !important;
        color: #04211c !important;
        border: none !important;
    }}
    button[kind="secondary"], [data-testid="baseButton-secondary"] {{
        background: rgba(236,76,143,0.12) !important;
        color: {PINK} !important;
        border: 1px solid rgba(236,76,143,0.4) !important;
    }}

    /* expander */
    [data-testid="stExpander"] {{
        background: {CARD};
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
    }}

    /* native bordered containers = our "cards" — one real wrapper,
       so labels/widgets actually render inside the visible border */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: {CARD};
        border: 1px solid {BORDER} !important;
        border-radius: 14px;
    }}
    .card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 18px 20px;
    }}
    .kpi-label {{
        font-size: 11px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {SUBTEXT};
        font-family: monospace;
    }}
    .kpi-value {{
        font-size: 26px;
        font-weight: 700;
        margin-top: 4px;
    }}
    .kpi-sub {{
        font-size: 12px;
        color: {SUBTEXT};
        margin-top: 4px;
    }}
    .chip {{
        display: inline-block;
        padding: 3px 11px;
        margin: 3px 5px 3px 0;
        border-radius: 999px;
        font-size: 11px;
        font-family: monospace;
    }}
    .chip-up   {{ background: rgba(236,76,143,0.15); color: {PINK}; }}
    .chip-down {{ background: rgba(32,227,194,0.15); color: {TEAL}; }}
    hr {{ border-color: {BORDER}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

FIELD_KEYS = [
    "title", "employment_type", "required_experience", "required_education",
    "industry", "department", "company_profile", "description",
    "requirements", "benefits",
]
for k in FIELD_KEYS:
    if k not in st.session_state:
        st.session_state[k] = ""
if "result" not in st.session_state:
    st.session_state["result"] = None
if "checked_empty" not in st.session_state:
    st.session_state["checked_empty"] = False


@st.cache_resource
def load_detector():
    return FraudDetector()


def clear_all():
    for k in FIELD_KEYS:
        st.session_state[k] = ""
    st.session_state["paste_box"] = ""
    st.session_state["result"] = None
    st.session_state["checked_empty"] = False


def run_autofill():
    parsed = parse_pasted_posting(st.session_state.get("paste_box", ""))
    for k, v in parsed.items():
        if k in st.session_state:
            st.session_state[k] = v


def ring(pct, color, label, sub, size=56, inner_font=12):
    """Conic-gradient ring gauge. size/inner_font let the hero result ring
    render much larger than the small 'Model status' rings."""
    deg = max(0, min(pct, 1)) * 360
    hole = size - 14
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:16px; margin-bottom:14px;">
          <div style="width:{size}px; height:{size}px; border-radius:50%;
                      background:conic-gradient({color} {deg}deg, rgba(255,255,255,0.08) {deg}deg);
                      display:flex; align-items:center; justify-content:center; flex-shrink:0;">
            <div style="width:{hole}px; height:{hole}px; border-radius:50%; background:{CARD};
                        display:flex; align-items:center; justify-content:center;
                        font-weight:800; color:{color}; font-size:{inner_font}px;">{int(pct * 100)}%</div>
          </div>
          <div>
            <div style="font-size:14px; font-weight:600;">{label}</div>
            <div style="font-size:12px; color:{SUBTEXT};">{sub}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


try:
    detector = load_detector()
except FileNotFoundError:
    st.error(
        "Model files not found in `models/`. Run the training notebook "
        "(`notebook/eda.ipynb`) first to generate `logistic_regression_model.pkl`, "
        "`tfidf_vectorizer.pkl`, and `tabular_feature_columns.pkl`."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar — branding + the auto-fill helper (secondary, tucked away like
# the reference's left nav rail).
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:24px;">
          <div style="width:48px; height:48px; border-radius:12px;
                      background:linear-gradient(135deg,{TEAL},{PURPLE});
                      display:flex; align-items:center; justify-content:center; font-size:24px;">🔍</div>
          <div style="font-size:22px; font-weight:800; letter-spacing:-0.02em;">FraudShield</div>
        </div>
        <div class="kpi-label">Overview</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div style="margin:10px 0 20px 0; font-size:13px;">
          <div style="color:{TEAL}; font-weight:600;">● Posting checker</div>
          <div class="subtle" style="margin-top:6px;">Model diagnostics</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown('<div class="kpi-label">Auto-fill</div>', unsafe_allow_html=True)
    with st.expander("Paste a posting to auto-fill fields"):
        st.text_area("Paste raw text", key="paste_box", height=120, label_visibility="collapsed")
        st.button("Auto-fill", on_click=run_autofill, use_container_width=True)
        st.caption("Heuristic guess only — always review before checking.")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:12px;">
      <span style="font-size:34px;">🔍</span>
      <span style="font-size:36px; font-weight:800; letter-spacing:-0.02em;">Fake Job Posting Detector</span>
    </div>
    <div class="subtle" style="font-size:12px; letter-spacing:0.06em; text-transform:uppercase;
                font-family:monospace; margin-top:6px; margin-left:2px;">
    TEXT + TABULAR FUSION · TF-IDF + LOGISTIC REGRESSION
    </div>
    """,  # noqa: F541
    unsafe_allow_html=True,
)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# KPI strip — mirrors the four stat cards at the top of the reference.
# ---------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
kpis = [
    (k1, "PR-AUC", "0.89", "held-out test set", TEAL),
    (k2, "Precision (Fraud)", "61%", "of flagged = fraud", PURPLE),
    (k3, "Recall (Fraud)", "90%", "of fraud caught", PINK),
    (k4, "Fields tracked", str(len(FIELD_KEYS)), "text + tabular", YELLOW),
]
for col, label, value, sub, color in kpis:
    with col:
        st.markdown(
            f"""
            <div class="card">
              <div class="kpi-label">{label}</div>
              <div class="kpi-value" style="color:{color};">{value}</div>
              <div class="kpi-sub">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Main grid — form card (left) + result card (right)
# ---------------------------------------------------------------------------
main_col, side_col = st.columns([2.3, 1], gap="large")

with main_col:
    with st.container(border=True):
        st.markdown('<div class="kpi-label">Posting details</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        with st.form("posting_form", border=False):
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Job title", key="title", placeholder="e.g. Senior Data Analyst")
                st.selectbox(
                    "Employment type",
                    ["", "Full-time", "Part-time", "Contract", "Temporary", "Other"],
                    key="employment_type",
                )
                st.selectbox(
                    "Required experience",
                    ["", "Internship", "Entry level", "Associate", "Mid-Senior level",
                     "Director", "Executive", "Not Applicable"],
                    key="required_experience",
                )
                st.text_input("Industry", key="industry", placeholder="e.g. Marketing and Advertising")
            with c2:
                st.selectbox(
                    "Required education",
                    ["", "High School or equivalent", "Bachelor's Degree",
                     "Master's Degree", "Doctorate", "Some College Coursework Completed",
                     "Unspecified"],
                    key="required_education",
                )
                st.text_input("Department", key="department", placeholder="e.g. Sales")

            t1, t2 = st.columns(2)
            with t1:
                st.text_area("Company profile", key="company_profile", height=140)
            with t2:
                st.text_area("Job description", key="description", height=140)

            b1, b2 = st.columns([1, 1])
            with b1:
                check_clicked = st.form_submit_button(
                    "Check posting", type="primary", use_container_width=True
                )
            with b2:
                clear_clicked = st.form_submit_button("Clear all", use_container_width=True)

    if clear_clicked:
        clear_all()
        st.rerun()

    if check_clicked:
        title = st.session_state["title"]
        description = st.session_state["description"]
        if not title and not description:
            st.session_state["checked_empty"] = True
            st.session_state["result"] = None
        else:
            st.session_state["checked_empty"] = False
            posting = {
                k: (st.session_state[k] if st.session_state[k] not in ("", None) else None)
                for k in FIELD_KEYS
            }
            with st.spinner("Scoring posting…"):
                st.session_state["result"] = detector.predict(posting)

    if st.session_state["checked_empty"]:
        st.warning("Enter at least a title or description before checking.")

with side_col:
    with st.container(border=True):
        st.markdown('<div class="kpi-label">Result</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        result = st.session_state.get("result")
        if result is None:
            st.markdown(
                '<div class="subtle" style="font-size:13px;">Fill in the posting details and '
                'click <b>Check posting</b> — the result will appear here.</div>',
                unsafe_allow_html=True,
            )
        else:
            proba = result["fraud_probability"]
            label = result["label"]
            is_fraud = label == "Fraud"
            color = PINK if is_fraud else TEAL
            verdict = "Likely fraudulent" if is_fraud else "Likely legitimate"
            icon = "⚠️" if is_fraud else "✅"

            # Big, unmissable verdict badge — the headline of the card.
            st.markdown(
                f"""
                <div style="background:rgba({'236,76,143' if is_fraud else '32,227,194'},0.14);
                            border:1px solid {color}; border-radius:12px;
                            padding:14px 16px; margin-bottom:16px;
                            display:flex; align-items:center; gap:10px;">
                  <span style="font-size:22px;">{icon}</span>
                  <span style="font-size:18px; font-weight:800; color:{color};">{verdict}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            ring(proba, color, "Fraud probability", f"{proba:.1%} confidence", size=96, inner_font=22)

            reasons = result.get("reasons", [])
            if reasons:
                st.markdown('<div class="kpi-label" style="margin-top:10px;">Why</div>', unsafe_allow_html=True)
                chips = ""
                for r in reasons:
                    cls = "chip-up" if r["direction"] == "toward Fraud" else "chip-down"
                    arrow = "▲" if r["direction"] == "toward Fraud" else "▼"
                    chips += f'<span class="chip {cls}">{arrow} {r["feature"]}</span>'
                st.markdown(chips, unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="kpi-label">Model status</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        ring(0.89, TEAL, "PR-AUC", "held-out test")
        ring(0.61, PURPLE, "Precision", "fraud class")
        ring(0.90, YELLOW, "Recall", "fraud class")