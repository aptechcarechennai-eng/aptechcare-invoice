import streamlit as st
import os
from datetime import datetime

# ── PAGE CONFIG ─────────────────────────────────────────────────
st.set_page_config(
    page_title="AP Tech Care",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="auto"
)

# ── THEME CSS ────────────────────────────────────────────────────
def get_theme_css(theme="default"):
    themes = {
        "default": {
            "bg": "#F8F9FA", "sidebar_bg": "#0F1923", "card": "#FFFFFF",
            "accent": "#00C896", "text": "#1A1A2E", "sub": "#6B7280",
            "border": "#E5E7EB", "badge_paid": "#D1FAE5", "badge_paid_text": "#065F46",
            "badge_overdue": "#FEE2E2", "badge_overdue_text": "#991B1B",
            "badge_sent": "#DBEAFE", "badge_sent_text": "#1E40AF",
            "badge_draft": "#F3F4F6", "badge_draft_text": "#374151",
        },
        "classic": {
            "bg": "#0F1923", "sidebar_bg": "#070D14", "card": "#1A2535",
            "accent": "#00C896", "text": "#E2E8F0", "sub": "#94A3B8",
            "border": "#2D3748", "badge_paid": "#065F46", "badge_paid_text": "#D1FAE5",
            "badge_overdue": "#991B1B", "badge_overdue_text": "#FEE2E2",
            "badge_sent": "#1E40AF", "badge_sent_text": "#DBEAFE",
            "badge_draft": "#374151", "badge_draft_text": "#F3F4F6",
        },
        "ultra": {
            "bg": "#FFF8F0", "sidebar_bg": "#1E1B4B", "card": "#FFFFFF",
            "accent": "#F97316", "text": "#1E1B4B", "sub": "#6D28D9",
            "border": "#DDD6FE", "badge_paid": "#D1FAE5", "badge_paid_text": "#065F46",
            "badge_overdue": "#FEE2E2", "badge_overdue_text": "#991B1B",
            "badge_sent": "#EDE9FE", "badge_sent_text": "#5B21B6",
            "badge_draft": "#F3F4F6", "badge_draft_text": "#374151",
        }
    }
    t = themes.get(theme, themes["default"])
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* Hide default streamlit elements */
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 1.5rem 2rem 2rem !important; max-width: 100% !important; }}

/* Main background */
.stApp {{ background: {t["bg"]} !important; }}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: {t["sidebar_bg"]} !important;
    min-width: 240px !important;
}}
[data-testid="stSidebar"] * {{ color: rgba(255,255,255,0.7) !important; }}
[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    border: none !important;
    color: rgba(255,255,255,0.6) !important;
    text-align: left !important;
    width: 100% !important;
    padding: 10px 16px !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(0,200,150,0.15) !important;
    color: #00C896 !important;
}}

/* Cards */
.ap-card {{
    background: {t["card"]};
    border: 1px solid {t["border"]};
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: all 0.2s;
}}
.ap-card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}

/* Stat cards */
.stat-card {{
    background: {t["card"]};
    border: 1px solid {t["border"]};
    border-radius: 14px;
    padding: 18px 20px;
    text-align: left;
}}
.stat-label {{ font-size: 12px; font-weight: 600; color: {t["sub"]}; margin: 0; text-transform: uppercase; letter-spacing: 0.5px; }}
.stat-value {{ font-size: 28px; font-weight: 900; color: {t["text"]}; margin: 6px 0 0; }}

