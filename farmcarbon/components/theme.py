
import streamlit as st
import plotly.io as pio


def apply_theme():
    pio.templates.default = "plotly_dark"

    st.markdown("""
    <style>
    :root {
        --bg: #101014;
        --panel: #1B1B22;
        --panel2: #23232C;
        --red: #E53945;
        --red-hover: #FF6972;
        --ivory: #F3F1EE;
        --text: #F5F3F0;
        --muted: #A7A5AD;
        --border: #34343E;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(16,16,20,0.95);
        border-bottom: 1px solid var(--border);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4 {
        color: var(--ivory) !important;
        letter-spacing: -0.025em;
    }

    h1 {
        font-weight: 800 !important;
    }

    p, label, li {
        color: var(--text);
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted) !important;
    }

    /* Sidebar */

    [data-testid="stSidebar"] {
        background: #15151B;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebarNav"] {
        display: none;
    }

    .fc-brand {
        padding: 12px 0 18px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 15px;
    }

    .fc-brand-name {
        color: var(--ivory);
        font-size: 21px;
        font-weight: 800;
    }

    .fc-brand-mark {
        color: var(--red);
        font-size: 24px;
        margin-right: 7px;
    }

    .fc-brand-caption {
        color: var(--muted);
        font-size: 10px;
        letter-spacing: 2px;
        margin-top: 5px;
    }

    /* Metric cards */

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #25252E, #19191F);
        border: 1px solid var(--border);
        border-left: 3px solid var(--red);
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.18);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--ivory) !important;
        font-weight: 800;
    }

    /* Buttons */

    .stButton > button,
    .stDownloadButton > button,
    [data-testid="stFormSubmitButton"] > button {
        border-radius: 10px;
        border: 1px solid var(--red);
        font-weight: 650;
        transition: 0.2s ease;
    }

    .stButton > button[kind="primary"],
    [data-testid="stFormSubmitButton"] > button[kind="primary"] {
        background: var(--red);
        color: white;
        border-color: var(--red);
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: var(--red-hover);
        color: white;
        box-shadow: 0 0 0 2px rgba(229,57,69,0.2);
        transform: translateY(-1px);
    }

    /* Inputs */

    input, textarea,
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div {
        background: #202029 !important;
        color: var(--text) !important;
        border-color: #41414D !important;
        border-radius: 9px !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"] {
        background: #22222A !important;
    }

    [data-baseweb="option"] {
        color: var(--text) !important;
    }

    /* Tabs */

    [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid var(--border);
    }

    button[data-baseweb="tab"] {
        color: var(--muted);
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--ivory);
        border-bottom: 3px solid var(--red);
    }

    /* Expanders and tables */

    [data-testid="stExpander"] {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }

    [data-testid="stAlert"] {
        border-radius: 11px;
    }

    [data-testid="stProgressBar"] > div > div {
        background: var(--red);
    }

    hr {
        border-color: var(--border) !important;
    }

    a {
        color: #FF737C !important;
    }

    @media(max-width: 760px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Global navigation
    with st.sidebar:
        st.markdown("""
        <div class="fc-brand">
            <span class="fc-brand-mark">●</span>
            <span class="fc-brand-name">FarmCarbon MRV</span>
            <div class="fc-brand-caption">
                AGRICULTURAL CARBON INTELLIGENCE
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.caption("WORKSPACE")

        st.page_link("app.py", label="Overview", icon="🏠")
        st.page_link("pages/1_Farm_Registry.py",
                     label="Farm Registry", icon="🌾")
        st.page_link("pages/2_Satellite_Monitoring.py",
                     label="Satellite Monitoring", icon="🛰️")
        st.page_link("pages/3_Soil_Carbon_Analysis.py",
                     label="Soil Carbon Analysis", icon="🧪")
        st.page_link("pages/4_Agricultural_Practices.py",
                     label="Agricultural Practices", icon="🌱")
        st.page_link("pages/5_MRV_Reports.py",
                     label="MRV Reports & Review", icon="📊")
        st.page_link("pages/6_Methodology.py",
                     label="Methodology", icon="📘")

        st.divider()
        st.caption("LOCAL-FIRST DEMONSTRATOR")
        st.caption("JSON + GeoJSON · No SQL database")
