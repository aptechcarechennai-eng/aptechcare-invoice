import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="AP Tech Care",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_theme_css():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
.block-container { padding: 2rem 2.5rem 2rem !important; max-width: 100% !important; }

/* App background */
.stApp { background: #F5F6FA !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E8EAED !important;
    min-width: 220px !important;
}
[data-testid="stSidebar"] * { color: #374151 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #6B7280 !important;
    text-align: left !important;
    width: 100% !important;
    padding: 9px 14px !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #F3F4F6 !important;
    color: #111827 !important;
}

/* ── CARDS ── */
.ap-card {
    background: #FFFFFF;
    border: 1px solid #E8EAED;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 10px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    transition: box-shadow 0.15s;
}
.ap-card:hover { box-shadow: 0 3px 8px rgba(0,0,0,0.08); }

/* ── BADGES ── */
.badge-paid    { background: #DCFCE7; color: #166534;   padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-overdue { background: #FEE2E2; color: #991B1B;   padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-sent    { background: #DBEAFE; color: #1E40AF;   padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-draft   { background: #F3F4F6; color: #6B7280;   padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-read    { background: #FEF9C3; color: #854D0E;   padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }

/* ── PAGE TITLE ── */
.page-title { font-size: 22px; font-weight: 700; color: #111827; margin: 0 0 2px; }
.page-sub   { font-size: 13px; color: #9CA3AF; margin: 0 0 20px; }

/* ── INV ROW ── */
.inv-customer { font-weight: 600; color: #111827; font-size: 14px; }
.inv-meta     { font-size: 12px; color: #9CA3AF; margin-top: 2px; }
.inv-amount   { font-weight: 700; font-size: 15px; color: #111827; }

/* ── DIVIDER ── */
.ap-divider { border: none; border-top: 1px solid #E8EAED; margin: 16px 0; }

/* ── PRIMARY BUTTON ── */
.stButton > button[kind="primary"] {
    background: #4F46E5 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

/* ── METRIC ── */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E8EAED;
    border-radius: 12px;
    padding: 16px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
[data-testid="metric-container"] label {
    font-size: 12px !important;
    color: #9CA3AF !important;
    font-weight: 500 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #111827 !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0px;
    background: transparent !important;
    border-bottom: 1px solid #E8EAED !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #9CA3AF !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 8px 18px !important;
    border: none !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #4F46E5 !important;
    border-bottom: 2px solid #4F46E5 !important;
    font-weight: 600 !important;
}

/* ── INPUTS ── */
.stTextInput input, .stTextArea textarea, .stDateInput input {
    border: 1px solid #E8EAED !important;
    border-radius: 8px !important;
    background: #FFFFFF !important;
    color: #111827 !important;
    font-size: 13px !important;
}
.stSelectbox > div > div {
    border: 1px solid #E8EAED !important;
    border-radius: 8px !important;
    font-size: 13px !important;
}
</style>
"""

# ── SESSION INIT ──────────────────────────────────────────────────
def init_session():
    defaults = {
        "page": "home",
        "invoices": [
            {"id": "AP-1001", "type": "invoice", "customer": "TechSoft Pvt Ltd",    "date": "2025-06-01", "due": "2025-06-15", "amount": 18500, "status": "paid",    "items": []},
            {"id": "AP-1002", "type": "invoice", "customer": "InfoBridge Solutions","date": "2025-06-05", "due": "2025-06-20", "amount": 32000, "status": "sent",    "items": []},
            {"id": "AP-1003", "type": "invoice", "customer": "Nexus Digital",       "date": "2025-06-10", "due": "2025-06-10", "amount": 7500,  "status": "overdue", "items": []},
            {"id": "AP-1004", "type": "invoice", "customer": "CloudVerse Inc",      "date": "2025-06-12", "due": "2025-06-26", "amount": 54000, "status": "draft",   "items": []},
            {"id": "AP-1005", "type": "invoice", "customer": "ByteWave Tech",       "date": "2025-06-14", "due": "2025-06-28", "amount": 12300, "status": "sent",    "items": []},
        ],
        "customers": [
            {"name": "TechSoft Pvt Ltd",    "email": "techsoft@example.com",  "phone": "9800001111", "address": "Chennai"},
            {"name": "InfoBridge Solutions","email": "info@infobridge.com",   "phone": "9800002222", "address": "Bangalore"},
            {"name": "Nexus Digital",       "email": "hello@nexusdigital.in", "phone": "9800003333", "address": "Hyderabad"},
            {"name": "CloudVerse Inc",      "email": "admin@cloudverse.io",   "phone": "9800004444", "address": "Mumbai"},
            {"name": "ByteWave Tech",       "email": "support@bytewave.in",   "phone": "9800005555", "address": "Pune"},
        ],
        "items_db": [
            {"name": "AMC Service",      "code": "AMC001", "price": 5000, "unit": "per year",   "desc": "Annual Maintenance Contract"},
            {"name": "Hardware Repair",  "code": "HW002",  "price": 1500, "unit": "per unit",   "desc": "Hardware diagnosis and repair"},
            {"name": "Software Install", "code": "SW003",  "price": 800,  "unit": "per device", "desc": "Software installation and setup"},
            {"name": "Network Setup",    "code": "NW004",  "price": 3500, "unit": "per job",    "desc": "Network configuration and setup"},
        ],
        "settings": {
            "company_name": "AP Tech Care",
            "company_email": "info@aptechcare.in",
            "company_phone": "+91 98765 43210",
            "company_address1": "Chennai, Tamil Nadu",
            "gst_no": "33XXXXX1234Z1",
            "currency": "INR",
            "date_format": "DD/MM/YYYY",
            "theme": "default",
            "tax_rate": 18,
            "payment_instructions": "Please transfer to our bank account.\nUPI ID: aptechcare@upi\nBank: HDFC | A/c: XXXXXXXXXXXX | IFSC: HDFC0001234",
            "next_invoice_no": 1006,
        },
        "transactions": [],
        "show_new_invoice": False,
        "selected_invoice": None,
        "doc_type": "invoice",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Safe migration: string customers → dicts
    st.session_state.customers = [
        {"name": c, "email": "", "phone": "", "address": ""} if isinstance(c, str) else c
        for c in st.session_state.customers
    ]

init_session()
st.markdown(get_theme_css(), unsafe_allow_html=True)

def nav(page):
    st.session_state.page = page
    st.rerun()

# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 16px 16px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:24px;">
        <div style="width:36px;height:36px;border-radius:9px;background:#4F46E5;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
          <span style="color:#fff;font-weight:800;font-size:12px;">AP</span>
        </div>
        <div>
          <div style="font-weight:700;font-size:14px;color:#111827;line-height:1.2;">AP Tech Care</div>
          <div style="font-size:11px;color:#9CA3AF;">Smart Tech Solutions</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    cur = st.session_state.page

    # Active highlight CSS
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] [data-testid="stButton-nav_{cur}"] > button {{
        background: #EEF2FF !important;
        color: #4F46E5 !important;
        font-weight: 600 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:0 12px;margin-bottom:4px;font-size:10px;font-weight:600;color:#9CA3AF;letter-spacing:1px;">DOCUMENTS</div>', unsafe_allow_html=True)

    nav_items = [
        ("home",     "🏠", "Home"),
        ("invoice",  "📄", "Invoices"),
        ("estimate", "📋", "Estimates"),
        ("credit",   "💳", "Credit Notes"),
        ("delivery", "🚚", "Delivery Notes"),
        ("purchase", "🛒", "Purchase Orders"),
    ]
    for pid, icon, label in nav_items:
        if st.button(f"{icon}  {label}", key=f"nav_{pid}", use_container_width=True):
            nav(pid)

    st.markdown('<div style="padding:0 12px;margin:12px 0 4px;font-size:10px;font-weight:600;color:#9CA3AF;letter-spacing:1px;">MANAGE</div>', unsafe_allow_html=True)

    more_items = [
        ("cashflow",  "📊", "Cash Flow"),
        ("reports",   "📈", "Reports"),
        ("items",     "📦", "Items"),
        ("customers", "👥", "Customers"),
        ("settings",  "⚙️", "Settings"),
    ]
    for pid, icon, label in more_items:
        if st.button(f"{icon}  {label}", key=f"nav_{pid}", use_container_width=True):
            nav(pid)

    st.markdown('<div style="margin:16px 12px 0;border-top:1px solid #E8EAED;padding-top:12px;">', unsafe_allow_html=True)
    if st.button("🚪  Logout", key="nav_logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── BACK BUTTON (non-home pages) ──────────────────────────────────
if st.session_state.page != "home":
    if st.button("← Home", key="global_back"):
        nav("home")
    st.markdown("<div class='ap-divider'></div>", unsafe_allow_html=True)

# ── PAGE ROUTING ──────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    try:
        from pages.home import render
    except ModuleNotFoundError:
        from pages.Home import render
    render()
elif page in ["invoice", "estimate", "credit", "delivery", "purchase"]:
    from pages.documents import render
    render(page)
elif page == "cashflow":
    from pages.cashflow import render
    render()
elif page == "reports":
    from pages.reports import render
    render()
elif page == "items":
    from pages.items import render
    render()
elif page == "customers":
    from pages.customers import render
    render()
elif page == "settings":
    from pages.settings import render
    render()
