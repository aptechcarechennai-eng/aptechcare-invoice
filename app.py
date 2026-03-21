import streamlit as st
from datetime import datetime, date, timedelta
import base64

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
            {"id":"AP-1001","type":"invoice","customer":"TechSoft Pvt Ltd",   "date":"2025-06-01","due":"2025-06-15","amount":18500,"status":"paid",   "items":[]},
            {"id":"AP-1002","type":"invoice","customer":"InfoBridge Solutions","date":"2025-06-05","due":"2025-06-20","amount":32000,"status":"sent",   "items":[]},
            {"id":"AP-1003","type":"invoice","customer":"Nexus Digital",      "date":"2025-06-10","due":"2025-06-10","amount":7500, "status":"overdue","items":[]},
            {"id":"AP-1004","type":"invoice","customer":"CloudVerse Inc",     "date":"2025-06-12","due":"2025-06-26","amount":54000,"status":"draft",  "items":[]},
            {"id":"AP-1005","type":"invoice","customer":"ByteWave Tech",      "date":"2025-06-14","due":"2025-06-28","amount":12300,"status":"sent",   "items":[]},
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
        ],
        "settings":{
            "company_name":"AP Tech Care","company_email":"info@aptechcare.in",
            "company_phone":"+91 98765 43210","company_address1":"Chennai, Tamil Nadu",
            "gst_no":"33XXXXX1234Z1","currency":"INR","date_format":"DD/MM/YYYY",
            "theme":"default","tax_rate":18,"accounts":["Cash","G.M. Account","Savings Account"],
            "payment_instructions":"Please transfer to our bank account.\nUPI ID: aptechcare@upi\nBank: HDFC | A/c: XXXXXXXXXXXX | IFSC: HDFC0001234",
            "next_invoice_no":1006,"logo_b64":None,
        },
        "transactions":[],"show_new_invoice":False,"selected_invoice":None,"doc_type":"invoice",
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

# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    s=st.session_state.settings
    logo_b64=s.get("logo_b64")
    if logo_b64:
        st.markdown(f'<div style="padding:16px 16px 8px;"><img src="data:image/png;base64,{logo_b64}" style="width:48px;height:48px;border-radius:10px;object-fit:cover;"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="padding:{'4px' if logo_b64 else '20px'} 16px 16px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
        {'' if logo_b64 else '<div style="width:36px;height:36px;border-radius:9px;background:#4F46E5;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><span style="color:#fff;font-weight:800;font-size:12px;">AP</span></div>'}
        <div>
          <div style="font-weight:700;font-size:14px;color:#111827;">{s.get("company_name","AP Tech Care")}</div>
          <div style="font-size:11px;color:#9CA3AF;">Smart Tech Solutions</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

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
    pending_amt=sum(i["amount"] for i in invoices if i["status"]!="paid")
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
        pending=[i for i in invoices if i["status"]!="paid"]
        if not pending:
            st.markdown('<div class="ap-card" style="text-align:center;padding:28px;color:#9CA3AF;">✅ All invoices are paid!</div>',unsafe_allow_html=True)
        else:
            for inv in pending[:5]:
                bm={"overdue":("#FEE2E2","#991B1B"),"sent":("#DBEAFE","#1E40AF"),"draft":("#F3F4F6","#6B7280"),"read":("#FEF9C3","#854D0E")}
                bg,fg=bm.get(inv["status"],("#F3F4F6","#6B7280"))
                od='<span style="font-size:11px;color:#EF4444;font-weight:600;">● Overdue</span>' if inv["status"]=="overdue" else ""
                cl,cr=st.columns([3,1])
                with cl: st.markdown(f'<div class="ap-card" style="margin-bottom:6px;"><div style="font-weight:600;font-size:14px;color:#111827;">{inv["customer"]}</div><div style="font-size:12px;color:#9CA3AF;margin-top:2px;">{inv["id"]} • Due: {inv["due"]}</div>{od}</div>',unsafe_allow_html=True)
                with cr: st.markdown(f'<div class="ap-card" style="margin-bottom:6px;text-align:right;"><div style="font-weight:700;font-size:14px;color:#111827;">₹{inv["amount"]:,.0f}</div><span style="background:{bg};color:{fg};padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;">{inv["status"].title()}</span></div>',unsafe_allow_html=True)
        if st.button("View All Invoices →",key="home_view_all"): nav("invoice")
    with right:
        st.markdown("<p style='font-size:14px;font-weight:600;color:#111827;margin-bottom:10px;'>Summary</p>",unsafe_allow_html=True)
        statuses={}
        for inv in invoices: statuses[inv["status"]]=statuses.get(inv["status"],0)+1
        sc={"paid":"#166534","sent":"#1E40AF","overdue":"#991B1B","draft":"#6B7280","read":"#854D0E"}
        for s,c in statuses.items():
            st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:#fff;border:1px solid #E8EAED;border-radius:10px;margin-bottom:6px;"><span style="font-size:13px;color:#374151;">{s.title()}</span><span style="font-weight:700;font-size:13px;color:{sc.get(s,"#6B7280")};">{c}</span></div>',unsafe_allow_html=True)
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
    col1,col2=st.columns([3,1])
    with col1:
        st.markdown(f'<p class="page-title">{cfg["icon"]} {cfg["title"]}</p>',unsafe_allow_html=True)
        st.markdown(f'<p class="page-sub">{len(docs)} total {cfg["title"].lower()}</p>',unsafe_allow_html=True)
    with col2:
        if st.button(f'➕ New {cfg["title"][:-1]}',type="primary",use_container_width=True):
            st.session_state.show_new_invoice=True; st.session_state.doc_type=doc_type

    if st.session_state.get("selected_invoice"):
        doc=st.session_state.selected_invoice; s=st.session_state.settings
        cb, cw, ce, cp = st.columns([1,1,1,1])
        with cb:
            if st.button("← Back",key="print_back",use_container_width=True):
                st.session_state.selected_invoice=None; st.rerun()
        with cw:
            phone = doc.get("customer_phone","")
            msg = f"Dear {doc['customer']}, your {cfg['header']} {doc['id']} of ₹{doc.get('amount',0):,.0f} is due on {doc['due']}. Please transfer to: {st.session_state.settings.get('payment_instructions','').split(chr(10))[0] if st.session_state.settings.get('payment_instructions') else ''}. Thank you - {st.session_state.settings.get('company_name','AP Tech Care')}"
            import urllib.parse
            wa_url = f"https://wa.me/?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%;padding:8px;background:#25D366;color:white;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:13px;">💬 WhatsApp</button></a>', unsafe_allow_html=True)
        with ce:
            subject = urllib.parse.quote(f"{cfg['header']} {doc['id']} from {st.session_state.settings.get('company_name','AP Tech Care')}")
            body = urllib.parse.quote(f"Dear {doc['customer']},\n\nPlease find your {cfg['header']} {doc['id']} for ₹{doc.get('amount',0):,.0f} due on {doc['due']}.\n\nThank you,\n{st.session_state.settings.get('company_name','AP Tech Care')}")
            st.markdown(f'<a href="mailto:?subject={subject}&body={body}"><button style="width:100%;padding:8px;background:#4F46E5;color:white;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:13px;">📧 Email</button></a>', unsafe_allow_html=True)
        with cp:
            st.markdown('<button onclick="window.print()" style="width:100%;padding:8px;background:#111827;color:white;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:13px;">🖨️ Print</button>', unsafe_allow_html=True)
        items=doc.get("items",[]); subtotal=doc.get("subtotal",sum(i.get("amount",0) for i in items))
        tax_rate=s.get("tax_rate",18); tax=doc.get("tax",int(subtotal*tax_rate/100)); total=doc.get("amount",subtotal+tax)
        rows=""
        for idx,item in enumerate(items,1):
            rows+=f'<tr style="background:{"#fff" if idx%2==0 else "#f8f9fa"}"><td style="padding:10px 14px;color:#6b7280;font-size:13px;">{idx}</td><td style="padding:10px 14px;font-weight:600;">{item.get("name","")}</td><td style="padding:10px 14px;text-align:center;">{item.get("qty",1)}</td><td style="padding:10px 14px;text-align:right;">₹{item.get("price",0):,}</td><td style="padding:10px 14px;text-align:right;font-weight:700;">₹{item.get("amount",0):,}</td></tr>'
        if not rows: rows='<tr><td colspan="5" style="padding:20px;text-align:center;color:#9ca3af;">No items</td></tr>'
        logo_b64=s.get("logo_b64")
        logo_html=f'<img src="data:image/png;base64,{logo_b64}" style="width:56px;height:56px;border-radius:10px;object-fit:cover;margin-bottom:10px;">' if logo_b64 else '<div style="width:56px;height:56px;border-radius:10px;background:#4F46E5;display:flex;align-items:center;justify-content:center;margin-bottom:10px;"><span style="color:#fff;font-weight:900;font-size:14px;">AP</span></div>'
        st.markdown(f"""<div style="max-width:680px;margin:0 auto;background:#fff;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,0.08);overflow:hidden;">
          <div style="padding:32px 40px 24px;border-bottom:2px solid #f3f4f6;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
              <div>{logo_html}
                <div style="font-weight:800;font-size:18px;color:#111827;">{s.get("company_name","AP Tech Care")}</div>
                <div style="font-size:12px;color:#9CA3AF;">{s.get("company_address1","Chennai, Tamil Nadu")}</div>
                <div style="font-size:12px;color:#9CA3AF;">{s.get("company_phone","")}</div>
                <div style="font-size:12px;color:#9CA3AF;">GST: {s.get("gst_no","")}</div>
              </div>
              <div style="text-align:right;">
                <div style="font-size:28px;font-weight:900;color:#4F46E5;">{cfg["header"]}</div>
                <div style="font-size:16px;font-weight:700;color:#111827;">{doc["id"]}</div>
                <div style="font-size:12px;color:#9CA3AF;margin-top:8px;">Date: {doc["date"]}</div>
                <div style="font-size:12px;color:#9CA3AF;">Due: {doc["due"]}</div>
              </div>
            </div>
          </div>
          <div style="padding:20px 40px;">
            <div style="background:#f8f9fa;border-radius:10px;padding:12px 16px;margin-bottom:20px;">
              <div style="font-size:10px;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:1px;margin-bottom:3px;">Bill To</div>
              <div style="font-weight:700;font-size:15px;color:#111827;">{doc["customer"]}</div>
            </div>
            <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
              <thead><tr style="background:#4F46E5;color:#fff;">
                <th style="padding:10px 14px;text-align:left;font-size:12px;">#</th>
                <th style="padding:10px 14px;text-align:left;font-size:12px;">Item</th>
                <th style="padding:10px 14px;text-align:center;font-size:12px;">Qty</th>
                <th style="padding:10px 14px;text-align:right;font-size:12px;">Rate</th>
                <th style="padding:10px 14px;text-align:right;font-size:12px;">Amount</th>
              </tr></thead><tbody>{rows}</tbody>
            </table>
            <div style="display:flex;justify-content:flex-end;">
              <div style="width:240px;">
                <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #E8EAED;"><span style="font-size:13px;color:#9CA3AF;">Subtotal</span><span style="font-size:13px;font-weight:600;">₹{subtotal:,}</span></div>
                <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #E8EAED;"><span style="font-size:13px;color:#9CA3AF;">GST ({tax_rate}%)</span><span style="font-size:13px;font-weight:600;">₹{tax:,}</span></div>
                <div style="display:flex;justify-content:space-between;padding:10px 12px;background:#4F46E5;border-radius:8px;margin-top:6px;"><span style="font-size:14px;font-weight:700;color:#fff;">Total</span><span style="font-size:16px;font-weight:900;color:#fff;">₹{total:,}</span></div>
              </div>
            </div>
            <div style="margin-top:24px;padding-top:16px;border-top:1px solid #E8EAED;font-size:12px;color:#6B7280;">{s.get("payment_instructions","").replace(chr(10),"<br>")}</div>
            <div style="margin-top:16px;text-align:center;font-size:11px;color:#9CA3AF;">Thank you! — {s.get("company_name","AP Tech Care")}</div>
          </div></div>""",unsafe_allow_html=True)

        # PDF Download
        pdf_html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
        <style>body{{font-family:Arial,sans-serif;margin:0;padding:20px;}}
        table{{width:100%;border-collapse:collapse;}}
        th{{background:#4F46E5;color:white;padding:10px 14px;text-align:left;font-size:12px;}}
        td{{padding:10px 14px;border-bottom:1px solid #e5e7eb;font-size:13px;}}
        .total-row{{background:#4F46E5;color:white;padding:10px 12px;border-radius:6px;}}
        @media print{{button{{display:none!important;}}.no-print{{display:none!important;}}}}
        </style></head><body>
        <div style="display:flex;justify-content:space-between;padding-bottom:20px;border-bottom:2px solid #f3f4f6;">
          <div><h2 style="margin:0;color:#111827;">{s.get("company_name","AP Tech Care")}</h2>
          <p style="margin:4px 0;color:#6b7280;font-size:12px;">{s.get("company_address1","")}</p>
          <p style="margin:4px 0;color:#6b7280;font-size:12px;">{s.get("company_phone","")}</p>
          <p style="margin:4px 0;color:#6b7280;font-size:12px;">GST: {s.get("gst_no","")}</p></div>
          <div style="text-align:right;"><h1 style="color:#4F46E5;margin:0;">{cfg["header"]}</h1>
          <p style="font-size:16px;font-weight:bold;margin:4px 0;">{doc["id"]}</p>
          <p style="color:#6b7280;font-size:12px;margin:4px 0;">Date: {doc["date"]}</p>
          <p style="color:#6b7280;font-size:12px;margin:4px 0;">Due: {doc["due"]}</p></div>
        </div>
        <div style="background:#f8f9fa;padding:12px 16px;border-radius:8px;margin:16px 0;">
          <p style="font-size:10px;color:#9ca3af;margin:0 0 4px;text-transform:uppercase;letter-spacing:1px;">Bill To</p>
          <h3 style="margin:0;color:#111827;">{doc["customer"]}</h3>
        </div>
        <table><thead><tr>{"".join(f'<th>{h}</th>' for h in ["#","Item","Qty","Rate","Amount"])}</tr></thead>
        <tbody>{"".join(f"<tr><td>{i+1}</td><td>{it.get('name','')}</td><td style='text-align:center'>{it.get('qty',1)}</td><td style='text-align:right'>Rs.{it.get('price',0):,}</td><td style='text-align:right;font-weight:bold'>Rs.{it.get('amount',0):,}</td></tr>" for i,it in enumerate(items))}</tbody>
        </table>
        <div style="display:flex;justify-content:flex-end;margin-top:16px;">
          <div style="width:240px;">
            <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #e5e7eb;"><span style="color:#6b7280;">Subtotal</span><span>Rs.{subtotal:,}</span></div>
            <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #e5e7eb;"><span style="color:#6b7280;">GST ({tax_rate}%)</span><span>Rs.{tax:,}</span></div>
            <div class="total-row" style="display:flex;justify-content:space-between;margin-top:6px;"><span style="font-weight:bold;">Total</span><span style="font-weight:bold;">Rs.{total:,}</span></div>
          </div>
        </div>
        <div style="margin-top:24px;padding-top:16px;border-top:1px solid #e5e7eb;font-size:12px;color:#6b7280;">{s.get("payment_instructions","").replace(chr(10),"<br>")}</div>
        <p style="text-align:center;font-size:11px;color:#9ca3af;margin-top:16px;">Thank you for your business! — {s.get("company_name","AP Tech Care")}</p>
        </body></html>"""

        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_html.encode("utf-8"),
            file_name=f"{doc['id']}.html",
            mime="text/html",
            use_container_width=False,
        )
        st.caption("💡 Open downloaded file in browser → Ctrl+P → Save as PDF")
        return

    if st.session_state.get("show_new_invoice") and st.session_state.get("doc_type")==doc_type:
        st.markdown("---"); st.markdown(f"### ➕ New {cfg['title'][:-1]}")
        with st.form(key=f"new_{doc_type}_form"):
            c1,c2,c3=st.columns(3)
            with c1:
                cust_names=[c["name"] if isinstance(c,dict) else c for c in st.session_state.customers]
                customer=st.selectbox("Customer *",cust_names+["+ Add New"])
            with c2:
                prefix=prefixes.get(doc_type,"AP"); n=st.session_state.settings.get("next_invoice_no",1001)
                inv_no=st.text_input("Document #",value=f"{prefix}-{n}")
            with c3: inv_date=st.date_input("Date",value=date.today())
            c4,c5=st.columns(2)
            with c4: due_date=st.date_input("Due Date",value=date.today()+timedelta(days=15))
            with c5: status=st.selectbox("Status",["draft","sent","read","paid"])
            st.markdown("**Items**")
            item_rows=st.session_state.get(f"ir_{doc_type}",1); line_items=[]; inames=[i["name"] for i in st.session_state.items_db]
            for i in range(item_rows):
                ci1,ci2,ci3,ci4=st.columns([3,1,1,1])
                with ci1: iname=st.selectbox(f"Item {i+1}",["—"]+inames,key=f"in_{doc_type}_{i}")
                with ci2: qty=st.number_input("Qty",min_value=1,value=1,key=f"q_{doc_type}_{i}")
                with ci3:
                    dp=0
                    if iname and iname!="—":
                        found=next((x for x in st.session_state.items_db if x["name"]==iname),None)
                        if found: dp=found["price"]
                    price=st.number_input("Price ₹",min_value=0,value=dp,key=f"p_{doc_type}_{i}")
                with ci4: st.markdown(f"<div style='padding-top:28px;font-weight:700;color:#4F46E5;'>₹{qty*price:,}</div>",unsafe_allow_html=True)
                if iname and iname!="—": line_items.append({"name":iname,"qty":qty,"price":price,"amount":qty*price})
            subtotal=sum(x["amount"] for x in line_items); tax_rate=st.session_state.settings.get("tax_rate",18)
            tax=int(subtotal*tax_rate/100); total=subtotal+tax
            st.markdown(f'<div style="background:#f8f9fa;border-radius:10px;padding:14px 18px;margin:10px 0;"><div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span style="color:#9CA3AF;font-size:13px;">Subtotal</span><span style="font-weight:600;">₹{subtotal:,}</span></div><div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span style="color:#9CA3AF;font-size:13px;">GST ({tax_rate}%)</span><span style="font-weight:600;">₹{tax:,}</span></div><div style="display:flex;justify-content:space-between;padding-top:8px;border-top:2px solid #E8EAED;"><span style="font-weight:700;font-size:15px;">Total</span><span style="font-weight:900;font-size:17px;color:#4F46E5;">₹{total:,}</span></div></div>',unsafe_allow_html=True)
            cs,ca,cc=st.columns([2,1,1])
            with cs: save=st.form_submit_button("💾 Save",type="primary",use_container_width=True)
            with ca: add_row=st.form_submit_button("➕ Row",use_container_width=True)
            with cc: cancel=st.form_submit_button("✕ Cancel",use_container_width=True)
            if save and customer and customer!="+ Add New":
                st.session_state.invoices.insert(0,{"id":inv_no,"type":doc_type,"customer":customer,"date":str(inv_date),"due":str(due_date),"amount":total,"status":status,"items":line_items,"subtotal":subtotal,"tax":tax})
                st.session_state.settings["next_invoice_no"]=st.session_state.settings.get("next_invoice_no",1001)+1
                st.session_state.show_new_invoice=False; st.session_state[f"ir_{doc_type}"]=1; st.success(f"✅ {inv_no} saved!"); st.rerun()
            if add_row: st.session_state[f"ir_{doc_type}"]=item_rows+1; st.rerun()
            if cancel: st.session_state.show_new_invoice=False; st.session_state[f"ir_{doc_type}"]=1; st.rerun()

    tabs=st.tabs(["All","Draft","Sent","Read","Paid","Overdue"])
    for tab,flt in zip(tabs,["all","draft","sent","read","paid","overdue"]):
        with tab:
            filtered=docs if flt=="all" else [d for d in docs if d["status"]==flt]
            search=st.text_input("🔍",placeholder="Search...",key=f"srch_{doc_type}_{flt}",label_visibility="collapsed")
            if search: filtered=[d for d in filtered if search.lower() in d["customer"].lower() or search.lower() in d["id"].lower()]
            if not filtered:
                st.markdown(f'<div class="ap-card" style="text-align:center;padding:32px;color:#9CA3AF;">No {cfg["title"].lower()} found</div>',unsafe_allow_html=True)
            else:
                for doc in filtered:
                    c1,c2,c3=st.columns([4,2,1])
                    with c1: st.markdown(f'<div style="padding:4px 0;"><div style="font-weight:600;font-size:14px;color:#111827;">{doc["customer"]}</div><div style="font-size:12px;color:#9CA3AF;">{doc["id"]} • {doc["date"]} • Due: {doc["due"]}</div></div>',unsafe_allow_html=True)
                    with c2:
                        bm={"paid":("#DCFCE7","#166534"),"overdue":("#FEE2E2","#991B1B"),"sent":("#DBEAFE","#1E40AF"),"draft":("#F3F4F6","#6B7280"),"read":("#FEF9C3","#854D0E")}
                        bg,fg=bm.get(doc["status"],("#F3F4F6","#6B7280"))
                        st.markdown(f'<div style="padding:4px 0;text-align:right;"><div style="font-weight:700;font-size:15px;color:#111827;">₹{doc["amount"]:,.0f}</div><span style="background:{bg};color:{fg};padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;">{doc["status"].title()}</span></div>',unsafe_allow_html=True)
                    with c3:
                        if st.button("👁 View",key=f"v_{flt}_{doc['id']}",use_container_width=True):
                            st.session_state.selected_invoice=doc; st.rerun()
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
        total_out=st.session_state.get("total_expenses",45000)
        net=total_in-total_out
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f'<div style="background:#D1FAE5;border-radius:14px;padding:20px;"><p style="margin:0;font-size:12px;font-weight:700;color:#065F46;">💰 Total Income</p><p style="margin:8px 0 0;font-size:26px;font-weight:900;color:#065F46;">₹{total_in:,.0f}</p></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div style="background:#FEE2E2;border-radius:14px;padding:20px;"><p style="margin:0;font-size:12px;font-weight:700;color:#991B1B;">💸 Total Expense</p><p style="margin:8px 0 0;font-size:26px;font-weight:900;color:#991B1B;">₹{total_out:,.0f}</p></div>',unsafe_allow_html=True)
        with c3:
            color="#065F46" if net>=0 else "#991B1B"; bg="#D1FAE5" if net>=0 else "#FEE2E2"
            st.markdown(f'<div style="background:{bg};border-radius:14px;padding:20px;"><p style="margin:0;font-size:12px;font-weight:700;color:{color};">📈 Net Balance</p><p style="margin:8px 0 0;font-size:26px;font-weight:900;color:{color};">₹{net:,.0f}</p></div>',unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Recent Paid Invoices**")
        for inv in [i for i in invoices if i["status"]=="paid"][:5]:
            st.markdown(f'<div class="ap-card" style="display:flex;justify-content:space-between;margin-bottom:8px;"><div><div style="font-weight:700;">{inv["customer"]}</div><div style="font-size:12px;color:#6b7280;">{inv["id"]} • {inv["date"]}</div></div><div style="font-weight:900;color:#10B981;font-size:16px;">+₹{inv["amount"]:,.0f}</div></div>',unsafe_allow_html=True)

    with tab2:
        accounts=st.session_state.settings.get("accounts",["Cash","G.M. Account","Savings Account"])
        for acc in accounts:
            st.markdown(f'<div class="ap-card" style="display:flex;justify-content:space-between;align-items:center;"><span style="font-weight:600;">💰 {acc}</span><span style="font-weight:700;color:#4F46E5;">₹0</span></div>',unsafe_allow_html=True)

    with tab3:
        txns=st.session_state.get("transactions",[])
        if st.button("➕ Add Transaction",type="primary"):
            with st.form("add_txn"):
                c1,c2=st.columns(2)
                with c1: txn_type=st.selectbox("Type",["Income","Expense"]); amount=st.number_input("Amount ₹",min_value=0)
                with c2: desc=st.text_input("Description"); acct=st.selectbox("Account",st.session_state.settings.get("accounts",["Cash"]))
                if st.form_submit_button("Save"):
                    txns.append({"type":txn_type,"amount":amount,"desc":desc,"account":acct})
                    st.session_state.transactions=txns; st.rerun()
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
            with c1: name=st.text_input("Name *",value=cust.get("name","")); phone=st.text_input("Phone",value=cust.get("phone",""))
            with c2: email=st.text_input("Email",value=cust.get("email","")); address=st.text_input("Address",value=cust.get("address",""))
            cs,cc=st.columns(2)
            with cs: save=st.form_submit_button("💾 Save",type="primary",use_container_width=True)
            with cc: close=st.form_submit_button("✕ Close",use_container_width=True)
            if save and name: customers[ei]={"name":name,"email":email,"phone":phone,"address":address}; st.session_state.edit_customer_idx=None; st.success("✅ Updated!"); st.rerun()
            if close: st.session_state.edit_customer_idx=None; st.rerun()
    if st.session_state.get("show_add_customer"):
        st.markdown("---"); st.markdown("### ➕ New Customer")
        with st.form("add_cust_form"):
            c1,c2=st.columns(2)
            with c1: name=st.text_input("Name *"); phone=st.text_input("Phone")
            with c2: email=st.text_input("Email"); address=st.text_input("Address")
            cs,cc=st.columns(2)
            with cs: save=st.form_submit_button("💾 Save",type="primary",use_container_width=True)
            with cc: close=st.form_submit_button("✕ Close",use_container_width=True)
            if save and name: customers.append({"name":name,"email":email,"phone":phone,"address":address}); st.session_state.show_add_customer=False; st.success(f"✅ '{name}' added!"); st.rerun()
            if close: st.session_state.show_add_customer=False; st.rerun()

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
    ei=st.session_state.get("edit_item_idx")
    if ei is not None and ei<len(items):
        item=items[ei]; st.markdown("---"); st.markdown(f"### ✏️ Edit — {item['name']}")
        with st.form("edit_item_form"):
            c1,c2=st.columns(2)
            with c1: name=st.text_input("Item Name *",value=item.get("name","")); price=st.number_input("Price ₹",min_value=0,value=int(item.get("price",0)))
            with c2: code=st.text_input("Product Code",value=item.get("code","")); unit=st.text_input("Unit Type",value=item.get("unit","per unit"))
            desc=st.text_area("Description",value=item.get("desc",""),max_chars=10000)
            cs,cc=st.columns(2)
            with cs: save=st.form_submit_button("💾 Save",type="primary",use_container_width=True)
            with cc: close=st.form_submit_button("✕ Close",use_container_width=True)
            if save and name: items[ei]={"name":name,"code":code,"price":price,"unit":unit,"desc":desc}; st.session_state.edit_item_idx=None; st.success("✅ Updated!"); st.rerun()
            if close: st.session_state.edit_item_idx=None; st.rerun()
    if st.session_state.get("show_add_item"):
        st.markdown("---"); st.markdown("### ➕ New Item")
        with st.form("add_item_form"):
            c1,c2=st.columns(2)
            with c1: name=st.text_input("Item Name *"); price=st.number_input("Price ₹",min_value=0)
            with c2: code=st.text_input("Product Code"); unit=st.text_input("Unit Type",value="per unit")
            desc=st.text_area("Description",max_chars=10000)
            cs,cc=st.columns(2)
            with cs: save=st.form_submit_button("💾 Save",type="primary",use_container_width=True)
            with cc: close=st.form_submit_button("✕ Close",use_container_width=True)
            if save and name: items.append({"name":name,"code":code,"price":price,"unit":unit,"desc":desc}); st.session_state.show_add_item=False; st.success(f"✅ '{name}' added!"); st.rerun()
            if close: st.session_state.show_add_item=False; st.rerun()

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
        # Logo upload
        logo_file=st.file_uploader("Upload Company Logo",type=["png","jpg","jpeg"])
        if logo_file:
            b64=base64.b64encode(logo_file.read()).decode()
            s["logo_b64"]=b64
            st.success("✅ Logo uploaded!")
            st.rerun()
        if s.get("logo_b64"):
            st.markdown(f'<img src="data:image/png;base64,{s["logo_b64"]}" style="width:80px;height:80px;border-radius:12px;object-fit:cover;margin-bottom:12px;">',unsafe_allow_html=True)
            if st.button("🗑️ Remove Logo"): s["logo_b64"]=None; st.rerun()
        st.markdown("---")
        c1,c2=st.columns(2)
        with c1:
            name=st.text_input("Company Name *",value=s.get("company_name","AP Tech Care"))
            phone=st.text_input("Phone",value=s.get("company_phone",""))
            addr1=st.text_input("Address Line 1",value=s.get("company_address1",""))
            city=st.text_input("City",value=s.get("city","Chennai"))
        with c2:
            email=st.text_input("Email",value=s.get("company_email",""))
            gst=st.text_input("GST Number",value=s.get("gst_no",""))
            addr2=st.text_input("Address Line 2",value=s.get("addr2",""))
            state=st.text_input("State",value=s.get("state","Tamil Nadu"))
        if st.button("💾 Save Company Info",type="primary"):
            s.update({"company_name":name,"company_email":email,"company_phone":phone,"gst_no":gst,"company_address1":addr1,"addr2":addr2,"city":city,"state":state})
            st.success("✅ Company info saved!"); st.rerun()

    elif section=="🧾 Tax":
        st.markdown("### 🧾 Tax Settings")
        c1,c2=st.columns(2)
        with c1: tax_name=st.text_input("Tax Name",value=s.get("tax_name","GST"))
        with c2: tax_rate=st.number_input("Tax Rate (%)",min_value=0.0,max_value=100.0,value=float(s.get("tax_rate",18)),step=0.5)
        inclusive=st.checkbox("Prices are tax inclusive",value=s.get("tax_inclusive",False))
        if st.button("💾 Save Tax Settings",type="primary"):
            s.update({"tax_name":tax_name,"tax_rate":tax_rate,"tax_inclusive":inclusive}); st.success("✅ Saved!")

    elif section=="💳 Payment":
        st.markdown("### 💳 Payment Instructions")
        instructions=st.text_area("Instructions",value=s.get("payment_instructions",""),height=150)
        st.markdown("**Upload Payment QR Code**")
        qr=st.file_uploader("QR Code",type=["png","jpg","jpeg"],key="qr_upload")
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
# ROUTING — 100% inline, zero imports
# ══════════════════════════════════════════════════════════════════
page=st.session_state.page
if page=="home": render_home()
elif page in ["invoice","estimate","credit","delivery","purchase"]: render_documents(page)
elif page=="cashflow": render_cashflow()
elif page=="reports": render_reports()
elif page=="customers": render_customers()
elif page=="items": render_items()
elif page=="settings": render_settings()
