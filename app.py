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
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
.block-container { padding: 2rem 2.5rem 2rem !important; max-width: 100% !important; }
.stApp { background: #F5F6FA !important; }
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E8EAED !important;
    min-width: 220px !important;
}
[data-testid="stSidebar"] * { color: #374151 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; border: none !important;
    color: #6B7280 !important; text-align: left !important;
    width: 100% !important; padding: 9px 14px !important;
    border-radius: 8px !important; font-size: 13px !important;
    font-weight: 500 !important; transition: all 0.15s !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #F3F4F6 !important; color: #111827 !important;
}
.ap-card {
    background: #FFFFFF; border: 1px solid #E8EAED;
    border-radius: 12px; padding: 18px 20px; margin-bottom: 10px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04); transition: box-shadow 0.15s;
}
.ap-card:hover { box-shadow: 0 3px 8px rgba(0,0,0,0.08); }
.badge-paid    { background:#DCFCE7; color:#166534;  padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-overdue { background:#FEE2E2; color:#991B1B;  padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-sent    { background:#DBEAFE; color:#1E40AF;  padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-draft   { background:#F3F4F6; color:#6B7280;  padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-read    { background:#FEF9C3; color:#854D0E;  padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.page-title { font-size:22px; font-weight:700; color:#111827; margin:0 0 2px; }
.page-sub   { font-size:13px; color:#9CA3AF; margin:0 0 20px; }
.inv-customer { font-weight:600; color:#111827; font-size:14px; }
.inv-meta     { font-size:12px; color:#9CA3AF; margin-top:2px; }
.inv-amount   { font-weight:700; font-size:15px; color:#111827; }
.ap-divider   { border:none; border-top:1px solid #E8EAED; margin:16px 0; }
.stButton > button[kind="primary"] {
    background:#4F46E5 !important; color:white !important;
    border:none !important; border-radius:8px !important;
    font-weight:600 !important; font-size:13px !important;
}
[data-testid="metric-container"] {
    background:#FFFFFF; border:1px solid #E8EAED;
    border-radius:12px; padding:16px !important;
    box-shadow:0 1px 2px rgba(0,0,0,0.04);
}
[data-testid="metric-container"] label { font-size:12px !important; color:#9CA3AF !important; font-weight:500 !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size:22px !important; font-weight:700 !important; color:#111827 !important; }
.stTabs [data-baseweb="tab-list"] { gap:0px; background:transparent !important; border-bottom:1px solid #E8EAED !important; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:#9CA3AF !important; font-weight:500 !important; font-size:13px !important; padding:8px 18px !important; border:none !important; border-radius:0 !important; }
.stTabs [aria-selected="true"] { color:#4F46E5 !important; border-bottom:2px solid #4F46E5 !important; font-weight:600 !important; }
.stTextInput input, .stTextArea textarea, .stDateInput input { border:1px solid #E8EAED !important; border-radius:8px !important; background:#FFFFFF !important; color:#111827 !important; font-size:13px !important; }
.stSelectbox > div > div { border:1px solid #E8EAED !important; border-radius:8px !important; font-size:13px !important; }
</style>
"""

# ── SESSION INIT ──────────────────────────────────────────────────
def init_session():
    defaults = {
        "page": "home",
        "invoices": [
            {"id":"AP-1001","type":"invoice","customer":"TechSoft Pvt Ltd",   "date":"2025-06-01","due":"2025-06-15","amount":18500,"status":"paid",   "items":[]},
            {"id":"AP-1002","type":"invoice","customer":"InfoBridge Solutions","date":"2025-06-05","due":"2025-06-20","amount":32000,"status":"sent",   "items":[]},
            {"id":"AP-1003","type":"invoice","customer":"Nexus Digital",      "date":"2025-06-10","due":"2025-06-10","amount":7500, "status":"overdue","items":[]},
            {"id":"AP-1004","type":"invoice","customer":"CloudVerse Inc",     "date":"2025-06-12","due":"2025-06-26","amount":54000,"status":"draft",  "items":[]},
            {"id":"AP-1005","type":"invoice","customer":"ByteWave Tech",      "date":"2025-06-14","due":"2025-06-28","amount":12300,"status":"sent",   "items":[]},
        ],
        "customers": [
            {"name":"TechSoft Pvt Ltd",   "email":"techsoft@example.com", "phone":"9800001111","address":"Chennai"},
            {"name":"InfoBridge Solutions","email":"info@infobridge.com",  "phone":"9800002222","address":"Bangalore"},
            {"name":"Nexus Digital",      "email":"hello@nexusdigital.in","phone":"9800003333","address":"Hyderabad"},
            {"name":"CloudVerse Inc",     "email":"admin@cloudverse.io",  "phone":"9800004444","address":"Mumbai"},
            {"name":"ByteWave Tech",      "email":"support@bytewave.in",  "phone":"9800005555","address":"Pune"},
        ],
        "items_db": [
            {"name":"AMC Service",     "code":"AMC001","price":5000,"unit":"per year",  "desc":"Annual Maintenance Contract"},
            {"name":"Hardware Repair", "code":"HW002", "price":1500,"unit":"per unit",  "desc":"Hardware diagnosis and repair"},
            {"name":"Software Install","code":"SW003", "price":800, "unit":"per device","desc":"Software installation and setup"},
            {"name":"Network Setup",   "code":"NW004", "price":3500,"unit":"per job",   "desc":"Network configuration and setup"},
        ],
        "settings": {
            "company_name":"AP Tech Care","company_email":"info@aptechcare.in",
            "company_phone":"+91 98765 43210","company_address1":"Chennai, Tamil Nadu",
            "gst_no":"33XXXXX1234Z1","currency":"INR","date_format":"DD/MM/YYYY",
            "theme":"default","tax_rate":18,
            "payment_instructions":"Please transfer to our bank account.\nUPI ID: aptechcare@upi\nBank: HDFC | A/c: XXXXXXXXXXXX | IFSC: HDFC0001234",
            "next_invoice_no":1006,
        },
        "transactions":[],"show_new_invoice":False,"selected_invoice":None,"doc_type":"invoice",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    st.session_state.customers = [
        {"name":c,"email":"","phone":"","address":""} if isinstance(c,str) else c
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
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
        <div style="width:36px;height:36px;border-radius:9px;background:#4F46E5;display:flex;align-items:center;justify-content:center;">
          <span style="color:#fff;font-weight:800;font-size:12px;">AP</span>
        </div>
        <div>
          <div style="font-weight:700;font-size:14px;color:#111827;">AP Tech Care</div>
          <div style="font-size:11px;color:#9CA3AF;">Smart Tech Solutions</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    cur = st.session_state.page
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] [data-testid="stButton-nav_{cur}"] > button {{
        background:#EEF2FF !important; color:#4F46E5 !important; font-weight:600 !important;
    }}
    </style>""", unsafe_allow_html=True)

    st.markdown('<div style="padding:0 12px;margin-bottom:4px;font-size:10px;font-weight:600;color:#9CA3AF;letter-spacing:1px;">DOCUMENTS</div>', unsafe_allow_html=True)
    for pid, icon, label in [
        ("home","🏠","Home"),("invoice","📄","Invoices"),("estimate","📋","Estimates"),
        ("credit","💳","Credit Notes"),("delivery","🚚","Delivery Notes"),("purchase","🛒","Purchase Orders"),
    ]:
        if st.button(f"{icon}  {label}", key=f"nav_{pid}", use_container_width=True):
            nav(pid)

    st.markdown('<div style="padding:0 12px;margin:12px 0 4px;font-size:10px;font-weight:600;color:#9CA3AF;letter-spacing:1px;">MANAGE</div>', unsafe_allow_html=True)
    for pid, icon, label in [
        ("cashflow","📊","Cash Flow"),("reports","📈","Reports"),
        ("items","📦","Items"),("customers","👥","Customers"),("settings","⚙️","Settings"),
    ]:
        if st.button(f"{icon}  {label}", key=f"nav_{pid}", use_container_width=True):
            nav(pid)

    st.markdown("---")
    if st.button("🚪  Logout", key="nav_logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ── BACK BUTTON ───────────────────────────────────────────────────
if st.session_state.page != "home":
    if st.button("← Home", key="global_back"):
        nav("home")
    st.markdown("<div class='ap-divider'></div>", unsafe_allow_html=True)

# ── HOME PAGE (inline — no import needed) ─────────────────────────
def render_home():
    invoices = st.session_state.invoices

    st.markdown('<p class="page-title">Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">AP Tech Care — Smart Tech Solutions</p>', unsafe_allow_html=True)

    # Stats
    total       = len(invoices)
    paid_amt    = sum(i["amount"] for i in invoices if i["status"] == "paid")
    pending_amt = sum(i["amount"] for i in invoices if i["status"] != "paid")
    overdue_n   = len([i for i in invoices if i["status"] == "overdue"])

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Invoices", total)
    with c2: st.metric("Collected",      f"₹{paid_amt/1000:.1f}K")
    with c3: st.metric("Outstanding",    f"₹{pending_amt/1000:.1f}K")
    with c4: st.metric("Overdue",        overdue_n)

    st.markdown("<div class='ap-divider'></div>", unsafe_allow_html=True)

    # Quick Actions
    st.markdown("<p style='font-size:11px;font-weight:600;color:#9CA3AF;letter-spacing:1px;margin-bottom:10px;'>QUICK ACTIONS</p>", unsafe_allow_html=True)
    q1,q2,q3,q4,q5,q6 = st.columns(6)
    for col, pid, icon, label in [
        (q1,"invoice","📄","Invoice"),(q2,"estimate","📋","Estimate"),
        (q3,"credit","💳","Credit Note"),(q4,"delivery","🚚","Delivery"),
        (q5,"purchase","🛒","Purchase"),(q6,"cashflow","📊","Cash Flow"),
    ]:
        with col:
            if st.button(f"{icon}\n\n{label}", key=f"qa_{pid}", use_container_width=True):
                nav(pid)

    st.markdown("<div class='ap-divider'></div>", unsafe_allow_html=True)

    # Pending + Summary
    left, right = st.columns([2, 1])

    with left:
        st.markdown("<p style='font-size:14px;font-weight:600;color:#111827;margin-bottom:10px;'>Unpaid Invoices</p>", unsafe_allow_html=True)
        pending = [i for i in invoices if i["status"] != "paid"]
        if not pending:
            st.markdown('<div class="ap-card" style="text-align:center;padding:28px;color:#9CA3AF;">✅ All invoices are paid!</div>', unsafe_allow_html=True)
        else:
            for inv in pending[:5]:
                is_overdue = inv["status"] == "overdue"
                badge_map  = {"overdue":("#FEE2E2","#991B1B"),"sent":("#DBEAFE","#1E40AF"),"draft":("#F3F4F6","#6B7280"),"read":("#FEF9C3","#854D0E")}
                bg, fg = badge_map.get(inv["status"], ("#F3F4F6","#6B7280"))
                overdue_dot = '<span style="font-size:11px;color:#EF4444;font-weight:600;">● Overdue</span>' if is_overdue else ""
                cl, cr = st.columns([3,1])
                with cl:
                    st.markdown(f"""
                    <div class="ap-card" style="margin-bottom:6px;">
                      <div style="font-weight:600;font-size:14px;color:#111827;">{inv['customer']}</div>
                      <div style="font-size:12px;color:#9CA3AF;margin-top:2px;">{inv['id']} &nbsp;•&nbsp; Due: {inv['due']}</div>
                      {overdue_dot}
                    </div>""", unsafe_allow_html=True)
                with cr:
                    st.markdown(f"""
                    <div class="ap-card" style="margin-bottom:6px;text-align:right;">
                      <div style="font-weight:700;font-size:14px;color:#111827;">₹{inv['amount']:,.0f}</div>
                      <span style="background:{bg};color:{fg};padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;">{inv['status'].title()}</span>
                    </div>""", unsafe_allow_html=True)

        if st.button("View All Invoices →", key="home_view_all"):
            nav("invoice")

    with right:
        st.markdown("<p style='font-size:14px;font-weight:600;color:#111827;margin-bottom:10px;'>Summary</p>", unsafe_allow_html=True)
        statuses = {}
        for inv in invoices:
            statuses[inv["status"]] = statuses.get(inv["status"], 0) + 1
        status_colors = {"paid":"#166534","sent":"#1E40AF","overdue":"#991B1B","draft":"#6B7280","read":"#854D0E"}
        for status, count in statuses.items():
            color = status_colors.get(status, "#6B7280")
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;background:#fff;border:1px solid #E8EAED;
                        border-radius:10px;margin-bottom:6px;">
              <span style="font-size:13px;color:#374151;">{status.title()}</span>
              <span style="font-weight:700;font-size:13px;color:{color};">{count}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div class='ap-divider'></div>", unsafe_allow_html=True)
        cust_count  = len(st.session_state.customers)
        items_count = len(st.session_state.items_db)
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:6px;margin-bottom:12px;">
          <div style="display:flex;justify-content:space-between;padding:10px 14px;background:#EEF2FF;border-radius:10px;">
            <span style="font-size:13px;color:#374151;">👥 Customers</span>
            <span style="font-weight:700;font-size:13px;color:#4F46E5;">{cust_count}</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:10px 14px;background:#F0FDF4;border-radius:10px;">
            <span style="font-size:13px;color:#374151;">📦 Items</span>
            <span style="font-weight:700;font-size:13px;color:#166534;">{items_count}</span>
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("➕ New Customer", use_container_width=True, key="home_add_cust"):
            nav("customers")
        if st.button("➕ New Item", use_container_width=True, key="home_add_item"):
            nav("items")

# ── PAGE ROUTING ──────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    render_home()   # ← no import, no file name issue!
elif page in ["invoice","estimate","credit","delivery","purchase"]:
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
