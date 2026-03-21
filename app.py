import streamlit as st
from datetime import datetime, date, timedelta
import base64
import urllib.parse

st.set_page_config(page_title="AP Tech Care", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

def get_theme_css():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"]        { display: none !important; }
section[data-testid="stSidebar"] { min-width:220px !important; width:220px !important; transform:translateX(0) !important; visibility:visible !important; }
.block-container { padding:2rem 2.5rem 2rem !important; max-width:100% !important; }
.stApp { background:#F5F6FA !important; }
[data-testid="stSidebar"] { background:#FFFFFF !important; border-right:1px solid #E8EAED !important; }
[data-testid="stSidebar"] * { color:#374151 !important; }
[data-testid="stSidebar"] .stButton > button { background:transparent !important; border:none !important; color:#6B7280 !important; text-align:left !important; width:100% !important; padding:9px 14px !important; border-radius:8px !important; font-size:13px !important; font-weight:500 !important; transition:all 0.15s !important; margin-bottom:2px !important; }
[data-testid="stSidebar"] .stButton > button:hover { background:#F3F4F6 !important; color:#111827 !important; }
.ap-card { background:#FFF; border:1px solid #E8EAED; border-radius:12px; padding:18px 20px; margin-bottom:10px; box-shadow:0 1px 2px rgba(0,0,0,0.04); transition:box-shadow 0.15s; }
.ap-card:hover { box-shadow:0 3px 8px rgba(0,0,0,0.08); }
.badge-paid    { background:#DCFCE7; color:#166534; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-overdue { background:#FEE2E2; color:#991B1B; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-sent    { background:#DBEAFE; color:#1E40AF; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-draft   { background:#F3F4F6; color:#6B7280; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-read    { background:#FEF9C3; color:#854D0E; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.badge-cancelled { background:#FEE2E2; color:#991B1B; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.page-title { font-size:22px; font-weight:700; color:#111827; margin:0 0 2px; }
.page-sub   { font-size:13px; color:#9CA3AF; margin:0 0 20px; }
.ap-divider { border:none; border-top:1px solid #E8EAED; margin:16px 0; }
.stButton > button[kind="primary"] { background:#4F46E5 !important; color:white !important; border:none !important; border-radius:8px !important; font-weight:600 !important; font-size:13px !important; }
[data-testid="metric-container"] { background:#FFF; border:1px solid #E8EAED; border-radius:12px; padding:16px !important; box-shadow:0 1px 2px rgba(0,0,0,0.04); }
[data-testid="metric-container"] label { font-size:12px !important; color:#9CA3AF !important; font-weight:500 !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size:22px !important; font-weight:700 !important; color:#111827 !important; }
.stTabs [data-baseweb="tab-list"] { gap:0; background:transparent !important; border-bottom:1px solid #E8EAED !important; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:#9CA3AF !important; font-weight:500 !important; font-size:13px !important; padding:8px 18px !important; border:none !important; border-radius:0 !important; }
.stTabs [aria-selected="true"] { color:#4F46E5 !important; border-bottom:2px solid #4F46E5 !important; font-weight:600 !important; }
.stTextInput input, .stTextArea textarea, .stDateInput input { border:1px solid #E8EAED !important; border-radius:8px !important; background:#FFF !important; color:#111827 !important; font-size:13px !important; }
.stSelectbox > div > div { border:1px solid #E8EAED !important; border-radius:8px !important; font-size:13px !important; }
</style>"""

def init_session():
    defaults = {
        "page":"home",
        "invoices":[
            {"id":"AP-1001","type":"invoice","customer":"TechSoft Pvt Ltd",   "date":"2025-06-01","due":"2025-06-15","amount":18500,"status":"paid",   "items":[],"subtotal":18500,"tax":0},
            {"id":"AP-1002","type":"invoice","customer":"InfoBridge Solutions","date":"2025-06-05","due":"2025-06-20","amount":32000,"status":"sent",   "items":[],"subtotal":32000,"tax":0},
            {"id":"AP-1003","type":"invoice","customer":"Nexus Digital",      "date":"2025-06-10","due":"2025-06-10","amount":7500, "status":"overdue","items":[],"subtotal":7500,"tax":0},
            {"id":"AP-1004","type":"invoice","customer":"CloudVerse Inc",     "date":"2025-06-12","due":"2025-06-26","amount":54000,"status":"draft",  "items":[],"subtotal":54000,"tax":0},
            {"id":"AP-1005","type":"invoice","customer":"ByteWave Tech",      "date":"2025-06-14","due":"2025-06-28","amount":12300,"status":"sent",   "items":[],"subtotal":12300,"tax":0},
        ],
        "customers":[
            {"name":"TechSoft Pvt Ltd",   "email":"techsoft@example.com", "phone":"9800001111","address":"Chennai"},
            {"name":"InfoBridge Solutions","email":"info@infobridge.com",  "phone":"9800002222","address":"Bangalore"},
            {"name":"Nexus Digital",      "email":"hello@nexusdigital.in","phone":"9800003333","address":"Hyderabad"},
            {"name":"CloudVerse Inc",     "email":"admin@cloudverse.io",  "phone":"9800004444","address":"Mumbai"},
            {"name":"ByteWave Tech",      "email":"support@bytewave.in",  "phone":"9800005555","address":"Pune"},
        ],
        "items_db":[
            {"name":"AMC Service",     "code":"AMC001","price":5000,"unit":"per year",  "desc":"Annual Maintenance Contract"},
            {"name":"Hardware Repair", "code":"HW002", "price":1500,"unit":"per unit",  "desc":"Hardware diagnosis and repair"},
            {"name":"Software Install","code":"SW003", "price":800, "unit":"per device","desc":"Software installation and setup"},
            {"name":"Network Setup",   "code":"NW004", "price":3500,"unit":"per job",   "desc":"Network configuration and setup"},
            {"name":"General Service", "code":"GS001", "price":500,  "unit":"per visit","desc":"General service visit"},
        ],
        "settings":{
            "company_name":"AP Tech Care","company_email":"aptechcare.chennai@gmail.com",
            "company_phone":"9940147658","company_address1":"1/4A, Kamaraj Cross Street,",
            "company_address2":"Ambal Nagar, Ramapuram, Chennai, Tamilnadu 600 089",
            "gst_no":"","currency":"INR","date_format":"DD/MM/YYYY",
            "theme":"default","tax_rate":0,"accounts":["Cash","G.M. Account","Savings Account"],
            "payment_instructions":"Bank: SBI, A/c no: 20001142967\nIFSC: SBIN0018229\nName: T.ArunPrasad, BE., MBA.\nGpay No: 9940147658",
            "next_invoice_no":1014,"logo_b64":None,
        },
        "transactions":[],"show_new_invoice":False,"selected_invoice":None,"doc_type":"invoice",
        "inv_action":None,
        "show_add_customer":False,"edit_customer_idx":None,"show_add_item":False,"edit_item_idx":None,
    }
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v
    st.session_state.customers=[
        {"name":c,"email":"","phone":"","address":""} if isinstance(c,str) else c
        for c in st.session_state.customers
    ]

init_session()
st.markdown(get_theme_css(), unsafe_allow_html=True)

def nav(page):
    st.session_state.page=page; st.rerun()

def fmt_date(d):
    if not d: return ""
    try:
        dt=datetime.strptime(str(d),"%Y-%m-%d")
        fmt=st.session_state.settings.get("date_format","DD/MM/YYYY")
        if fmt=="DD/MM/YYYY": return dt.strftime("%d/%m/%Y")
        elif fmt=="MM/DD/YYYY": return dt.strftime("%m/%d/%Y")
        elif fmt=="YYYY/MM/DD": return dt.strftime("%Y/%m/%d")
        return dt.strftime("%d/%m/%Y")
    except: return str(d)

def build_invoice_html(doc, cfg, s, for_download=False):
    items=doc.get("items",[])
    subtotal=doc.get("subtotal",sum(i.get("amount",0) for i in items))
    tax_rate=doc.get("tax_rate", s.get("tax_rate",0))
    tax=doc.get("tax",int(subtotal*tax_rate/100))
    total=doc.get("amount",subtotal+tax)
    logo_b64=s.get("logo_b64")

    rows=""
    for item in items:
        rows+=f"""<tr>
          <td style="padding:10px 12px;font-weight:600;border-bottom:1px solid #f0f0f0;">{item.get("name","")}</td>
          <td style="padding:10px 12px;text-align:center;border-bottom:1px solid #f0f0f0;">{item.get("qty",1)}</td>
          <td style="padding:10px 12px;text-align:right;border-bottom:1px solid #f0f0f0;">Rs.{item.get("price",0):,.2f}</td>
          <td style="padding:10px 12px;text-align:right;border-bottom:1px solid #f0f0f0;">Rs.{item.get("amount",0):,.2f}</td>
        </tr>"""
    if not rows:
        rows=f'<tr><td colspan="3" style="padding:12px;text-align:right;color:#6b7280;">Invoice Total</td><td style="padding:12px;text-align:right;font-weight:700;">Rs.{total:,.2f}</td></tr>'

    logo_html=""
    if logo_b64:
        logo_html=f'<img src="data:image/png;base64,{logo_b64}" style="max-width:120px;max-height:80px;object-fit:contain;">'

    tax_row=""
    if tax>0:
        tax_row=f'<tr><td style="padding:4px 8px;text-align:right;font-size:13px;color:#6b7280;">Tax ({tax_rate}%)</td><td style="padding:4px 8px;text-align:right;font-size:13px;">Rs.{tax:,.2f}</td></tr>'

    addr2=s.get("company_address2","")
    cust_data={}
    for c in st.session_state.customers:
        if isinstance(c,dict) and c.get("name")==doc.get("customer"):
            cust_data=c; break

    html=f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{doc["id"]}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333;background:#fff;padding:32px;}}
.wrap{{max-width:720px;margin:0 auto;background:#fff;}}
.header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px;padding-bottom:20px;border-bottom:2px solid #e5e7eb;}}
.logo-area{{flex:1;}}
.inv-title{{text-align:right;}}
.inv-title h1{{font-size:32px;font-weight:900;color:#1a1a1a;margin-bottom:4px;}}
.inv-title .co-name{{font-size:15px;font-weight:700;color:#1a1a1a;}}
.inv-title .co-info{{font-size:12px;color:#6b7280;line-height:1.6;}}
.bill-section{{display:flex;justify-content:space-between;margin-bottom:20px;padding:14px 16px;background:#f8f9fa;border-radius:6px;}}
.bill-to h3{{font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;}}
.bill-to .cname{{font-size:15px;font-weight:700;color:#1a1a1a;}}
.bill-to .cinfo{{font-size:12px;color:#6b7280;line-height:1.7;}}
.inv-meta{{text-align:right;}}
.inv-meta table{{margin-left:auto;}}
.inv-meta td{{padding:3px 8px;font-size:13px;}}
.inv-meta .label{{color:#6b7280;text-align:right;}}
.inv-meta .value{{font-weight:700;text-align:right;}}
table.items{{width:100%;border-collapse:collapse;margin-bottom:20px;}}
table.items thead tr{{background:#1a1a1a;color:#fff;}}
table.items thead th{{padding:10px 12px;text-align:left;font-size:12px;font-weight:600;}}
table.items thead th:not(:first-child){{text-align:center;}}
table.items thead th:last-child{{text-align:right;}}
.bottom{{display:flex;justify-content:space-between;align-items:flex-start;margin-top:8px;}}
.payment-info{{flex:1;margin-right:32px;}}
.payment-info h4{{font-size:12px;font-weight:700;color:#1a1a1a;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px;}}
.payment-info p{{font-size:12px;color:#374151;line-height:1.7;}}
.totals{{min-width:220px;}}
.totals table{{width:100%;border-collapse:collapse;}}
.totals td{{padding:5px 8px;font-size:13px;}}
.totals .label{{color:#6b7280;text-align:right;}}
.totals .value{{text-align:right;font-weight:600;}}
.amount-due{{background:#f8f9fa;border:1px solid #e5e7eb;border-radius:6px;padding:12px 16px;margin-top:8px;text-align:center;}}
.amount-due .label{{font-size:12px;color:#6b7280;margin-bottom:4px;}}
.amount-due .amount{{font-size:22px;font-weight:900;color:#1a1a1a;}}
.footer{{margin-top:28px;padding-top:14px;border-top:1px solid #e5e7eb;text-align:center;font-size:11px;color:#9ca3af;}}
@media print{{button{{display:none!important;}} body{{padding:16px;}}}}
</style></head><body><div class="wrap">
<div class="header">
  <div class="logo-area">{logo_html}</div>
  <div class="inv-title">
    <h1>Invoice</h1>
    <div class="co-name">{s.get("company_name","AP Tech Care")}</div>
    <div class="co-info">
      {s.get("company_address1","")}<br>
      {addr2}<br>
      {s.get("company_phone","")}<br>
      {s.get("company_email","")}
    </div>
  </div>
</div>
<div class="bill-section">
  <div class="bill-to">
    <h3>Bill To</h3>
    <div class="cname">{doc["customer"]}</div>
    <div class="cinfo">
      {cust_data.get("address","") if cust_data.get("address") else ""}<br>
      {"Ph: "+cust_data.get("phone","") if cust_data.get("phone") else ""}
    </div>
  </div>
  <div class="inv-meta">
    <table>
      <tr><td class="label">Invoice #</td><td class="value">{doc["id"]}</td></tr>
      <tr><td class="label">Date</td><td class="value">{fmt_date(doc["date"])}</td></tr>
      {"<tr><td class='label'>Due</td><td class='value'>"+fmt_date(doc["due"])+"</td></tr>" if doc.get("due") else ""}
    </table>
  </div>
</div>
<table class="items">
  <thead><tr>
    <th>Item</th>
    <th style="text-align:center;">Quantity</th>
    <th style="text-align:right;">Price</th>
    <th style="text-align:right;">Amount</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>
<div class="bottom">
  <div class="payment-info">
    <h4>Payment Instructions</h4>
    <p>{s.get("payment_instructions","").replace(chr(10),"<br>")}</p>
  </div>
  <div class="totals">
    <table>
      <tr><td class="label">Subtotal</td><td class="value">Rs.{subtotal:,.2f}</td></tr>
      {tax_row}
      <tr><td class="label">Total</td><td class="value">Rs.{total:,.2f}</td></tr>
    </table>
    <div class="amount-due">
      <div class="label">Amount due</div>
      <div class="amount">Rs.{total:,.2f}</div>
    </div>
  </div>
</div>
<div class="footer">Generated by AP Tech Care Invoice App</div>
</div></body></html>"""
    return html, total

with st.sidebar:
    s=st.session_state.settings
    logo_b64=s.get("logo_b64")
    if logo_b64:
        st.markdown(f'<div style="padding:16px 16px 8px;"><img src="data:image/png;base64,{logo_b64}" style="width:48px;height:48px;border-radius:10px;object-fit:cover;"></div>', unsafe_allow_html=True)
    st.markdown(f"""<div style="padding:{'4px' if logo_b64 else '20px'} 16px 16px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
        {'' if logo_b64 else '<div style="width:36px;height:36px;border-radius:9px;background:#4F46E5;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><span style="color:#fff;font-weight:800;font-size:12px;">AP</span></div>'}
        <div><div style="font-weight:700;font-size:14px;color:#111827;">{s.get("company_name","AP Tech Care")}</div>
        <div style="font-size:11px;color:#9CA3AF;">Smart Tech Solutions</div></div>
      </div></div>""", unsafe_allow_html=True)
    cur=st.session_state.page
    st.markdown(f"""<style>[data-testid="stSidebar"] [data-testid="stButton-nav_{cur}"] > button {{
        background:#EEF2FF !important; color:#4F46E5 !important; font-weight:600 !important;
    }}</style>""", unsafe_allow_html=True)
    st.markdown('<div style="padding:0 12px;margin-bottom:4px;font-size:10px;font-weight:600;color:#9CA3AF;letter-spacing:1px;">DOCUMENTS</div>', unsafe_allow_html=True)
    for pid,icon,label in [("home","🏠","Home"),("invoice","📄","Invoices"),("estimate","📋","Estimates"),
        ("credit","💳","Credit Notes"),("delivery","🚚","Delivery Notes"),("purchase","🛒","Purchase Orders")]:
        if st.button(f"{icon}  {label}",key=f"nav_{pid}",use_container_width=True): nav(pid)
    st.markdown('<div style="padding:0 12px;margin:12px 0 4px;font-size:10px;font-weight:600;color:#9CA3AF;letter-spacing:1px;">MANAGE</div>', unsafe_allow_html=True)
    for pid,icon,label in [("cashflow","📊","Cash Flow"),("reports","📈","Reports"),
        ("items","📦","Items"),("customers","👥","Customers"),("settings","⚙️","Settings")]:
        if st.button(f"{icon}  {label}",key=f"nav_{pid}",use_container_width=True): nav(pid)
    st.markdown("---")
    if st.button("🚪  Logout",key="nav_logout",use_container_width=True):
        st.session_state.logged_in=False; st.rerun()

if st.session_state.page!="home":
    if st.button("← Home",key="global_back"): nav("home")
    st.markdown("<div class='ap-divider'></div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════
def render_home():
    invoices=st.session_state.invoices
    st.markdown('<p class="page-title">Dashboard</p>',unsafe_allow_html=True)
    st.markdown('<p class="page-sub">AP Tech Care — Smart Tech Solutions</p>',unsafe_allow_html=True)
    total=len(invoices); paid_amt=sum(i["amount"] for i in invoices if i["status"]=="paid")
    pending_amt=sum(i["amount"] for i in invoices if i["status"] not in ["paid","cancelled"])
    overdue_n=len([i for i in invoices if i["status"]=="overdue"])
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric("Total Invoices",total)
    with c2: st.metric("Collected",f"₹{paid_amt/1000:.1f}K")
    with c3: st.metric("Outstanding",f"₹{pending_amt/1000:.1f}K")
    with c4: st.metric("Overdue",overdue_n)
    st.markdown("<div class='ap-divider'></div>",unsafe_allow_html=True)
    st.markdown("<p style='font-size:11px;font-weight:600;color:#9CA3AF;letter-spacing:1px;margin-bottom:10px;'>QUICK ACTIONS</p>",unsafe_allow_html=True)
    q1,q2,q3,q4,q5,q6=st.columns(6)
    for col,pid,icon,label in [(q1,"invoice","📄","Invoice"),(q2,"estimate","📋","Estimate"),
        (q3,"credit","💳","Credit Note"),(q4,"delivery","🚚","Delivery"),
        (q5,"purchase","🛒","Purchase"),(q6,"cashflow","📊","Cash Flow")]:
        with col:
            if st.button(f"{icon}\n\n{label}",key=f"qa_{pid}",use_container_width=True): nav(pid)
    st.markdown("<div class='ap-divider'></div>",unsafe_allow_html=True)
    left,right=st.columns([2,1])
    with left:
        st.markdown("<p style='font-size:14px;font-weight:600;color:#111827;margin-bottom:10px;'>Unpaid Invoices</p>",unsafe_allow_html=True)
        pending=[i for i in invoices if i["status"] not in ["paid","cancelled"]]
        if not pending:
            st.markdown('<div class="ap-card" style="text-align:center;padding:28px;color:#9CA3AF;">✅ All invoices are paid!</div>',unsafe_allow_html=True)
        else:
            for inv in pending[:5]:
                bm={"overdue":("#FEE2E2","#991B1B"),"sent":("#DBEAFE","#1E40AF"),"draft":("#F3F4F6","#6B7280"),"read":("#FEF9C3","#854D0E")}
                bg,fg=bm.get(inv["status"],("#F3F4F6","#6B7280"))
                od='<span style="font-size:11px;color:#EF4444;font-weight:600;">● Overdue</span>' if inv["status"]=="overdue" else ""
                cl,cr=st.columns([3,1])
                with cl: st.markdown(f'<div class="ap-card" style="margin-bottom:6px;"><div style="font-weight:600;font-size:14px;color:#111827;">{inv["customer"]}</div><div style="font-size:12px;color:#9CA3AF;margin-top:2px;">{inv["id"]} • Due: {fmt_date(inv["due"])}</div>{od}</div>',unsafe_allow_html=True)
                with cr: st.markdown(f'<div class="ap-card" style="margin-bottom:6px;text-align:right;"><div style="font-weight:700;font-size:14px;color:#111827;">₹{inv["amount"]:,.0f}</div><span style="background:{bg};color:{fg};padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;">{inv["status"].title()}</span></div>',unsafe_allow_html=True)
        if st.button("View All Invoices →",key="home_view_all"): nav("invoice")
    with right:
        st.markdown("<p style='font-size:14px;font-weight:600;color:#111827;margin-bottom:10px;'>Summary</p>",unsafe_allow_html=True)
        statuses={}
        for inv in invoices: statuses[inv["status"]]=statuses.get(inv["status"],0)+1
        sc={"paid":"#166534","sent":"#1E40AF","overdue":"#991B1B","draft":"#6B7280","read":"#854D0E","cancelled":"#991B1B"}
        for s2,c in statuses.items():
            st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:#fff;border:1px solid #E8EAED;border-radius:10px;margin-bottom:6px;"><span style="font-size:13px;color:#374151;">{s2.title()}</span><span style="font-weight:700;font-size:13px;color:{sc.get(s2,"#6B7280")};">{c}</span></div>',unsafe_allow_html=True)
        st.markdown("<div class='ap-divider'></div>",unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;flex-direction:column;gap:6px;margin-bottom:12px;"><div style="display:flex;justify-content:space-between;padding:10px 14px;background:#EEF2FF;border-radius:10px;"><span style="font-size:13px;color:#374151;">👥 Customers</span><span style="font-weight:700;font-size:13px;color:#4F46E5;">{len(st.session_state.customers)}</span></div><div style="display:flex;justify-content:space-between;padding:10px 14px;background:#F0FDF4;border-radius:10px;"><span style="font-size:13px;color:#374151;">📦 Items</span><span style="font-weight:700;font-size:13px;color:#166534;">{len(st.session_state.items_db)}</span></div></div>',unsafe_allow_html=True)
        if st.button("➕ New Customer",use_container_width=True,key="home_add_cust"): nav("customers")
        if st.button("➕ New Item",use_container_width=True,key="home_add_item"): nav("items")

# ══════════════════════════════════════════════════════════════════
# DOCUMENTS
# ══════════════════════════════════════════════════════════════════
DOC_LABELS={"invoice":{"title":"Invoices","icon":"📄","header":"INVOICE"},"estimate":{"title":"Estimates","icon":"📋","header":"ESTIMATE"},"credit":{"title":"Credit Notes","icon":"💳","header":"CREDIT NOTE"},"delivery":{"title":"Delivery Notes","icon":"🚚","header":"DELIVERY NOTE"},"purchase":{"title":"Purchase Orders","icon":"🛒","header":"PURCHASE ORDER"}}

def render_documents(doc_type):
    cfg=DOC_LABELS[doc_type]
    docs=[i for i in st.session_state.invoices if i.get("type","invoice")==doc_type]
    prefixes={"invoice":"AP","estimate":"EST","credit":"CN","delivery":"DN","purchase":"PO"}
    s=st.session_state.settings

    # ── Invoice action panel (Preview / Send / Payment / Cancel) ──
    if st.session_state.get("selected_invoice"):
        doc=st.session_state.selected_invoice
        action=st.session_state.get("inv_action","preview")

        # Top bar
        cb,_,cact=st.columns([1,2,2])
        with cb:
            if st.button("← Back",key="inv_back",use_container_width=True):
                st.session_state.selected_invoice=None
                st.session_state.inv_action=None
                st.rerun()

        # Action tabs
        st.markdown("<div style='margin:12px 0 4px;'>",unsafe_allow_html=True)
        a1,a2,a3,a4=st.columns(4)
        with a1:
            if st.button("👁 Preview",key="act_preview",use_container_width=True,
                type="primary" if action=="preview" else "secondary"):
                st.session_state.inv_action="preview"; st.rerun()
        with a2:
            if st.button("📤 Send",key="act_send",use_container_width=True,
                type="primary" if action=="send" else "secondary"):
                st.session_state.inv_action="send"; st.rerun()
        with a3:
            if st.button("💰 Record Payment",key="act_pay",use_container_width=True,
                type="primary" if action=="pay" else "secondary"):
                st.session_state.inv_action="pay"; st.rerun()
        with a4:
            if st.button("✕ Cancel Invoice",key="act_cancel",use_container_width=True):
                st.session_state.inv_action="cancel"; st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<div class='ap-divider'></div>",unsafe_allow_html=True)

        html_content, total = build_invoice_html(doc, cfg, s)

        if action=="preview":
            st.markdown(html_content, unsafe_allow_html=True)

        elif action=="send":
            st.markdown("### 📤 Send Invoice")
            # Download PDF
            st.download_button(
                "⬇️ Download Invoice (HTML→PDF)",
                data=html_content.encode("utf-8"),
                file_name=f"{doc['id']}_{doc['customer'].replace(' ','_')}.html",
                mime="text/html",type="primary",use_container_width=False
            )
            st.markdown("---")
            st.markdown("**📱 Send on WhatsApp**")
            cust_phone=""
            for c in st.session_state.customers:
                if isinstance(c,dict) and c.get("name")==doc.get("customer"):
                    cust_phone=c.get("phone","").replace(" ","").replace("+","")
                    break
            msg=f"Dear {doc['customer']},\n\nPlease find your {cfg['header']} *{doc['id']}* for *Rs.{total:,.2f}*\nDate: {fmt_date(doc['date'])}\nDue: {fmt_date(doc['due'])}\n\n{s.get('payment_instructions','')}\n\nThank you!\n{s.get('company_name','AP Tech Care')}"
            wa_url=f"https://wa.me/{cust_phone}?text={urllib.parse.quote(msg)}" if cust_phone else f"https://wa.me/?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background:#25D366;color:white;border:none;padding:10px 24px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;width:100%;margin-top:4px;">💬 Send on WhatsApp</button></a>',unsafe_allow_html=True)
            st.info("💡 Steps to send PDF on WhatsApp:\n1. Click **Download** above\n2. Open the `.html` file in Chrome\n3. Press **Ctrl+P** → **Save as PDF**\n4. Open WhatsApp → Attach the PDF file")

        elif action=="pay":
            st.markdown("### 💰 Record Payment")
            if doc["status"]=="paid":
                st.success("✅ This invoice is already marked as paid!")
            else:
                with st.form("record_payment_form"):
                    pay_date=st.date_input("Payment Date",value=date.today())
                    pay_method=st.selectbox("Payment Method",["Cash","UPI / GPay","Bank Transfer","Cheque","Other"])
                    pay_note=st.text_input("Note (optional)")
                    col1,col2=st.columns(2)
                    with col1: confirm=st.form_submit_button("✅ Mark as Paid",type="primary",use_container_width=True)
                    with col2: back=st.form_submit_button("✕ Cancel",use_container_width=True)
                    if confirm:
                        for i,inv in enumerate(st.session_state.invoices):
                            if inv["id"]==doc["id"]:
                                st.session_state.invoices[i]["status"]="paid"
                                st.session_state.invoices[i]["paid_date"]=str(pay_date)
                                st.session_state.invoices[i]["pay_method"]=pay_method
                                st.session_state.selected_invoice=st.session_state.invoices[i]
                                break
                        st.success(f"✅ {doc['id']} marked as Paid via {pay_method}!")
                        st.session_state.inv_action="preview"; st.rerun()
                    if back:
                        st.session_state.inv_action="preview"; st.rerun()

        elif action=="cancel":
            st.markdown("### ✕ Cancel Invoice")
            st.warning(f"Are you sure you want to cancel **{doc['id']}** for **{doc['customer']}** (Rs.{total:,.2f})?")
            col1,col2=st.columns(2)
            with col1:
                if st.button("✅ Yes, Cancel Invoice",type="primary",use_container_width=True):
                    for i,inv in enumerate(st.session_state.invoices):
                        if inv["id"]==doc["id"]:
                            st.session_state.invoices[i]["status"]="cancelled"
                            break
                    st.session_state.selected_invoice=None; st.session_state.inv_action=None
                    st.success("Invoice cancelled."); st.rerun()
            with col2:
                if st.button("← Go Back",use_container_width=True):
                    st.session_state.inv_action="preview"; st.rerun()
        return

    # ── Page header ──
    col1,col2=st.columns([3,1])
    with col1:
        st.markdown(f'<p class="page-title">{cfg["icon"]} {cfg["title"]}</p>',unsafe_allow_html=True)
        st.markdown(f'<p class="page-sub">{len(docs)} total {cfg["title"].lower()}</p>',unsafe_allow_html=True)
    with col2:
        if st.button(f'➕ New {cfg["title"][:-1]}',type="primary",use_container_width=True):
            st.session_state.show_new_invoice=True
            st.session_state.doc_type=doc_type
            st.session_state.selected_invoice=None
            st.rerun()

    # ── New invoice form ──
    if st.session_state.get("show_new_invoice") and st.session_state.get("doc_type")==doc_type:
        st.markdown("---")
        st.markdown(f"### ➕ New {cfg['title'][:-1]}")

        # Customer select
        cust_names=[c["name"] if isinstance(c,dict) else c for c in st.session_state.customers]
        with st.form(key=f"new_{doc_type}_form"):
            c1,c2,c3=st.columns(3)
            with c1: customer=st.selectbox("Customer *",cust_names+["+ Add New"])
            with c2:
                prefix=prefixes.get(doc_type,"AP"); n=s.get("next_invoice_no",1001)
                inv_no=st.text_input("Invoice #",value=f"{prefix}-{n}")
            with c3: inv_date=st.date_input("Date",value=date.today())

            c4,c5,c6=st.columns(3)
            with c4: due_date=st.date_input("Due Date",value=date.today()+timedelta(days=15))
            with c5: status=st.selectbox("Status",["draft","sent","read","paid"])
            with c6: tax_rate_val=st.number_input("Tax %",min_value=0.0,max_value=100.0,value=float(s.get("tax_rate",0)),step=0.5)

            st.markdown("**Line Items**")
            item_rows=st.session_state.get(f"ir_{doc_type}",1); line_items=[]
            inames=[i["name"] for i in st.session_state.items_db]
            for i in range(item_rows):
                ci1,ci2,ci3,ci4=st.columns([3,1,1,1])
                with ci1: iname=st.selectbox(f"Item {i+1}",["—"]+inames,key=f"in_{doc_type}_{i}")
                with ci2: qty=st.number_input("Qty",min_value=1,value=1,key=f"q_{doc_type}_{i}")
                with ci3:
                    dp=0
                    if iname and iname!="—":
                        found=next((x for x in st.session_state.items_db if x["name"]==iname),None)
                        if found: dp=found["price"]
                    price=st.number_input("Price",min_value=0,value=dp,key=f"p_{doc_type}_{i}")
                with ci4: st.markdown(f"<div style='padding-top:28px;font-weight:700;color:#4F46E5;'>₹{qty*price:,}</div>",unsafe_allow_html=True)
                if iname and iname!="—": line_items.append({"name":iname,"qty":qty,"price":price,"amount":qty*price})

            subtotal=sum(x["amount"] for x in line_items)
            tax=int(subtotal*tax_rate_val/100); total=subtotal+tax
            st.markdown(f'<div style="background:#f8f9fa;border-radius:10px;padding:14px 18px;margin:10px 0;"><div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span style="color:#9CA3AF;font-size:13px;">Subtotal</span><span style="font-weight:600;">₹{subtotal:,}</span></div>{"<div style=\'display:flex;justify-content:space-between;margin-bottom:4px;\'><span style=\'color:#9CA3AF;font-size:13px;\'>Tax ("+str(tax_rate_val)+"%)</span><span style=\'font-weight:600;\'>₹"+str(tax)+"</span></div>" if tax>0 else ""}<div style="display:flex;justify-content:space-between;padding-top:8px;border-top:2px solid #E8EAED;"><span style="font-weight:700;font-size:15px;">Total</span><span style="font-weight:900;font-size:17px;color:#4F46E5;">₹{total:,}</span></div></div>',unsafe_allow_html=True)

            cs,ca,cp,cc=st.columns([2,1,1,1])
            with cs: save=st.form_submit_button("💾 Save",type="primary",use_container_width=True)
            with ca: add_row=st.form_submit_button("➕ Row",use_container_width=True)
            with cp: preview=st.form_submit_button("👁 Preview",use_container_width=True)
            with cc: cancel=st.form_submit_button("✕ Cancel",use_container_width=True)

            if save and customer and customer!="+ Add New":
                new_doc={"id":inv_no,"type":doc_type,"customer":customer,"date":str(inv_date),
                         "due":str(due_date),"amount":total,"status":status,
                         "items":line_items,"subtotal":subtotal,"tax":tax,"tax_rate":tax_rate_val}
                st.session_state.invoices.insert(0,new_doc)
                s["next_invoice_no"]=s.get("next_invoice_no",1001)+1
                st.session_state.show_new_invoice=False; st.session_state[f"ir_{doc_type}"]=1
                st.success(f"✅ {inv_no} saved!"); st.rerun()
            if add_row: st.session_state[f"ir_{doc_type}"]=item_rows+1; st.rerun()
            if preview and customer and customer!="+ Add New":
                preview_doc={"id":inv_no,"type":doc_type,"customer":customer,"date":str(inv_date),
                             "due":str(due_date),"amount":total,"status":status,
                             "items":line_items,"subtotal":subtotal,"tax":tax,"tax_rate":tax_rate_val}
                st.session_state.selected_invoice=preview_doc
                st.session_state.inv_action="preview"; st.rerun()
            if cancel:
                st.session_state.show_new_invoice=False; st.session_state[f"ir_{doc_type}"]=1; st.rerun()

    # ── Invoice list with tabs ──
    tabs=st.tabs(["All","Draft","Sent","Read","Paid","Overdue","Cancelled"])
    for tab,flt in zip(tabs,["all","draft","sent","read","paid","overdue","cancelled"]):
        with tab:
            filtered=docs if flt=="all" else [d for d in docs if d["status"]==flt]
            search=st.text_input("🔍",placeholder="Search...",key=f"srch_{doc_type}_{flt}",label_visibility="collapsed")
            if search: filtered=[d for d in filtered if search.lower() in d["customer"].lower() or search.lower() in d["id"].lower()]
            if not filtered:
                st.markdown(f'<div class="ap-card" style="text-align:center;padding:32px;color:#9CA3AF;">No {cfg["title"].lower()} found</div>',unsafe_allow_html=True)
            else:
                for doc in filtered:
                    c1,c2,c3,c4,c5=st.columns([3,1,1,1,1])
                    bm={"paid":("#DCFCE7","#166534"),"overdue":("#FEE2E2","#991B1B"),"sent":("#DBEAFE","#1E40AF"),"draft":("#F3F4F6","#6B7280"),"read":("#FEF9C3","#854D0E"),"cancelled":("#FEE2E2","#991B1B")}
                    bg,fg=bm.get(doc["status"],("#F3F4F6","#6B7280"))
                    with c1: st.markdown(f'<div style="padding:8px 0;"><div style="font-weight:600;font-size:14px;color:#111827;">{doc["customer"]}</div><div style="font-size:12px;color:#9CA3AF;">{doc["id"]} • {fmt_date(doc["date"])}</div></div>',unsafe_allow_html=True)
                    with c2: st.markdown(f'<div style="padding:8px 0;text-align:right;"><div style="font-weight:700;font-size:14px;color:#111827;">₹{doc["amount"]:,.0f}</div><span style="background:{bg};color:{fg};padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;">{doc["status"].title()}</span></div>',unsafe_allow_html=True)
                    with c3:
                        if st.button("👁",key=f"v_{flt}_{doc['id']}",use_container_width=True,help="Preview"):
                            st.session_state.selected_invoice=doc; st.session_state.inv_action="preview"; st.rerun()
                    with c4:
                        if st.button("📤",key=f"s_{flt}_{doc['id']}",use_container_width=True,help="Send"):
                            st.session_state.selected_invoice=doc; st.session_state.inv_action="send"; st.rerun()
                    with c5:
                        if st.button("💰",key=f"p_{flt}_{doc['id']}",use_container_width=True,help="Payment"):
                            st.session_state.selected_invoice=doc; st.session_state.inv_action="pay"; st.rerun()
                    st.markdown("<hr style='margin:4px 0;border-color:#F3F4F6;'>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CASHFLOW
# ══════════════════════════════════════════════════════════════════
def render_cashflow():
    st.markdown('<p class="page-title">📊 Cash Flow</p>',unsafe_allow_html=True)
    invoices=st.session_state.invoices
    tab1,tab2,tab3=st.tabs(["📊 Dashboard","🏦 Accounts","💸 Transactions"])
    with tab1:
        total_in=sum(i["amount"] for i in invoices if i["status"]=="paid")
        total_out=st.session_state.get("total_expenses",0); net=total_in-total_out
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f'<div style="background:#D1FAE5;border-radius:14px;padding:20px;"><p style="margin:0;font-size:12px;font-weight:700;color:#065F46;">💰 Total Collected</p><p style="margin:8px 0 0;font-size:26px;font-weight:900;color:#065F46;">₹{total_in:,.0f}</p></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div style="background:#FEE2E2;border-radius:14px;padding:20px;"><p style="margin:0;font-size:12px;font-weight:700;color:#991B1B;">💸 Total Expense</p><p style="margin:8px 0 0;font-size:26px;font-weight:900;color:#991B1B;">₹{total_out:,.0f}</p></div>',unsafe_allow_html=True)
        with c3:
            color="#065F46" if net>=0 else "#991B1B"; bg="#D1FAE5" if net>=0 else "#FEE2E2"
            st.markdown(f'<div style="background:{bg};border-radius:14px;padding:20px;"><p style="margin:0;font-size:12px;font-weight:700;color:{color};">📈 Net Balance</p><p style="margin:8px 0 0;font-size:26px;font-weight:900;color:{color};">₹{net:,.0f}</p></div>',unsafe_allow_html=True)
        st.markdown("---"); st.markdown("**Recent Paid Invoices**")
        for inv in [i for i in invoices if i["status"]=="paid"][:5]:
            st.markdown(f'<div class="ap-card" style="display:flex;justify-content:space-between;margin-bottom:8px;"><div><div style="font-weight:700;">{inv["customer"]}</div><div style="font-size:12px;color:#6b7280;">{inv["id"]} • {fmt_date(inv["date"])}</div></div><div style="font-weight:900;color:#10B981;font-size:16px;">+₹{inv["amount"]:,.0f}</div></div>',unsafe_allow_html=True)
    with tab2:
        for acc in st.session_state.settings.get("accounts",["Cash","G.M. Account","Savings Account"]):
            st.markdown(f'<div class="ap-card" style="display:flex;justify-content:space-between;align-items:center;"><span style="font-weight:600;">💰 {acc}</span><span style="font-weight:700;color:#4F46E5;">₹0</span></div>',unsafe_allow_html=True)
    with tab3:
        txns=st.session_state.get("transactions",[])
        if st.button("➕ Add Transaction",type="primary"):
            with st.form("add_txn"):
                c1,c2=st.columns(2)
                with c1: txn_type=st.selectbox("Type",["Income","Expense"]); amount=st.number_input("Amount ₹",min_value=0)
                with c2: desc=st.text_input("Description"); acct=st.selectbox("Account",st.session_state.settings.get("accounts",["Cash"]))
                if st.form_submit_button("Save"):
                    txns.append({"type":txn_type,"amount":amount,"desc":desc,"account":acct}); st.session_state.transactions=txns; st.rerun()
        for t in txns[-10:]:
            color="#10B981" if t["type"]=="Income" else "#EF4444"; sign="+" if t["type"]=="Income" else "-"
            st.markdown(f'<div class="ap-card" style="display:flex;justify-content:space-between;"><div><div style="font-weight:600;">{t["desc"]}</div><div style="font-size:12px;color:#6b7280;">{t["account"]}</div></div><div style="font-weight:700;color:{color};">{sign}₹{t["amount"]:,}</div></div>',unsafe_allow_html=True)
        if not txns: st.info("No transactions yet.")

# ══════════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════════
def render_reports():
    st.markdown('<p class="page-title">📈 Reports</p>',unsafe_allow_html=True)
    invoices=st.session_state.invoices
    tab1,tab2=st.tabs(["📅 Monthly Report","📊 Summary"])
    with tab1:
        months={}
        for inv in invoices:
            try:
                m=datetime.strptime(inv["date"],"%Y-%m-%d").strftime("%b %Y")
                months.setdefault(m,{"total":0,"paid":0,"count":0})
                months[m]["total"]+=inv["amount"]; months[m]["count"]+=1
                if inv["status"]=="paid": months[m]["paid"]+=inv["amount"]
            except: pass
        for month,data in months.items():
            st.markdown(f'<div class="ap-card"><div style="font-weight:700;font-size:15px;margin-bottom:8px;">📅 {month}</div><div style="display:flex;gap:24px;"><div><span style="font-size:12px;color:#9CA3AF;">Invoices</span><br><span style="font-weight:700;">{data["count"]}</span></div><div><span style="font-size:12px;color:#9CA3AF;">Total</span><br><span style="font-weight:700;">₹{data["total"]:,}</span></div><div><span style="font-size:12px;color:#9CA3AF;">Collected</span><br><span style="font-weight:700;color:#10B981;">₹{data["paid"]:,}</span></div><div><span style="font-size:12px;color:#9CA3AF;">Pending</span><br><span style="font-weight:700;color:#EF4444;">₹{data["total"]-data["paid"]:,}</span></div></div></div>',unsafe_allow_html=True)
    with tab2:
        total=sum(i["amount"] for i in invoices); collected=sum(i["amount"] for i in invoices if i["status"]=="paid")
        st.metric("Total Billed",f"₹{total:,}"); st.metric("Collected",f"₹{collected:,}"); st.metric("Outstanding",f"₹{total-collected:,}")
        top=max(invoices,key=lambda x:x["amount"],default=None)
        if top: st.metric("Top Invoice",f"{top['customer']} — ₹{top['amount']:,}")

# ══════════════════════════════════════════════════════════════════
# CUSTOMERS
# ══════════════════════════════════════════════════════════════════
def render_customers():
    st.markdown('<p class="page-title">👥 Customers</p>',unsafe_allow_html=True)
    customers=st.session_state.customers
    _,col2=st.columns([3,1])
    with col2:
        if st.button("➕ Add Customer",type="primary",use_container_width=True):
            st.session_state.show_add_customer=True; st.session_state.edit_customer_idx=None
    search=st.text_input("🔍 Search",placeholder="Name or email...",label_visibility="collapsed",key="cust_search")
    filtered=[c for c in customers if not search or search.lower() in c["name"].lower() or search.lower() in c.get("email","").lower()]
    for cust in filtered:
        ri=customers.index(cust); c1,c2,c3=st.columns([4,1,1])
        with c1:
            invs=[i for i in st.session_state.invoices if i["customer"]==cust["name"]]
            st.markdown(f'<div style="padding:6px 0;"><div style="font-weight:600;font-size:14px;color:#111827;">{cust["name"]}</div><div style="font-size:12px;color:#9CA3AF;">{cust.get("email","—")} • {cust.get("phone","—")} • {len(invs)} invoices • ₹{sum(i["amount"] for i in invs):,}</div></div>',unsafe_allow_html=True)
        with c2:
            if st.button("✏️",key=f"ec_{ri}"): st.session_state.edit_customer_idx=ri; st.session_state.show_add_customer=False
        with c3:
            if st.button("🗑️",key=f"dc_{ri}"): customers.pop(ri); st.rerun()
        st.markdown("<hr style='margin:4px 0;border-color:#F3F4F6;'>",unsafe_allow_html=True)
    ei=st.session_state.get("edit_customer_idx")
    if ei is not None and ei<len(customers):
        cust=customers[ei]; st.markdown("---"); st.markdown(f"### ✏️ Edit — {cust['name']}")
        with st.form("edit_cust_form"):
            c1,c2=st.columns(2)
            with c1:
                ename=st.text_input("Name *",value=cust.get("name",""),key="ecn")
                ephone=st.text_input("Phone",value=cust.get("phone",""),key="ecp")
            with c2:
                eemail=st.text_input("Email",value=cust.get("email",""),key="ece")
                eaddress=st.text_input("Address",value=cust.get("address",""),key="eca")
            cs,cc=st.columns(2)
            with cs: esave=st.form_submit_button("💾 Save",type="primary",use_container_width=True)
            with cc: eclose=st.form_submit_button("✕ Close",use_container_width=True)
            if esave and ename:
                customers[ei]={"name":ename,"email":eemail,"phone":ephone,"address":eaddress}
                st.session_state.edit_customer_idx=None; st.success("✅ Updated!"); st.rerun()
            if eclose: st.session_state.edit_customer_idx=None; st.rerun()
    if st.session_state.get("show_add_customer"):
        st.markdown("---"); st.markdown("### ➕ New Customer")
        with st.form("add_cust_form"):
            c1,c2=st.columns(2)
            with c1:
                aname=st.text_input("Name *",key="acn")
                aphone=st.text_input("Phone",key="acp")
            with c2:
                aemail=st.text_input("Email",key="ace")
                aaddress=st.text_input("Address",key="aca")
            cs,cc=st.columns(2)
            with cs: asave=st.form_submit_button("💾 Save Customer",type="primary",use_container_width=True)
            with cc: aclose=st.form_submit_button("✕ Close",use_container_width=True)
            if asave and aname:
                customers.append({"name":aname,"email":aemail,"phone":aphone,"address":aaddress})
                st.session_state.show_add_customer=False; st.success(f"✅ '{aname}' added!"); st.rerun()
            if aclose: st.session_state.show_add_customer=False; st.rerun()

# ══════════════════════════════════════════════════════════════════
# ITEMS
# ══════════════════════════════════════════════════════════════════
def render_items():
    st.markdown('<p class="page-title">📦 Items</p>',unsafe_allow_html=True)
    items=st.session_state.items_db
    _,col2=st.columns([3,1])
    with col2:
        if st.button("➕ Add Item",type="primary",use_container_width=True):
            st.session_state.show_add_item=True; st.session_state.edit_item_idx=None
    search=st.text_input("🔍 Search",placeholder="Item name or code...",label_visibility="collapsed",key="item_search")
    filtered=[i for i in items if not search or search.lower() in i["name"].lower() or search.lower() in i.get("code","").lower()]
    for item in filtered:
        ri=items.index(item); c1,c2,c3,c4=st.columns([3,1,1,1])
        with c1: st.markdown(f'<div style="padding:6px 0;"><div style="font-weight:600;font-size:14px;color:#111827;">{item["name"]}</div><div style="font-size:12px;color:#9CA3AF;">Code: {item.get("code","—")} • {item.get("unit","")}</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f"<div style='padding-top:8px;font-weight:700;color:#166534;'>₹{item['price']:,}</div>",unsafe_allow_html=True)
        with c3:
            if st.button("✏️",key=f"ei_{ri}"): st.session_state.edit_item_idx=ri; st.session_state.show_add_item=False
        with c4:
            if st.button("🗑️",key=f"di_{ri}"): items.pop(ri); st.rerun()
        st.markdown("<hr style='margin:4px 0;border-color:#F3F4F6;'>",unsafe_allow_html=True)
    ei2=st.session_state.get("edit_item_idx")
    if ei2 is not None and ei2<len(items):
        item=items[ei2]; st.markdown("---"); st.markdown(f"### ✏️ Edit — {item['name']}")
        with st.form("edit_item_form"):
            c1,c2=st.columns(2)
            with c1:
                iname=st.text_input("Item Name *",value=item.get("name",""),key="ein")
                iprice=st.number_input("Price ₹",min_value=0,value=int(item.get("price",0)),key="eip")
            with c2:
                icode=st.text_input("Product Code",value=item.get("code",""),key="eic")
                iunit=st.text_input("Unit Type",value=item.get("unit","per unit"),key="eiu")
            idesc=st.text_area("Description",value=item.get("desc",""),max_chars=10000,key="eid")
            cs,cc=st.columns(2)
            with cs: isave=st.form_submit_button("💾 Save",type="primary",use_container_width=True)
            with cc: iclose=st.form_submit_button("✕ Close",use_container_width=True)
            if isave and iname: items[ei2]={"name":iname,"code":icode,"price":iprice,"unit":iunit,"desc":idesc}; st.session_state.edit_item_idx=None; st.success("✅ Updated!"); st.rerun()
            if iclose: st.session_state.edit_item_idx=None; st.rerun()
    if st.session_state.get("show_add_item"):
        st.markdown("---"); st.markdown("### ➕ New Item")
        with st.form("add_item_form"):
            c1,c2=st.columns(2)
            with c1:
                ainame=st.text_input("Item Name *",key="ain")
                aiprice=st.number_input("Price ₹",min_value=0,key="aip")
            with c2:
                aicode=st.text_input("Product Code",key="aic")
                aiunit=st.text_input("Unit Type",value="per unit",key="aiu")
            aidesc=st.text_area("Description",max_chars=10000,key="aid")
            cs,cc=st.columns(2)
            with cs: aisave=st.form_submit_button("💾 Save Item",type="primary",use_container_width=True)
            with cc: aiclose=st.form_submit_button("✕ Close",use_container_width=True)
            if aisave and ainame: items.append({"name":ainame,"code":aicode,"price":aiprice,"unit":aiunit,"desc":aidesc}); st.session_state.show_add_item=False; st.success(f"✅ '{ainame}' added!"); st.rerun()
            if aiclose: st.session_state.show_add_item=False; st.rerun()

# ══════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════
def render_settings():
    st.markdown('<p class="page-title">⚙️ Settings</p>',unsafe_allow_html=True)
    s=st.session_state.settings
    section=st.radio("",["🏢 Company & Logo","🧾 Tax","💳 Payment","🏦 Accounts","💱 Currency"],horizontal=True,label_visibility="collapsed")
    st.markdown("---")
    if section=="🏢 Company & Logo":
        st.markdown("### 🏢 Company Information")
        logo_file=st.file_uploader("Upload Company Logo",type=["png","jpg","jpeg"])
        if logo_file:
            s["logo_b64"]=base64.b64encode(logo_file.read()).decode()
            st.success("✅ Logo uploaded!"); st.rerun()
        if s.get("logo_b64"):
            st.markdown(f'<img src="data:image/png;base64,{s["logo_b64"]}" style="width:80px;height:80px;border-radius:12px;object-fit:cover;margin-bottom:12px;">',unsafe_allow_html=True)
            if st.button("🗑️ Remove Logo"): s["logo_b64"]=None; st.rerun()
        st.markdown("---")
        c1,c2=st.columns(2)
        with c1:
            sname=st.text_input("Company Name *",value=s.get("company_name","AP Tech Care"))
            sphone=st.text_input("Phone",value=s.get("company_phone",""))
            saddr1=st.text_input("Address Line 1",value=s.get("company_address1",""))
            saddr2=st.text_input("Address Line 2",value=s.get("company_address2",""))
        with c2:
            semail=st.text_input("Email",value=s.get("company_email",""))
            sgst=st.text_input("GST Number",value=s.get("gst_no",""))
            scity=st.text_input("City",value=s.get("city","Chennai"))
            sstate=st.text_input("State",value=s.get("state","Tamil Nadu"))
        if st.button("💾 Save Company Info",type="primary"):
            s.update({"company_name":sname,"company_email":semail,"company_phone":sphone,"gst_no":sgst,
                      "company_address1":saddr1,"company_address2":saddr2,"city":scity,"state":sstate})
            st.success("✅ Saved!"); st.rerun()
    elif section=="🧾 Tax":
        st.markdown("### 🧾 Tax Settings")
        c1,c2=st.columns(2)
        with c1: tax_name=st.text_input("Tax Name",value=s.get("tax_name","GST"))
        with c2: tax_rate=st.number_input("Default Tax Rate (%)",min_value=0.0,max_value=100.0,value=float(s.get("tax_rate",0)),step=0.5)
        inclusive=st.checkbox("Prices are tax inclusive",value=s.get("tax_inclusive",False))
        if st.button("💾 Save Tax Settings",type="primary"):
            s.update({"tax_name":tax_name,"tax_rate":tax_rate,"tax_inclusive":inclusive}); st.success("✅ Saved!")
    elif section=="💳 Payment":
        st.markdown("### 💳 Payment Instructions")
        instructions=st.text_area("Instructions",value=s.get("payment_instructions",""),height=150)
        qr=st.file_uploader("Payment QR Code",type=["png","jpg","jpeg"],key="qr_upload")
        if qr: st.image(qr,width=160)
        if st.button("💾 Save",type="primary"): s["payment_instructions"]=instructions; st.success("✅ Saved!")
    elif section=="🏦 Accounts":
        st.markdown("### 🏦 Transaction Accounts")
        accounts=s.get("accounts",["Cash","G.M. Account","Savings Account"])
        for i,acc in enumerate(accounts):
            c1,c2=st.columns([5,1])
            with c1: st.markdown(f'<div style="padding:12px 16px;background:#f8f9fa;border:1px solid #E8EAED;border-radius:8px;font-weight:600;">💰 {acc}</div>',unsafe_allow_html=True)
            with c2:
                if st.button("🗑️",key=f"delacc_{i}"): accounts.pop(i); s["accounts"]=accounts; st.rerun()
        st.markdown("---")
        new_acc=st.text_input("New Account Name")
        if st.button("➕ Add Account",type="primary"):
            if new_acc: accounts.append(new_acc); s["accounts"]=accounts; st.success(f"✅ '{new_acc}' added!"); st.rerun()
    elif section=="💱 Currency":
        st.markdown("### 💱 Currency & Date Format")
        c1,c2=st.columns(2)
        with c1: currency=st.selectbox("Currency",["INR","USD","EUR","GBP","AED"],index=["INR","USD","EUR","GBP","AED"].index(s.get("currency","INR")))
        with c2: date_fmt=st.selectbox("Date Format",["DD/MM/YYYY","MM/DD/YYYY","YYYY/MM/DD"],index=["DD/MM/YYYY","MM/DD/YYYY","YYYY/MM/DD"].index(s.get("date_format","DD/MM/YYYY")))
        if st.button("💾 Save",type="primary"): s.update({"currency":currency,"date_format":date_fmt}); st.success("✅ Saved!")

# ══════════════════════════════════════════════════════════════════
# ROUTING
# ══════════════════════════════════════════════════════════════════
page=st.session_state.page
if page=="home": render_home()
elif page in ["invoice","estimate","credit","delivery","purchase"]: render_documents(page)
elif page=="cashflow": render_cashflow()
elif page=="reports": render_reports()
elif page=="customers": render_customers()
elif page=="items": render_items()
elif page=="settings": render_settings()
