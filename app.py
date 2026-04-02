import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date, timedelta
import base64, urllib.parse, json, os

st.set_page_config(page_title="AP Tech Care", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*,[class*="css"]{font-family:'Inter',sans-serif!important;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stSidebarCollapseButton"],[data-testid="collapsedControl"]{display:none!important;}
section[data-testid="stSidebar"]{min-width:215px!important;width:215px!important;transform:translateX(0)!important;visibility:visible!important;}
.block-container{padding:1.6rem 2rem 2rem!important;max-width:100%!important;}
.stApp{background:#F7F8FA!important;}
[data-testid="stSidebar"]{background:#fff!important;border-right:1px solid #E5E7EB!important;}
[data-testid="stSidebar"] *{color:#374151!important;}
[data-testid="stSidebar"] .stButton>button{background:transparent!important;border:none!important;color:#6B7280!important;text-align:left!important;width:100%!important;padding:8px 12px!important;border-radius:7px!important;font-size:13px!important;font-weight:500!important;margin-bottom:1px!important;}
[data-testid="stSidebar"] .stButton>button:hover{background:#F3F4F6!important;color:#111!important;}
.pt{font-size:20px;font-weight:700;color:#111827;margin:0 0 2px;}
.ps{font-size:12px;color:#9CA3AF;margin:0 0 14px;}
.div{border:none;border-top:1px solid #E5E7EB;margin:12px 0;}
.stButton>button[kind="primary"]{background:#4F46E5!important;color:#fff!important;border:none!important;border-radius:8px!important;font-weight:600!important;}
[data-testid="metric-container"]{background:#fff;border:1px solid #E5E7EB;border-radius:10px;padding:14px!important;}
[data-testid="metric-container"] label{font-size:11px!important;color:#9CA3AF!important;font-weight:500!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{font-size:20px!important;font-weight:700!important;color:#111!important;}
.stTabs [data-baseweb="tab-list"]{gap:0;background:transparent!important;border-bottom:1px solid #E5E7EB!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#9CA3AF!important;font-weight:500!important;font-size:13px!important;padding:7px 16px!important;border:none!important;border-radius:0!important;}
.stTabs [aria-selected="true"]{color:#4F46E5!important;border-bottom:2px solid #4F46E5!important;font-weight:600!important;}
.stTextInput input,.stTextArea textarea,.stDateInput input,.stNumberInput input{border:1px solid #E5E7EB!important;border-radius:7px!important;background:#fff!important;color:#111!important;font-size:13px!important;}
.stSelectbox>div>div{border:1px solid #E5E7EB!important;border-radius:7px!important;font-size:13px!important;}

/* ── MOBILE RESPONSIVE ── */
@media (max-width: 768px) {
  section[data-testid="stSidebar"]{min-width:0!important;width:0!important;transform:translateX(-215px)!important;}
  .block-container{padding:0.8rem 0.7rem 1.5rem!important;}
  [data-testid="metric-container"]{padding:10px 8px!important;}
  [data-testid="metric-container"] [data-testid="stMetricValue"]{font-size:15px!important;}
  .pt{font-size:16px!important;}
  /* Stack columns on mobile */
  [data-testid="column"]{min-width:100%!important;width:100%!important;}
  /* Smaller buttons */
  .stButton>button{font-size:11px!important;padding:5px 6px!important;}
  /* Invoice list wrap */
  .inv-row-wrap{flex-direction:column!important;}
  /* Tabs scroll */
  .stTabs [data-baseweb="tab-list"]{overflow-x:auto!important;flex-wrap:nowrap!important;}
  .stTabs [data-baseweb="tab"]{font-size:11px!important;padding:6px 10px!important;white-space:nowrap!important;}
}
@media (max-width: 480px) {
  .block-container{padding:0.5rem 0.4rem 1rem!important;}
  [data-testid="metric-container"] [data-testid="stMetricValue"]{font-size:13px!important;}
}
</style>"""

# ── SUPABASE ──────────────────────────────────────────────────────
SUPABASE_URL = "https://zibexeqgtajeaujjkwqe.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def get_sb():
    if SUPABASE_KEY:
        try:
            from supabase import create_client
            return create_client(SUPABASE_URL, SUPABASE_KEY)
        except:
            pass
    return None

# ── Save ALL app data to Supabase ─────────────────────────────────
def db_save_all():
    """Save invoices, customers, items_db, settings, transactions to Supabase."""
    try:
        sb = get_sb()
        if sb:
            payload = {
                "id": 1,
                "data": json.dumps({
                    "settings":     st.session_state.settings,
                    "invoices":     st.session_state.invoices,
                    "customers":    st.session_state.customers,
                    "items_db":     st.session_state.items_db,
                    "transactions": st.session_state.transactions,
                })
            }
            sb.table("ap_settings").upsert(payload).execute()
            return True
    except Exception as e:
        st.toast(f"Cloud save error: {e}", icon="⚠️")
    return False

def db_load_all():
    """Load all app data from Supabase."""
    try:
        sb = get_sb()
        if sb:
            res = sb.table("ap_settings").select("data").eq("id", 1).execute()
            if res.data and res.data[0]["data"]:
                d = res.data[0]["data"]
                return json.loads(d) if isinstance(d, str) else d
    except:
        pass
    return None

# ── helpers ───────────────────────────────────────────────────────
def nav(p):
    st.session_state.page = p
    st.session_state.selected_inv = None
    st.session_state.inv_action = None
    st.rerun()

def fd(d):
    try: return datetime.strptime(str(d), "%Y-%m-%d").strftime("%d/%m/%Y")
    except: return str(d) if d else ""

def inv_html(doc, s, doc_label="Invoice"):
    items = doc.get("items", [])
    sub = doc.get("subtotal", doc.get("amount", 0))
    tax = doc.get("tax", 0)
    total = doc.get("amount", sub + tax)
    lb = s.get("logo_b64", "")
    logo = f'<img src="data:image/png;base64,{lb}" style="max-height:80px;max-width:140px;object-fit:contain;">' if lb else ""
    rows = ""
    for it in items:
        rows += f"""<tr>
          <td style="padding:10px 12px;font-weight:600;border-bottom:1px solid #eee;">{it.get("name","")}</td>
          <td style="padding:10px 12px;text-align:center;border-bottom:1px solid #eee;">{it.get("qty",1)}</td>
          <td style="padding:10px 12px;text-align:right;border-bottom:1px solid #eee;">Rs.{it.get("price",0):,.2f}</td>
          <td style="padding:10px 12px;text-align:right;border-bottom:1px solid #eee;">Rs.{it.get("amount",0):,.2f}</td>
        </tr>"""
    if not rows:
        rows = f'<tr><td colspan="3" style="padding:12px;text-align:right;color:#777">Total</td><td style="padding:12px;text-align:right;font-weight:700">Rs.{total:,.2f}</td></tr>'
    tax_row = ""
    if tax > 0:
        tax_row = f'<tr><td style="padding:6px 12px;font-size:13px;color:#555;text-align:left;border-bottom:1px solid #eee;">Tax ({doc.get("tax_rate",0)}%)</td><td style="padding:6px 12px;font-size:13px;text-align:right;font-weight:600;border-bottom:1px solid #eee;">Rs.{tax:,.2f}</td></tr>'
    caddr = ""; cphone = ""
    for c in st.session_state.customers:
        if isinstance(c, dict) and c.get("name") == doc.get("customer"):
            caddr = c.get("address", ""); cphone = c.get("phone", ""); break
    a2 = s.get("company_address2", "")
    tagline = s.get("company_tagline", "Smart Tech Solutions")
    owner = s.get("owner_name", "")
    due_row = ""
    if doc.get("due"):
        due_row = f'<tr><td style="padding:3px 8px;color:#555">Due</td><td style="padding:3px 8px;font-weight:700;text-align:right">{fd(doc["due"])}</td></tr>'
    tots_rows = f'<tr><td style="padding:6px 12px;font-size:13px;color:#555;text-align:left;border-bottom:1px solid #eee;">Subtotal</td><td style="padding:6px 12px;font-size:13px;text-align:right;font-weight:600;border-bottom:1px solid #eee;">Rs.{sub:,.2f}</td></tr>'
    tots_rows += tax_row
    tots_rows += f'<tr><td style="padding:6px 12px;font-size:13px;color:#555;text-align:left;border-bottom:1px solid #eee;">Total</td><td style="padding:6px 12px;font-size:13px;text-align:right;font-weight:600;border-bottom:1px solid #eee;">Rs.{total:,.2f}</td></tr>'
    owner_line = f'<div class="co-owner">{owner}</div>' if owner else ""
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{doc["id"]}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#1a1a1a;padding:40px;background:#fff;}}
.wrap{{max-width:720px;margin:0 auto;}}
.hdr{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:28px;padding-bottom:20px;border-bottom:2px solid #e5e7eb;}}
.logo-box{{min-width:160px;}}
.co-right{{text-align:right;}}
.inv-title{{font-size:34px;font-weight:900;color:#1a1a1a;line-height:1;margin-bottom:8px;}}
.co-name{{font-size:16px;font-weight:800;color:#1a1a1a;margin-bottom:2px;}}
.co-tagline{{font-size:12px;font-weight:600;color:#4F46E5;margin-bottom:3px;letter-spacing:.3px;}}
.co-owner{{font-size:12px;font-weight:600;color:#374151;margin-bottom:3px;}}
.co-info{{font-size:12px;color:#555;line-height:1.7;}}
.mid{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:22px;padding:14px 16px;border:1px solid #e5e7eb;border-radius:4px;}}
.bill-to h4{{font-size:11px;font-weight:700;color:#555;text-transform:uppercase;letter-spacing:.8px;margin-bottom:5px;}}
.bill-to .cn{{font-size:15px;font-weight:700;}}
.bill-to .ci{{font-size:12px;color:#666;line-height:1.6;margin-top:2px;}}
.inv-meta table{{border-collapse:collapse;}}
.inv-meta td{{padding:3px 8px;font-size:13px;color:#555;}}
.inv-meta td:last-child{{font-weight:700;text-align:right;color:#1a1a1a;}}
table.items{{width:100%;border-collapse:collapse;margin-bottom:20px;}}
table.items thead tr{{background:#1a1a1a;color:#fff;}}
table.items thead th{{padding:10px 12px;text-align:left;font-size:12px;font-weight:600;letter-spacing:.3px;}}
table.items thead th:nth-child(2){{text-align:center;}}
table.items thead th:nth-child(3),table.items thead th:nth-child(4){{text-align:right;}}
table.items tbody tr:nth-child(even){{background:#fafafa;}}
.bot{{display:flex;justify-content:space-between;align-items:flex-start;gap:24px;margin-top:4px;}}
.pi{{flex:1;}}
.pi h4{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;color:#1a1a1a;}}
.pi p{{font-size:12px;color:#444;line-height:1.8;}}
.tots{{min-width:230px;}}
.tots table{{width:100%;border-collapse:collapse;border:1px solid #e5e7eb;}}
.amt-box{{border:1px solid #e5e7eb;border-top:none;padding:14px 12px;text-align:center;}}
.amt-label{{font-size:12px;color:#777;margin-bottom:4px;}}
.amt-val{{font-size:24px;font-weight:900;color:#1a1a1a;}}
.footer{{margin-top:32px;padding-top:12px;border-top:1px solid #e5e7eb;text-align:center;font-size:11px;color:#aaa;}}
@media print{{button{{display:none!important;}}body{{padding:20px;}}}}
</style></head><body><div class="wrap">
<div class="hdr">
  <div class="logo-box">{logo}</div>
  <div class="co-right">
    <div class="inv-title">{doc_label}</div>
    <div class="co-name">{s.get("company_name","AP Tech Care")}</div>
    <div class="co-tagline">{tagline}</div>
    {owner_line}
    <div class="co-info">
      {s.get("company_address1","")}<br>
      {(a2+"<br>") if a2 else ""}{s.get("company_phone","")}<br>
      {s.get("company_email","")}
    </div>
  </div>
</div>
<div class="mid">
  <div class="bill-to">
    <h4>Bill To</h4>
    <div class="cn">{doc["customer"]}</div>
    <div class="ci">{""+caddr if caddr else ""}{"<br>Ph: "+cphone if cphone else ""}</div>
  </div>
  <div class="inv-meta">
    <table>
      <tr><td>Invoice #</td><td>{doc["id"]}</td></tr>
      <tr><td>Date</td><td>{fd(doc["date"])}</td></tr>
      {due_row}
    </table>
  </div>
</div>
<table class="items">
  <thead><tr><th>Item</th><th>Quantity</th><th>Price</th><th>Amount</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
<div class="bot">
  <div class="pi">
    <h4>Payment Instructions</h4>
    <p>{s.get("payment_instructions","").replace(chr(10),"<br>")}</p>
  </div>
  <div class="tots">
    <table>{tots_rows}</table>
    <div class="amt-box">
      <div class="amt-label">Amount due</div>
      <div class="amt-val">Rs.{total:,.2f}</div>
    </div>
  </div>
</div>
<div class="footer">Generated by AP Tech Care Invoice App</div>
</div></body></html>"""

# ── session init ──────────────────────────────────────────────────
def init():
    D = {
        "page": "home", "selected_inv": None, "inv_action": None,
        "show_new_inv": False, "new_inv_type": "invoice", "n_rows": 1,
        "show_add_cust": False, "edit_cust_idx": None,
        "show_add_item": False, "edit_item_idx": None,
        "invoices": [], "customers": [],
        "items_db": [
            {"name": "General Service",  "code": "GS001",  "price": 500,  "unit": "per visit"},
            {"name": "AMC Service",      "code": "AMC001", "price": 5000, "unit": "per year"},
            {"name": "Hardware Repair",  "code": "HW002",  "price": 1500, "unit": "per unit"},
            {"name": "Software Install", "code": "SW003",  "price": 800,  "unit": "per device"},
            {"name": "Network Setup",    "code": "NW004",  "price": 3500, "unit": "per job"},
        ],
        "settings": {
            "company_name": "AP Tech Care",
            "company_email": "aptechcare.chennai@gmail.com",
            "company_phone": "9940147658",
            "company_address1": "1/4A, Kamaraj Cross Street, Ambal Nagar, Ramapuram,",
            "company_address2": "Chennai, Tamilnadu 600 089",
            "company_tagline": "Smart Tech Solutions",
            "owner_name": "T.Arunprasad, BE., MBA.,",
            "gst_no": "", "currency": "INR", "date_format": "DD/MM/YYYY", "tax_rate": 0,
            "logo_b64": None, "next_invoice_no": 1001,
            "accounts": ["Cash", "UPI / GPay", "Bank Transfer"],
            "payment_instructions": "Bank: SBI, A/c no: 20001142967\nIFSC: SBIN0018229\nName: T.ArunPrasad, BE., MBA.\nGpay No: 9940147658",
        },
        "transactions": [],
        "data_loaded": False,   # ← renamed from settings_loaded
    }
    for k, v in D.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Patch missing settings keys
    for sk, sv in D["settings"].items():
        if sk not in st.session_state.settings:
            st.session_state.settings[sk] = sv

    # Normalize customers
    st.session_state.customers = [
        {"name": c, "email": "", "phone": "", "address": ""} if isinstance(c, str) else c
        for c in st.session_state.customers
    ]

    # ── Load ALL data from Supabase (only once per session) ──────
    if not st.session_state.data_loaded:
        loaded = db_load_all()
        if loaded:
            # Settings
            if "settings" in loaded:
                for k, v in loaded["settings"].items():
                    st.session_state.settings[k] = v
            # Invoices
            if "invoices" in loaded and loaded["invoices"]:
                st.session_state.invoices = loaded["invoices"]
            # Customers
            if "customers" in loaded and loaded["customers"]:
                raw = loaded["customers"]
                st.session_state.customers = [
                    {"name": c, "email": "", "phone": "", "address": ""} if isinstance(c, str) else c
                    for c in raw
                ]
            # Items
            if "items_db" in loaded and loaded["items_db"]:
                st.session_state.items_db = loaded["items_db"]
            # Transactions
            if "transactions" in loaded and loaded["transactions"]:
                st.session_state.transactions = loaded["transactions"]
            st.toast("☁️ Data loaded from cloud!", icon="✅")
        st.session_state.data_loaded = True

init()
st.markdown(CSS, unsafe_allow_html=True)

DOC_CFG = {
    "invoice":  {"label": "Invoices",        "icon": "📄", "prefix": "AP", "doc_label": "Invoice",       "tab_label": "Invoice"},
    "purchase": {"label": "Purchase Orders", "icon": "🛒", "prefix": "PO", "doc_label": "Purchase Order","tab_label": "Purchase"},
}

# ── sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    s = st.session_state.settings
    lb = s.get("logo_b64")
    if lb:
        st.markdown(f'<div style="padding:16px 14px 8px;text-align:center"><img src="data:image/png;base64,{lb}" style="max-width:150px;max-height:70px;object-fit:contain;border-radius:8px;"></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="padding:4px 14px 14px;text-align:center"><div style="font-weight:700;font-size:13px;color:#111">{s.get("company_name","AP Tech Care")}</div><div style="font-size:10px;color:#9CA3AF">Smart Tech Solutions</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="padding:18px 14px 14px"><div style="display:flex;align-items:center;gap:9px;margin-bottom:18px"><div style="width:34px;height:34px;border-radius:8px;background:#4F46E5;display:flex;align-items:center;justify-content:center;flex-shrink:0"><span style="color:#fff;font-weight:800;font-size:11px">AP</span></div><div><div style="font-weight:700;font-size:13px;color:#111">{s.get("company_name","AP Tech Care")}</div><div style="font-size:10px;color:#9CA3AF">Smart Tech Solutions</div></div></div></div>', unsafe_allow_html=True)

    cur = st.session_state.page
    st.markdown(f'<style>[data-testid="stSidebar"] [data-testid="stButton-sb_{cur}"]>button{{background:#EEF2FF!important;color:#4F46E5!important;font-weight:600!important;}}</style>', unsafe_allow_html=True)

    st.markdown('<div style="padding:0 10px;margin-bottom:3px;font-size:10px;font-weight:600;color:#9CA3AF;letter-spacing:1px">DOCUMENTS</div>', unsafe_allow_html=True)
    for pid, icon, lbl in [("home","🏠","Home"), ("invoice","📄","Invoice"), ("purchase","🛒","Purchase Orders")]:
        if st.button(f"{icon}  {lbl}", key=f"sb_{pid}", use_container_width=True): nav(pid)

    st.markdown('<div style="padding:0 10px;margin:10px 0 3px;font-size:10px;font-weight:600;color:#9CA3AF;letter-spacing:1px">MANAGE</div>', unsafe_allow_html=True)
    for pid, icon, lbl in [("cashflow","📊","Cash Flow"), ("reports","📈","Reports"),
                             ("items","📦","Items"), ("customers","👥","Customers"), ("settings","⚙️","Settings")]:
        if st.button(f"{icon}  {lbl}", key=f"sb_{pid}", use_container_width=True): nav(pid)

    st.markdown("---")
    if st.button("🚪  Logout", key="sb_logout", use_container_width=True): st.rerun()

if st.session_state.page not in ("home",):
    if st.button("← Home", key="gb"): nav("home")
    st.markdown("<div class='div'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════
def page_home():
    invs = st.session_state.invoices
    st.markdown('<p class="pt">Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="ps">AP Tech Care — Smart Tech Solutions</p>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    paid = sum(i["amount"] for i in invs if i["status"]=="paid")
    pend = sum(i["amount"] for i in invs if i["status"] not in ["paid","cancelled"])
    ovd  = len([i for i in invs if i["status"]=="overdue"])
    with c1: st.metric("Total Invoices", len(invs))
    with c2: st.metric("Collected", f"Rs.{paid:,.0f}")
    with c3: st.metric("Outstanding", f"Rs.{pend:,.0f}")
    with c4: st.metric("Overdue", ovd)
    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    st.markdown('<p style="font-size:11px;font-weight:600;color:#9CA3AF;letter-spacing:1px;margin-bottom:8px">QUICK ACTIONS</p>', unsafe_allow_html=True)
    qa = st.columns(3)
    for col,(pid,icon,lbl) in zip(qa,[("invoice","📄","New Invoice"),("purchase","🛒","Purchase Order"),("cashflow","📊","Cash Flow")]):
        with col:
            if st.button(f"{icon}  {lbl}", key=f"qa_{pid}", use_container_width=True):
                if pid in DOC_CFG:
                    st.session_state.show_new_inv = True
                    st.session_state.new_inv_type = pid
                nav(pid)
    st.markdown("<div class='div'></div>", unsafe_allow_html=True)
    left, right = st.columns([2,1])
    with left:
        st.markdown('<p style="font-size:13px;font-weight:600;color:#111;margin-bottom:8px">Unpaid Invoices</p>', unsafe_allow_html=True)
        pending = [i for i in invs if i["status"] not in ["paid","cancelled"]]
        if not pending:
            st.success("All invoices paid!")
        else:
            bm = {"overdue":("#FEE2E2","#991B1B"),"sent":("#DBEAFE","#1E40AF"),"draft":("#F3F4F6","#6B7280"),"read":("#FEF9C3","#854D0E")}
            for inv in pending[:6]:
                bg,fg = bm.get(inv["status"],("#F3F4F6","#6B7280"))
                od = '<span style="font-size:10px;color:#EF4444;font-weight:600"> Overdue</span>' if inv["status"]=="overdue" else ""
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:11px 14px;background:#fff;border:1px solid #E5E7EB;border-radius:9px;margin-bottom:5px"><div><div style="font-weight:600;font-size:13px">{inv["customer"]}</div><div style="font-size:11px;color:#9CA3AF">{inv["id"]} Due {fd(inv["due"])}{od}</div></div><div style="text-align:right"><div style="font-weight:700;font-size:13px">Rs.{inv["amount"]:,.0f}</div><span style="background:{bg};color:{fg};padding:1px 8px;border-radius:20px;font-size:11px;font-weight:600">{inv["status"].title()}</span></div></div>', unsafe_allow_html=True)
        if st.button("View All Invoices", key="h_all", use_container_width=True): nav("invoice")
    with right:
        st.markdown('<p style="font-size:13px;font-weight:600;color:#111;margin-bottom:8px">Summary</p>', unsafe_allow_html=True)
        sc = {"paid":"#166534","sent":"#1E40AF","overdue":"#991B1B","draft":"#6B7280","cancelled":"#991B1B","read":"#854D0E"}
        sts = {}
        for i in invs: sts[i["status"]] = sts.get(i["status"],0)+1
        for st2,cnt in sts.items():
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:7px 12px;background:#fff;border:1px solid #E5E7EB;border-radius:8px;margin-bottom:4px"><span style="font-size:13px">{st2.title()}</span><span style="font-weight:700;color:{sc.get(st2,"#6B7280")}">{cnt}</span></div>', unsafe_allow_html=True)
        st.markdown("<div class='div'></div>", unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:8px 12px;background:#EEF2FF;border-radius:8px;margin-bottom:4px"><span style="font-size:13px">Customers</span><span style="font-weight:700;color:#4F46E5">{len(st.session_state.customers)}</span></div><div style="display:flex;justify-content:space-between;padding:8px 12px;background:#F0FDF4;border-radius:8px"><span style="font-size:13px">Items</span><span style="font-weight:700;color:#166534">{len(st.session_state.items_db)}</span></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# DOCUMENTS
# ══════════════════════════════════════════════════════════════════
def page_documents(dtype):
    cfg = DOC_CFG[dtype]
    s = st.session_state.settings
    all_invs = st.session_state.invoices
    docs = [i for i in all_invs if i.get("type")==dtype]

    if st.session_state.get("selected_inv") and st.session_state.get("selected_inv",{}).get("type")==dtype:
        doc = st.session_state.selected_inv
        action = st.session_state.get("inv_action","preview")
        bm = {"paid":("#DCFCE7","#166534"),"overdue":("#FEE2E2","#991B1B"),"sent":("#DBEAFE","#1E40AF"),"draft":("#F3F4F6","#6B7280"),"read":("#FEF9C3","#854D0E"),"cancelled":("#FEE2E2","#991B1B")}
        bg,fg = bm.get(doc["status"],("#F3F4F6","#6B7280"))
        sub = doc.get("subtotal",doc.get("amount",0)); tax = doc.get("tax",0); total = doc.get("amount",sub+tax)
        hc1,hc2,hc3 = st.columns([1,3,2])
        with hc1:
            if st.button("Back",key="inv_back",use_container_width=True):
                st.session_state.selected_inv=None; st.session_state.inv_action=None; st.rerun()
        with hc3:
            st.markdown(f'<div style="text-align:right;padding-top:5px"><b>{doc["id"]}</b> <span style="background:{bg};color:{fg};padding:2px 10px;border-radius:20px;font-size:12px;font-weight:600">{doc["status"].title()}</span></div>', unsafe_allow_html=True)
        a1,a2,a3,a4,a5 = st.columns(5)
        with a1:
            if st.button("Preview",key="ap",use_container_width=True,type="primary" if action=="preview" else "secondary"):
                st.session_state.inv_action="preview"; st.rerun()
        with a2:
            if st.button("Edit",key="aedit",use_container_width=True,type="primary" if action=="edit" else "secondary"):
                st.session_state.inv_action="edit"; st.rerun()
        with a3:
            if st.button("Send",key="as",use_container_width=True,type="primary" if action=="send" else "secondary"):
                st.session_state.inv_action="send"; st.rerun()
        with a4:
            if st.button("Payment",key="apay",use_container_width=True,type="primary" if action=="pay" else "secondary"):
                st.session_state.inv_action="pay"; st.rerun()
        with a5:
            if st.button("Cancel",key="acan",use_container_width=True):
                st.session_state.inv_action="cancel"; st.rerun()
        st.markdown("<div class='div'></div>", unsafe_allow_html=True)
        html = inv_html(doc,s,cfg["doc_label"])

        if action=="preview":
            components.html(html, height=900, scrolling=True)

        elif action=="edit":
            st.markdown(f"### Edit {cfg['doc_label']} — {doc['id']}")
            cust_names = [c["name"] if isinstance(c,dict) else c for c in st.session_state.customers]
            cust_map   = {c["name"]:c for c in st.session_state.customers if isinstance(c,dict)}
            inames     = [i["name"] for i in st.session_state.items_db]
            iprices    = {i["name"]:i["price"] for i in st.session_state.items_db}
            ek_name  = f"edit_cname_{doc['id']}"; ek_phone = f"edit_cph_{doc['id']}"
            ek_addr  = f"edit_cad_{doc['id']}";   ek_email = f"edit_cem_{doc['id']}"
            if ek_name not in st.session_state: st.session_state[ek_name]=doc.get("customer","")
            if ek_phone not in st.session_state:
                c2=cust_map.get(doc.get("customer",""),{}); st.session_state[ek_phone]=c2.get("phone","")
            if ek_addr not in st.session_state:
                c2=cust_map.get(doc.get("customer",""),{}); st.session_state[ek_addr]=c2.get("address","")
            if ek_email not in st.session_state:
                c2=cust_map.get(doc.get("customer",""),{}); st.session_state[ek_email]=c2.get("email","")
            etyped = st.text_input("Customer",value=st.session_state[ek_name],label_visibility="collapsed",key=f"ectype_{doc['id']}")
            if etyped!=st.session_state[ek_name]:
                st.session_state[ek_name]=etyped
                if etyped in cust_map:
                    c2=cust_map[etyped]; st.session_state[ek_phone]=c2.get("phone",""); st.session_state[ek_addr]=c2.get("address",""); st.session_state[ek_email]=c2.get("email","")
                st.rerun()
            ed1,ed2,ed3 = st.columns(3)
            with ed1:
                eph=st.text_input("Phone",value=st.session_state[ek_phone],key=f"ephf_{doc['id']}")
                if eph!=st.session_state[ek_phone]: st.session_state[ek_phone]=eph
            with ed2:
                ead=st.text_input("Address",value=st.session_state[ek_addr],key=f"eadf_{doc['id']}")
                if ead!=st.session_state[ek_addr]: st.session_state[ek_addr]=ead
            with ed3:
                eem=st.text_input("Email",value=st.session_state[ek_email],key=f"eemf_{doc['id']}")
                if eem!=st.session_state[ek_email]: st.session_state[ek_email]=eem
            with st.form(f"detail_edit_{doc['id']}"):
                ef1,ef2,ef3 = st.columns(3)
                with ef1: e_invno=st.text_input("Invoice No",value=doc["id"])
                with ef2: e_date=st.date_input("Date",value=datetime.strptime(doc["date"],"%Y-%m-%d").date())
                with ef3: e_due=st.date_input("Due Date",value=datetime.strptime(doc["due"],"%Y-%m-%d").date() if doc.get("due") else date.today())
                ef4,ef5 = st.columns(2)
                with ef4:
                    stat_opts=["draft","sent","paid","overdue","cancelled"]
                    e_status=st.selectbox("Status",stat_opts,index=stat_opts.index(doc["status"]) if doc["status"] in stat_opts else 0)
                with ef5: e_tax=st.number_input("Tax %",min_value=0.0,max_value=100.0,value=float(doc.get("tax_rate",0)),step=0.5)
                st.markdown("**Items**")
                existing_items = doc.get("items",[]) or []
                n_er = st.session_state.get(f"n_edit_detail_{doc['id']}",max(1,len(existing_items)))
                edit_line_items=[]
                for i in range(n_er):
                    er1,er2,er3,er4 = st.columns([3,1,1,1])
                    prev_name  = existing_items[i]["name"]  if i<len(existing_items) else "—"
                    prev_qty   = existing_items[i]["qty"]   if i<len(existing_items) else 1
                    prev_price = existing_items[i]["price"] if i<len(existing_items) else 0
                    item_opts  = ["—"]+inames; pidx=item_opts.index(prev_name) if prev_name in item_opts else 0
                    with er1: e_iname=st.selectbox(f"Item {i+1}",item_opts,index=pidx,key=f"dein_{doc['id']}_{i}")
                    with er2: e_qty=st.number_input("Qty",min_value=1,value=int(prev_qty),key=f"deq_{doc['id']}_{i}")
                    with er3:
                        dp=iprices.get(e_iname,0) if e_iname!="—" else int(prev_price)
                        e_price=st.number_input("Price",min_value=0,value=int(dp),key=f"dep_{doc['id']}_{i}")
                    with er4: st.markdown(f"<div style='padding-top:26px;font-weight:700;color:#4F46E5'>Rs.{e_qty*e_price:,}</div>",unsafe_allow_html=True)
                    if e_iname!="—": edit_line_items.append({"name":e_iname,"qty":e_qty,"price":e_price,"amount":e_qty*e_price})
                e_sub=sum(x["amount"] for x in edit_line_items); e_tax_amt=int(e_sub*e_tax/100); e_total=e_sub+e_tax_amt
                st.markdown(f'<div style="background:#f8f9fa;border-radius:8px;padding:9px 14px;margin:8px 0;text-align:right"><b style="color:#4F46E5">Total: Rs.{e_total:,}</b></div>',unsafe_allow_html=True)
                sb1,sb2,sb3 = st.columns([2,1,1])
                with sb1: do_esave=st.form_submit_button("Save Changes",type="primary",use_container_width=True)
                with sb2: do_erow=st.form_submit_button("+ Row",use_container_width=True)
                with sb3: do_ecanc=st.form_submit_button("Cancel",use_container_width=True)
                if do_esave:
                    ec=st.session_state.get(ek_name,"").strip() or doc["customer"]
                    ph2=st.session_state.get(ek_phone,""); ad2=st.session_state.get(ek_addr,""); em2=st.session_state.get(ek_email,"")
                    found=False
                    for ci,cc in enumerate(st.session_state.customers):
                        if (cc["name"] if isinstance(cc,dict) else cc)==ec:
                            st.session_state.customers[ci]={"name":ec,"email":em2,"phone":ph2,"address":ad2}; found=True; break
                    if not found and ec: st.session_state.customers.append({"name":ec,"email":em2,"phone":ph2,"address":ad2})
                    old_id=doc["id"]
                    for idx,inv in enumerate(st.session_state.invoices):
                        if inv["id"]==old_id:
                            st.session_state.invoices[idx].update({"id":e_invno,"customer":ec,"date":str(e_date),"due":str(e_due),"status":e_status,"items":edit_line_items,"subtotal":e_sub,"tax":e_tax_amt,"tax_rate":e_tax,"amount":e_total}); break
                    updated={**doc,"id":e_invno,"customer":ec,"date":str(e_date),"due":str(e_due),"status":e_status,"items":edit_line_items,"subtotal":e_sub,"tax":e_tax_amt,"tax_rate":e_tax,"amount":e_total}
                    st.session_state.selected_inv=updated
                    for k in [ek_name,ek_phone,ek_addr,ek_email,f"n_edit_detail_{doc['id']}"]: st.session_state.pop(k,None)
                    db_save_all()   # ← SAVE after edit
                    st.session_state.inv_action="preview"; st.success("Updated & saved!"); st.rerun()
                if do_erow: st.session_state[f"n_edit_detail_{doc['id']}"]=n_er+1; st.rerun()
                if do_ecanc:
                    for k in [ek_name,ek_phone,ek_addr,ek_email]: st.session_state.pop(k,None)
                    st.session_state.inv_action="preview"; st.rerun()

        elif action=="send":
            st.markdown(f"### Send {cfg['doc_label']}")
            st.download_button(f"Download {doc['id']} (HTML)",data=html.encode(),file_name=f"{doc['id']}_{doc['customer'].replace(' ','_')}.html",mime="text/html",type="primary",use_container_width=True)
            st.markdown("---")
            phone=""
            for c in st.session_state.customers:
                if isinstance(c,dict) and c.get("name")==doc.get("customer"): phone=c.get("phone","").strip(); break
            phone_wa=("91"+phone if phone and len(phone)==10 else phone.replace("+",""))
            msg=f"Dear {doc['customer']},\n\nYour {cfg['doc_label']} *{doc['id']}* — *Rs.{total:,.2f}*\nDate: {fd(doc['date'])}\n\n{s.get('payment_instructions','')}\n\nThank you!\n— {s.get('company_name','AP Tech Care')}"
            wa=f"https://wa.me/{phone_wa}?text={urllib.parse.quote(msg)}" if phone_wa else f"https://wa.me/?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{wa}" target="_blank"><button style="width:100%;padding:11px;background:#25D366;color:#fff;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;margin-top:6px">Send on WhatsApp</button></a>',unsafe_allow_html=True)

        elif action=="pay":
            st.markdown("### Record Payment")
            if doc["status"]=="paid":
                st.success(f"Already paid — {doc.get('pay_method','')} on {fd(doc.get('paid_date',''))}")
            else:
                with st.form("pf"):
                    pc1,pc2 = st.columns(2)
                    with pc1: pd2=st.date_input("Payment Date",value=date.today())
                    with pc2: pm=st.selectbox("Method",["Cash","UPI / GPay","Bank Transfer","Cheque","Other"])
                    ps1,ps2 = st.columns(2)
                    with ps1: ok=st.form_submit_button("Mark Paid",type="primary",use_container_width=True)
                    with ps2: bk=st.form_submit_button("Cancel",use_container_width=True)
                    if ok:
                        for idx,inv in enumerate(st.session_state.invoices):
                            if inv["id"]==doc["id"]:
                                st.session_state.invoices[idx].update({"status":"paid","paid_date":str(pd2),"pay_method":pm})
                                st.session_state.selected_inv=st.session_state.invoices[idx]; break
                        db_save_all()   # ← SAVE after payment
                        st.success("Marked as Paid & saved!"); st.session_state.inv_action="preview"; st.rerun()
                    if bk: st.session_state.inv_action="preview"; st.rerun()

        elif action=="cancel":
            st.warning(f"Cancel **{doc['id']}** for **{doc['customer']}**?")
            cc1,cc2 = st.columns(2)
            with cc1:
                if st.button("Yes, Cancel",type="primary",use_container_width=True):
                    for idx,inv in enumerate(st.session_state.invoices):
                        if inv["id"]==doc["id"]: st.session_state.invoices[idx]["status"]="cancelled"; break
                    db_save_all()   # ← SAVE after cancel
                    st.session_state.selected_inv=None; st.session_state.inv_action=None; st.rerun()
            with cc2:
                if st.button("Go Back",use_container_width=True): st.session_state.inv_action="preview"; st.rerun()
        return

    hc1,hc2 = st.columns([3,1])
    with hc1:
        st.markdown(f'<p class="pt">{cfg["icon"]} {cfg["label"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="ps">{len(docs)} total</p>', unsafe_allow_html=True)
    with hc2:
        if st.button("+ New",type="primary",use_container_width=True,key=f"new_btn_{dtype}"):
            st.session_state.show_new_inv=True; st.session_state.new_inv_type=dtype
            st.session_state.n_rows=1; st.session_state.selected_inv=None; st.rerun()

    if st.session_state.get("show_new_inv") and st.session_state.get("new_inv_type")==dtype:
        st.markdown("---")
        cust_names = [c["name"] if isinstance(c,dict) else c for c in st.session_state.customers]
        cust_map   = {c["name"]:c for c in st.session_state.customers if isinstance(c,dict)}
        inames     = [i["name"] for i in st.session_state.items_db]
        iprices    = {i["name"]:i["price"] for i in st.session_state.items_db}
        st.markdown(f"**New {cfg['doc_label']}**")
        ck_name=f"nc_name_{dtype}"; ck_phone=f"nc_phone_{dtype}"; ck_addr=f"nc_addr_{dtype}"; ck_email=f"nc_email_{dtype}"
        for k in [ck_name,ck_phone,ck_addr,ck_email]:
            if k not in st.session_state: st.session_state[k]=""
        typed=st.text_input("Customer name",value=st.session_state[ck_name],placeholder="Type to search...",label_visibility="collapsed",key=f"ctype_{dtype}")
        if typed!=st.session_state[ck_name]:
            st.session_state[ck_name]=typed
            if typed in cust_map:
                c=cust_map[typed]; st.session_state[ck_phone]=c.get("phone",""); st.session_state[ck_addr]=c.get("address",""); st.session_state[ck_email]=c.get("email","")
            else:
                st.session_state[ck_phone]=""; st.session_state[ck_addr]=""; st.session_state[ck_email]=""
            st.rerun()
        if typed and typed not in cust_map:
            matches=[n for n in cust_names if typed.lower() in n.lower()]
            if matches:
                scols=st.columns(min(len(matches),4))
                for i,m in enumerate(matches[:4]):
                    with scols[i]:
                        if st.button(f"{m}",key=f"sug_{dtype}_{i}",use_container_width=True):
                            c=cust_map.get(m,{}); st.session_state[ck_name]=m; st.session_state[ck_phone]=c.get("phone",""); st.session_state[ck_addr]=c.get("address",""); st.session_state[ck_email]=c.get("email",""); st.rerun()
        cd1,cd2,cd3 = st.columns(3)
        with cd1:
            ph_val=st.text_input("Phone",value=st.session_state[ck_phone],key=f"cph_{dtype}")
            if ph_val!=st.session_state[ck_phone]: st.session_state[ck_phone]=ph_val
        with cd2:
            ad_val=st.text_input("Address",value=st.session_state[ck_addr],key=f"cad_{dtype}")
            if ad_val!=st.session_state[ck_addr]: st.session_state[ck_addr]=ad_val
        with cd3:
            em_val=st.text_input("Email",value=st.session_state[ck_email],key=f"cem_{dtype}")
            if em_val!=st.session_state[ck_email]: st.session_state[ck_email]=em_val
        with st.form(f"nif_{dtype}"):
            fc1,fc2 = st.columns(2)
            with fc1:
                n=s.get("next_invoice_no",1001)
                inv_no=st.text_input("Doc #",value=f"{cfg['prefix']}-{n}")
            with fc2: inv_date=st.date_input("Date",value=date.today())
            dc1,dc2,dc3 = st.columns(3)
            with dc1:
                due_toggle=st.toggle("Due Date",value=True)
                due_date=st.date_input("",value=date.today()+timedelta(days=15),label_visibility="collapsed") if due_toggle else None
            with dc2: inv_status=st.selectbox("Status",["draft","sent","paid"])
            with dc3: tax_rate=st.number_input("Tax %",min_value=0.0,max_value=100.0,value=float(s.get("tax_rate",0)),step=0.5)
            st.markdown("**Items**")
            n_rows=st.session_state.get("n_rows",1)
            line_items=[]
            for i in range(n_rows):
                r1,r2,r3,r4 = st.columns([3,1,1,1])
                with r1: iname=st.selectbox(f"Item {i+1}",["—"]+inames,key=f"in_{dtype}_{i}")
                with r2: qty=st.number_input("Qty",min_value=1,value=1,key=f"q_{dtype}_{i}")
                with r3:
                    dp=iprices.get(iname,0) if iname!="—" else 0
                    price=st.number_input("Price",min_value=0,value=dp,key=f"p_{dtype}_{i}")
                with r4: st.markdown(f"<div style='padding-top:26px;font-weight:700;color:#4F46E5'>Rs.{qty*price:,}</div>",unsafe_allow_html=True)
                if iname!="—": line_items.append({"name":iname,"qty":qty,"price":price,"amount":qty*price})
            sub=sum(x["amount"] for x in line_items); tax_amt=int(sub*tax_rate/100); total=sub+tax_amt
            st.markdown(f'<div style="background:#f8f9fa;border-radius:8px;padding:9px 14px;margin:8px 0;text-align:right"><b style="color:#4F46E5">Total: Rs.{total:,}</b></div>',unsafe_allow_html=True)
            bc1,bc2,bc3,bc4 = st.columns([2,1,1,1])
            with bc1: do_save=st.form_submit_button("Save",type="primary",use_container_width=True)
            with bc2: do_row=st.form_submit_button("+ Row",use_container_width=True)
            with bc3: do_prev=st.form_submit_button("Preview",use_container_width=True)
            with bc4: do_canc=st.form_submit_button("Cancel",use_container_width=True)
            actual_cust=st.session_state.get(ck_name,"").strip()
            new_doc={"id":inv_no,"type":dtype,"customer":actual_cust,"date":str(inv_date),"due":str(due_date) if due_date else "","amount":total,"status":inv_status,"items":line_items,"subtotal":sub,"tax":tax_amt,"tax_rate":tax_rate}
            if do_save and actual_cust:
                ph=st.session_state.get(ck_phone,""); ad=st.session_state.get(ck_addr,""); em=st.session_state.get(ck_email,"")
                if actual_cust not in [c["name"] if isinstance(c,dict) else c for c in st.session_state.customers]:
                    st.session_state.customers.append({"name":actual_cust,"email":em,"phone":ph,"address":ad})
                else:
                    for ci,cc in enumerate(st.session_state.customers):
                        if (cc["name"] if isinstance(cc,dict) else cc)==actual_cust:
                            st.session_state.customers[ci]={"name":actual_cust,"email":em,"phone":ph,"address":ad}; break
                st.session_state.invoices.insert(0,new_doc)
                s["next_invoice_no"]=s.get("next_invoice_no",1001)+1
                st.session_state.show_new_inv=False; st.session_state.n_rows=1
                for k in [ck_name,ck_phone,ck_addr,ck_email]: st.session_state.pop(k,None)
                db_save_all()   # ← SAVE after new invoice
                st.success(f"{inv_no} saved to cloud!"); st.rerun()
            if do_row: st.session_state.n_rows=n_rows+1; st.rerun()
            if do_prev and actual_cust:
                st.session_state.selected_inv=new_doc; st.session_state.inv_action="preview"; st.rerun()
            if do_canc:
                st.session_state.show_new_inv=False; st.session_state.n_rows=1
                for k in [ck_name,ck_phone,ck_addr,ck_email]: st.session_state.pop(k,None)
                st.rerun()

    tabs=st.tabs(["All","Draft","Sent","Paid","Overdue","Cancelled"])
    for tab,flt in zip(tabs,["all","draft","sent","paid","overdue","cancelled"]):
        with tab:
            fl=docs if flt=="all" else [d for d in docs if d["status"]==flt]
            srch=st.text_input("Search",placeholder=f"Search...",key=f"srch_{dtype}_{flt}",label_visibility="collapsed")
            if srch: fl=[d for d in fl if srch.lower() in d["customer"].lower() or srch.lower() in d["id"].lower()]
            if not fl:
                st.info(f"No {cfg['label'].lower()}")
            else:
                bm={"paid":("#DCFCE7","#166534"),"overdue":("#FEE2E2","#991B1B"),"sent":("#DBEAFE","#1E40AF"),"draft":("#F3F4F6","#6B7280"),"read":("#FEF9C3","#854D0E"),"cancelled":("#FEE2E2","#991B1B")}
                for doc in fl:
                    bg2,fg2=bm.get(doc["status"],("#F3F4F6","#6B7280"))
                    lc1,lc2,lc3,lc4,lc5,lc6,lc7=st.columns([3,1,1,1,1,1,1])
                    with lc1: st.markdown(f'<div style="padding:5px 0"><div style="font-weight:600;font-size:14px">{doc["customer"]}</div><div style="font-size:11px;color:#9CA3AF">{doc["id"]} {fd(doc["date"])}</div></div>',unsafe_allow_html=True)
                    with lc2: st.markdown(f'<div style="padding:5px 0;text-align:right"><div style="font-weight:700;font-size:13px">Rs.{doc["amount"]:,.0f}</div><span style="background:{bg2};color:{fg2};padding:1px 8px;border-radius:20px;font-size:11px;font-weight:600">{doc["status"].title()}</span></div>',unsafe_allow_html=True)
                    with lc3:
                        if st.button("View",key=f"v_{dtype}_{flt}_{doc['id']}",use_container_width=True):
                            st.session_state.selected_inv=doc; st.session_state.inv_action="preview"; st.rerun()
                    with lc4:
                        if st.button("Send",key=f"snd_{dtype}_{flt}_{doc['id']}",use_container_width=True):
                            st.session_state.selected_inv=doc; st.session_state.inv_action="send"; st.rerun()
                    with lc5:
                        if st.button("Pay",key=f"pay_{dtype}_{flt}_{doc['id']}",use_container_width=True):
                            st.session_state.selected_inv=doc; st.session_state.inv_action="pay"; st.rerun()
                    with lc6:
                        if st.button("Edit",key=f"edit_{dtype}_{flt}_{doc['id']}",use_container_width=True):
                            st.session_state.selected_inv=doc; st.session_state.inv_action="edit"; st.rerun()
                    with lc7:
                        if st.button("Del",key=f"del_{dtype}_{flt}_{doc['id']}",use_container_width=True):
                            st.session_state[f"confirm_del_{dtype}"]=doc["id"]; st.rerun()
                    if st.session_state.get(f"confirm_del_{dtype}")==doc["id"]:
                        st.warning(f"Delete {doc['id']} ({doc['customer']})?")
                        dc1,dc2=st.columns(2)
                        with dc1:
                            if st.button("Yes Delete",key=f"yes_del_{doc['id']}",type="primary",use_container_width=True):
                                st.session_state.invoices=[i for i in st.session_state.invoices if i["id"]!=doc["id"]]
                                db_save_all()   # ← SAVE after delete
                                st.session_state.pop(f"confirm_del_{dtype}",None); st.rerun()
                        with dc2:
                            if st.button("No",key=f"no_del_{doc['id']}",use_container_width=True):
                                st.session_state.pop(f"confirm_del_{dtype}",None); st.rerun()
                    st.markdown("<hr style='margin:3px 0;border-color:#F3F4F6'>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CASHFLOW
# ══════════════════════════════════════════════════════════════════
def page_cashflow():
    st.markdown('<p class="pt">Cash Flow</p>',unsafe_allow_html=True)
    invs=st.session_state.invoices
    t1,t2,t3=st.tabs(["Dashboard","Accounts","Transactions"])
    with t1:
        tin=sum(i["amount"] for i in invs if i["status"]=="paid")
        tout=sum(t["amount"] for t in st.session_state.transactions if t.get("type")=="Expense")
        net=tin-tout
        c1,c2,c3=st.columns(3)
        with c1: st.metric("Collected",f"Rs.{tin:,.0f}")
        with c2: st.metric("Expenses",f"Rs.{tout:,.0f}")
        with c3: st.metric("Net Balance",f"Rs.{net:,.0f}")
        st.markdown("---")
        for inv in [i for i in invs if i["status"]=="paid"][:5]:
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:10px 14px;background:#fff;border:1px solid #E5E7EB;border-radius:8px;margin-bottom:5px"><div><b>{inv["customer"]}</b><br><span style="font-size:11px;color:#9CA3AF">{inv["id"]} {fd(inv["date"])}</span></div><b style="color:#10B981">+Rs.{inv["amount"]:,.0f}</b></div>',unsafe_allow_html=True)
    with t2:
        for acc in st.session_state.settings.get("accounts",[]):
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:10px 14px;background:#fff;border:1px solid #E5E7EB;border-radius:8px;margin-bottom:5px"><span style="font-weight:600">{acc}</span><span style="font-weight:700;color:#4F46E5">Rs.0</span></div>',unsafe_allow_html=True)
    with t3:
        txns=st.session_state.transactions
        with st.form("tf"):
            tc1,tc2=st.columns(2)
            with tc1: ttype=st.selectbox("Type",["Income","Expense"]); tamt=st.number_input("Amount",min_value=0)
            with tc2: tdesc=st.text_input("Description"); tacct=st.selectbox("Account",st.session_state.settings.get("accounts",["Cash"]))
            if st.form_submit_button("Add Transaction",type="primary"):
                txns.append({"type":ttype,"amount":tamt,"desc":tdesc,"account":tacct})
                db_save_all()   # ← SAVE transactions
                st.rerun()
        for t in reversed(txns[-10:]):
            col2="#10B981" if t["type"]=="Income" else "#EF4444"; sgn="+" if t["type"]=="Income" else "-"
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:10px 14px;background:#fff;border:1px solid #E5E7EB;border-radius:8px;margin-bottom:5px"><div><b>{t["desc"]}</b><br><span style="font-size:11px;color:#9CA3AF">{t["account"]}</span></div><b style="color:{col2}">{sgn}Rs.{t["amount"]:,}</b></div>',unsafe_allow_html=True)
        if not txns: st.info("No transactions yet.")

# ══════════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════════
def page_reports():
    st.markdown('<p class="pt">Reports</p>',unsafe_allow_html=True)
    invs=st.session_state.invoices
    t1,t2=st.tabs(["Monthly","Summary"])
    with t1:
        months={}
        for inv in invs:
            try:
                m=datetime.strptime(inv["date"],"%Y-%m-%d").strftime("%b %Y")
                months.setdefault(m,{"total":0,"paid":0,"count":0})
                months[m]["total"]+=inv["amount"]; months[m]["count"]+=1
                if inv["status"]=="paid": months[m]["paid"]+=inv["amount"]
            except: pass
        if not months: st.info("No invoices yet.")
        for mo,d in months.items():
            st.markdown(f'<div style="background:#fff;border:1px solid #E5E7EB;border-radius:10px;padding:14px 16px;margin-bottom:8px"><b>{mo}</b><div style="display:flex;gap:24px;margin-top:8px"><div><span style="font-size:11px;color:#9CA3AF">Invoices</span><br><b>{d["count"]}</b></div><div><span style="font-size:11px;color:#9CA3AF">Total</span><br><b>Rs.{d["total"]:,}</b></div><div><span style="font-size:11px;color:#9CA3AF">Collected</span><br><b style="color:#10B981">Rs.{d["paid"]:,}</b></div><div><span style="font-size:11px;color:#9CA3AF">Pending</span><br><b style="color:#EF4444">Rs.{d["total"]-d["paid"]:,}</b></div></div></div>',unsafe_allow_html=True)
    with t2:
        tot=sum(i["amount"] for i in invs); col_amt=sum(i["amount"] for i in invs if i["status"]=="paid")
        c1,c2,c3=st.columns(3)
        with c1: st.metric("Total Billed",f"Rs.{tot:,}")
        with c2: st.metric("Collected",f"Rs.{col_amt:,}")
        with c3: st.metric("Outstanding",f"Rs.{tot-col_amt:,}")

# ══════════════════════════════════════════════════════════════════
# CUSTOMERS
# ══════════════════════════════════════════════════════════════════
def page_customers():
    custs=st.session_state.customers
    st.markdown('<p class="pt">Customers</p>',unsafe_allow_html=True)
    _,c2=st.columns([3,1])
    with c2:
        if st.button("+ Add",type="primary",use_container_width=True,key="cust_add_btn"):
            st.session_state.show_add_cust=True; st.session_state.edit_cust_idx=None
    srch=st.text_input("Search",placeholder="Search name or phone...",label_visibility="collapsed",key="csrch")
    fl=[c for c in custs if not srch or srch.lower() in c["name"].lower() or srch.lower() in c.get("phone","").lower()]
    for cust in fl:
        ri=custs.index(cust)
        cinvs=[i for i in st.session_state.invoices if i["customer"]==cust["name"]]
        cc1,cc2,cc3=st.columns([4,1,1])
        with cc1: st.markdown(f'<div style="padding:5px 0"><div style="font-weight:600;font-size:14px">{cust["name"]}</div><div style="font-size:11px;color:#9CA3AF">{cust.get("phone","—")} | {len(cinvs)} invoices | Rs.{sum(i["amount"] for i in cinvs):,}</div></div>',unsafe_allow_html=True)
        with cc2:
            if st.button("Edit",key=f"ec{ri}"): st.session_state.edit_cust_idx=ri; st.session_state.show_add_cust=False
        with cc3:
            if st.button("Del",key=f"dc{ri}"):
                custs.pop(ri)
                db_save_all()   # ← SAVE after delete customer
                st.rerun()
        st.markdown("<hr style='margin:3px 0;border-color:#F3F4F6'>",unsafe_allow_html=True)
    ei=st.session_state.get("edit_cust_idx")
    if ei is not None and ei<len(custs):
        c=custs[ei]; st.markdown("---")
        with st.form("ecf"):
            st.markdown(f"**Edit — {c['name']}**")
            fc1,fc2=st.columns(2)
            with fc1: en=st.text_input("Name *",value=c.get("name","")); ep=st.text_input("Phone",value=c.get("phone",""))
            with fc2: ee=st.text_input("Email",value=c.get("email","")); ea=st.text_input("Address",value=c.get("address",""))
            s1,s2=st.columns(2)
            with s1: esv=st.form_submit_button("Save",type="primary",use_container_width=True)
            with s2: ecl=st.form_submit_button("Close",use_container_width=True)
            if esv and en:
                custs[ei]={"name":en,"email":ee,"phone":ep,"address":ea}
                db_save_all()   # ← SAVE customer edit
                st.session_state.edit_cust_idx=None; st.success("Updated!"); st.rerun()
            if ecl: st.session_state.edit_cust_idx=None; st.rerun()
    if st.session_state.get("show_add_cust"):
        st.markdown("---")
        with st.form("acf"):
            st.markdown("**New Customer**")
            fc1,fc2=st.columns(2)
            with fc1: an=st.text_input("Name *"); ap2=st.text_input("Phone")
            with fc2: ae=st.text_input("Email"); aa=st.text_input("Address")
            s1,s2=st.columns(2)
            with s1: asv=st.form_submit_button("Save",type="primary",use_container_width=True)
            with s2: acl=st.form_submit_button("Close",use_container_width=True)
            if asv and an:
                custs.append({"name":an,"email":ae,"phone":ap2,"address":aa})
                db_save_all()   # ← SAVE new customer
                st.session_state.show_add_cust=False; st.success(f"'{an}' added!"); st.rerun()
            if acl: st.session_state.show_add_cust=False; st.rerun()

# ══════════════════════════════════════════════════════════════════
# ITEMS
# ══════════════════════════════════════════════════════════════════
def page_items():
    items=st.session_state.items_db
    st.markdown('<p class="pt">Items</p>',unsafe_allow_html=True)
    _,c2=st.columns([3,1])
    with c2:
        if st.button("+ Add",type="primary",use_container_width=True,key="item_add_btn"):
            st.session_state.show_add_item=True; st.session_state.edit_item_idx=None
    srch=st.text_input("Search",placeholder="Search items...",label_visibility="collapsed",key="isrch")
    fl=[i for i in items if not srch or srch.lower() in i["name"].lower()]
    for item in fl:
        ri=items.index(item)
        ic1,ic2,ic3,ic4=st.columns([3,1,1,1])
        with ic1: st.markdown(f'<div style="padding:5px 0"><div style="font-weight:600;font-size:14px">{item["name"]}</div><div style="font-size:11px;color:#9CA3AF">Code: {item.get("code","—")} | {item.get("unit","")}</div></div>',unsafe_allow_html=True)
        with ic2: st.markdown(f"<div style='padding-top:6px;font-weight:700;color:#166534'>Rs.{item['price']:,}</div>",unsafe_allow_html=True)
        with ic3:
            if st.button("Edit",key=f"ei{ri}"): st.session_state.edit_item_idx=ri; st.session_state.show_add_item=False
        with ic4:
            if st.button("Del",key=f"di{ri}"):
                items.pop(ri)
                db_save_all()   # ← SAVE after delete item
                st.rerun()
        st.markdown("<hr style='margin:3px 0;border-color:#F3F4F6'>",unsafe_allow_html=True)
    ei2=st.session_state.get("edit_item_idx")
    if ei2 is not None and ei2<len(items):
        it=items[ei2]; st.markdown("---")
        with st.form("eif"):
            st.markdown(f"**Edit — {it['name']}**")
            ic1,ic2=st.columns(2)
            with ic1: n=st.text_input("Name *",value=it.get("name","")); pr=st.number_input("Price",min_value=0,value=int(it.get("price",0)))
            with ic2: cd=st.text_input("Code",value=it.get("code","")); u=st.text_input("Unit",value=it.get("unit","per unit"))
            s1,s2=st.columns(2)
            with s1: isv=st.form_submit_button("Save",type="primary",use_container_width=True)
            with s2: icl=st.form_submit_button("Close",use_container_width=True)
            if isv and n:
                items[ei2]={"name":n,"code":cd,"price":pr,"unit":u,"desc":""}
                db_save_all()   # ← SAVE item edit
                st.session_state.edit_item_idx=None; st.success("Updated!"); st.rerun()
            if icl: st.session_state.edit_item_idx=None; st.rerun()
    if st.session_state.get("show_add_item"):
        st.markdown("---")
        with st.form("aif"):
            st.markdown("**New Item**")
            ic1,ic2=st.columns(2)
            with ic1: n=st.text_input("Item Name *"); pr=st.number_input("Price",min_value=0)
            with ic2: cd=st.text_input("Code"); u=st.text_input("Unit",value="per visit")
            s1,s2=st.columns(2)
            with s1: aIsv=st.form_submit_button("Save",type="primary",use_container_width=True)
            with s2: aIcl=st.form_submit_button("Close",use_container_width=True)
            if aIsv and n:
                items.append({"name":n,"code":cd,"price":pr,"unit":u,"desc":""})
                db_save_all()   # ← SAVE new item
                st.session_state.show_add_item=False; st.success(f"'{n}' added!"); st.rerun()
            if aIcl: st.session_state.show_add_item=False; st.rerun()

# ══════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════
def page_settings():
    st.markdown('<p class="pt">Settings</p>',unsafe_allow_html=True)
    s=st.session_state.settings

    if SUPABASE_KEY:
        st.success("☁️ Cloud save enabled — all data persists after refresh!")
    else:
        st.warning("⚠️ SUPABASE_KEY not set — data lost on refresh. Add it in Streamlit Cloud Secrets.")

    sec=st.radio("",["Company","Payment","Accounts","Tax & Currency"],horizontal=True,label_visibility="collapsed")
    st.markdown("---")

    if sec=="Company":
        lf=st.file_uploader("Upload Logo",type=["png","jpg","jpeg"])
        if lf:
            s["logo_b64"]=base64.b64encode(lf.read()).decode()
            db_save_all()
            st.success("Logo saved!"); st.rerun()
        if s.get("logo_b64"):
            st.markdown(f'<img src="data:image/png;base64,{s["logo_b64"]}" style="height:60px;border-radius:8px;margin-bottom:10px">',unsafe_allow_html=True)
            if st.button("Remove Logo"): s["logo_b64"]=None; db_save_all(); st.rerun()
        c1,c2=st.columns(2)
        with c1:
            sn   = st.text_input("Company Name",    value=s.get("company_name",""))
            stag = st.text_input("Tagline",          value=s.get("company_tagline","Smart Tech Solutions"))
            sown = st.text_input("Owner Name",       value=s.get("owner_name",""))
            sp   = st.text_input("Phone",            value=s.get("company_phone",""))
            sa1  = st.text_input("Address Line 1",   value=s.get("company_address1",""))
            sa2  = st.text_input("Address Line 2",   value=s.get("company_address2",""))
        with c2:
            se   = st.text_input("Email",            value=s.get("company_email",""))
            sg   = st.text_input("GST No",           value=s.get("gst_no",""))
        if st.button("Save Company Info",type="primary"):
            s.update({"company_name":sn,"company_tagline":stag,"owner_name":sown,
                      "company_phone":sp,"company_email":se,"gst_no":sg,
                      "company_address1":sa1,"company_address2":sa2})
            if db_save_all():
                st.success("Saved to cloud! Will persist after refresh.")
            else:
                st.warning("Saved locally. Add SUPABASE_KEY to persist.")
            st.rerun()

    elif sec=="Payment":
        ins=st.text_area("Payment Instructions",value=s.get("payment_instructions",""),height=120)
        if st.button("Save",type="primary"):
            s["payment_instructions"]=ins
            if db_save_all():
                st.success("Saved to cloud!")
            else:
                st.warning("Saved locally.")

    elif sec=="Accounts":
        accs=s.get("accounts",["Cash","UPI","Bank Transfer"])
        for i,a in enumerate(accs):
            rc1,rc2=st.columns([5,1])
            with rc1: st.markdown(f'<div style="padding:10px 14px;background:#f8f9fa;border:1px solid #E5E7EB;border-radius:7px;font-weight:600">{a}</div>',unsafe_allow_html=True)
            with rc2:
                if st.button("Del",key=f"da{i}"): accs.pop(i); s["accounts"]=accs; db_save_all(); st.rerun()
        na=st.text_input("New Account Name")
        if st.button("+ Add",type="primary"):
            if na: accs.append(na); s["accounts"]=accs; db_save_all(); st.rerun()

    elif sec=="Tax & Currency":
        c1,c2=st.columns(2)
        with c1: tr=st.number_input("Default Tax %",min_value=0.0,max_value=100.0,value=float(s.get("tax_rate",0)),step=0.5)
        with c2: df2=st.selectbox("Date Format",["DD/MM/YYYY","MM/DD/YYYY","YYYY/MM/DD"],index=["DD/MM/YYYY","MM/DD/YYYY","YYYY/MM/DD"].index(s.get("date_format","DD/MM/YYYY")))
        if st.button("Save",type="primary"):
            s.update({"tax_rate":tr,"date_format":df2})
            if db_save_all():
                st.success("Saved to cloud!")
            else:
                st.warning("Saved locally.")

# ══════════════════════════════════════════════════════════════════
# ROUTING
# ══════════════════════════════════════════════════════════════════
pg=st.session_state.page
if pg=="home":        page_home()
elif pg=="invoice":   page_documents("invoice")
elif pg=="purchase":  page_documents("purchase")
elif pg=="cashflow":  page_cashflow()
elif pg=="reports":   page_reports()
elif pg=="customers": page_customers()
elif pg=="items":     page_items()
elif pg=="settings":  page_settings()