/* Badges */
.badge-paid {{ background: {t["badge_paid"]}; color: {t["badge_paid_text"]}; padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
.badge-overdue {{ background: {t["badge_overdue"]}; color: {t["badge_overdue_text"]}; padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
.badge-sent {{ background: {t["badge_sent"]}; color: {t["badge_sent_text"]}; padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
.badge-draft {{ background: {t["badge_draft"]}; color: {t["badge_draft_text"]}; padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
.badge-read {{ background: #FEF3C7; color: #92400E; padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; }}

/* Page title */
.page-title {{ font-size: 24px; font-weight: 900; color: {t["text"]}; margin: 0 0 4px; }}
.page-sub {{ font-size: 13px; color: {t["sub"]}; margin: 0 0 24px; }}

/* Invoice row */
.inv-row {{
    background: {t["card"]};
    border: 1px solid {t["border"]};
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    transition: all 0.2s;
}}
.inv-row:hover {{ border-color: {t["accent"]}; box-shadow: 0 2px 8px rgba(0,200,150,0.12); }}
.inv-customer {{ font-weight: 700; color: {t["text"]}; font-size: 14px; }}
.inv-meta {{ font-size: 12px; color: {t["sub"]}; margin-top: 2px; }}
.inv-amount {{ font-weight: 900; font-size: 16px; color: {t["text"]}; text-align: right; }}

/* Section header */
.section-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}}

/* Accent button */
.stButton > button[kind="primary"] {{
    background: {t["accent"]} !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
}}

/* Input styling */
.stTextInput input, .stSelectbox select, .stTextArea textarea, .stDateInput input {{
    border: 1px solid {t["border"]} !important;
    border-radius: 8px !important;
    background: {t["card"]} !important;
    color: {t["text"]} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* Divider */
.ap-divider {{ border: none; border-top: 1px solid {t["border"]}; margin: 20px 0; }}

/* Logo box */
.logo-box {{
    background: #0F1923;
    border-radius: 12px;
    width: 48px; height: 48px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 8px;
}}

/* Alert box */
.ap-alert-overdue {{
    background: #FEE2E2;
    border-left: 4px solid #EF4444;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #991B1B;
    margin-bottom: 8px;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    background: transparent !important;
    border-bottom: 2px solid {t["border"]} !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: 8px 8px 0 0 !important;
    color: {t["sub"]} !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
    border: none !important;
}}
.stTabs [aria-selected="true"] {{
    color: {t["accent"]} !important;
    border-bottom: 2px solid {t["accent"]} !important;
}}

/* Metric */
[data-testid="metric-container"] {{
    background: {t["card"]};
    border: 1px solid {t["border"]};
    border-radius: 14px;
    padding: 16px !important;
}}
</style>
"""

# ── SESSION INIT ─────────────────────────────────────────────────
def init_session():
    defaults = {
        "page": "home",
        "theme": "default",
        "logged_in": False,
        "user": None,
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

    # Safe migration: convert string customers to dicts if needed
    st.session_state.customers = [
        {"name": c, "email": "", "phone": "", "address": ""} if isinstance(c, str) else c
        for c in st.session_state.customers
    ]

init_session()

# ── APPLY THEME ──────────────────────────────────────────────────
theme = st.session_state.settings.get("theme", "default")
st.markdown(get_theme_css(theme), unsafe_allow_html=True)

# ── HELPERS ──────────────────────────────────────────────────────
def badge(status):
    labels = {"paid": "✓ Paid", "sent": "→ Sent", "overdue": "⚠ Overdue", "draft": "✎ Draft", "read": "👁 Read"}
    return f'<span class="badge-{status}">{labels.get(status, status.title())}</span>'

def fmt_currency(amount):
    s = st.session_state.settings
    sym = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£"}.get(s.get("currency", "INR"), "₹")
    return f"{sym}{amount:,.0f}"

def fmt_date(date_str):
    if not date_str:
        return ""
    try:
        d = datetime.strptime(str(date_str), "%Y-%m-%d")
        fmt = st.session_state.settings.get("date_format", "DD/MM/YYYY")
        if fmt == "DD/MM/YYYY":   return d.strftime("%d/%m/%Y")
        elif fmt == "MM/DD/YYYY": return d.strftime("%m/%d/%Y")
        elif fmt == "YYYY/MM/DD": return d.strftime("%Y/%m/%d")
        elif fmt == "19 Jun 2025": return d.strftime("%d %b %Y")
        elif fmt == "Jun 19, 2025": return d.strftime("%b %d, %Y")
        return d.strftime("%d/%m/%Y")
    except:
        return str(date_str)

def nav(page):
    st.session_state.page = page
    st.rerun()

# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 16px 12px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom:8px;">
      <div style="display:flex; align-items:center; gap:10px;">
        <div style="width:44px;height:44px;border-radius:12px;background:#00C896;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
          <span style="color:#fff;font-weight:900;font-size:14px;letter-spacing:0.5px;">AP</span>
        </div>
        <div>
          <div style="font-weight:800;font-size:15px;color:#fff;line-height:1.2;">AP Tech Care</div>
          <div style="font-size:10px;color:rgba(255,255,255,0.4);margin-top:1px;">Smart Tech Solutions</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    cur = st.session_state.page

    # Active nav highlight via CSS
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] [data-testid="stButton-nav_{cur}"] > button {{
        background: rgba(0,200,150,0.18) !important;
        color: #00C896 !important;
        font-weight: 700 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    nav_items = [
        ("home",     "🏠", "Home"),
        ("invoice",  "📄", "Invoice"),
        ("estimate", "📋", "Estimate"),
        ("credit",   "💳", "Credit Notes"),
        ("delivery", "🚚", "Delivery Notes"),
        ("purchase", "🛒", "Purchase Order"),
    ]
    for pid, icon, label in nav_items:
        if st.button(f"{icon}  {label}", key=f"nav_{pid}", use_container_width=True):
            nav(pid)

    st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.08);margin:8px 0;padding-top:4px;"><span style="font-size:10px;color:rgba(255,255,255,0.3);font-weight:700;letter-spacing:1px;padding:0 16px;">MORE</span></div>', unsafe_allow_html=True)

    more_items = [
        ("cashflow",   "📊", "Cash Flow"),
        ("reports",    "📈", "Reports"),
        ("items",      "📦", "Items"),
        ("customers",  "👥", "Customers"),
        ("settings",   "⚙️", "Settings"),
    ]
    for pid, icon, label in more_items:
        if st.button(f"{icon}  {label}", key=f"nav_{pid}", use_container_width=True):
            nav(pid)

    st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.08);margin-top:8px;padding-top:8px;">', unsafe_allow_html=True)
    if st.button("🚪  Logout", key="nav_logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── PAGE ROUTING ─────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    from home import render
    render()
elif page in ["invoice", "estimate", "credit", "delivery", "purchase"]:
    from documents import render
    render(page)
elif page == "cashflow":
    from cashflow import render
    render()
elif page == "reports":
    from reports import render
    render()
elif page == "items":
    from items import render
    render()
elif page == "customers":
    from customers import render
    render()
elif page == "settings":
    from settings import render
    render()
