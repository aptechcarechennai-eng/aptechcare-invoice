import streamlit as st
from datetime import datetime, date, timedelta
import base64, urllib.parse

st.set_page_config(page_title="AP Tech Care", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*,[class*="css"]{font-family:'Inter',sans-serif!important;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stSidebarCollapseButton"],[data-testid="collapsedControl"]{display:none!important;}
section[data-testid="stSidebar"]{min-width:210px!important;width:210px!important;transform:translateX(0)!important;}
.block-container{padding:1.8rem 2rem!important;max-width:100%!important;}
.stApp{background:#F7F8FA!important;}
[data-testid="stSidebar"]{background:#fff!important;border-right:1px solid #E5E7EB!important;}
[data-testid="stSidebar"] *{color:#374151!important;}
[data-testid="stSidebar"] .stButton>button{background:transparent!important;border:none!important;color:#6B7280!important;text-align:left!important;width:100%!important;padding:8px 12px!important;border-radius:7px!important;font-size:13px!important;font-weight:500!important;margin-bottom:1px!important;}
[data-testid="stSidebar"] .stButton>button:hover{background:#F3F4F6!important;color:#111!important;}
.card{background:#fff;border:1px solid #E5E7EB;border-radius:10px;padding:16px 18px;margin-bottom:8px;box-shadow:0 1px 2px rgba(0,0,0,0.04);}
.pt{font-size:20px;font-weight:700;color:#111827;margin:0 0 2px;}
.ps{font-size:12px;color:#9CA3AF;margin:0 0 16px;}
.div{border:none;border-top:1px solid #E5E7EB;margin:14px 0;}
.stButton>button[kind="primary"]{background:#4F46E5!important;color:#fff!important;border:none!important;border-radius:8px!important;font-weight:600!important;}
[data-testid="metric-container"]{background:#fff;border:1px solid #E5E7EB;border-radius:10px;padding:14px!important;}
[data-testid="metric-container"] label{font-size:11px!important;color:#9CA3AF!important;font-weight:500!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{font-size:20px!important;font-weight:700!important;color:#111!important;}
.stTabs [data-baseweb="tab-list"]{gap:0;background:transparent!important;border-bottom:1px solid #E5E7EB!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#9CA3AF!important;font-weight:500!important;font-size:13px!important;padding:7px 16px!important;border:none!important;border-radius:0!important;}
.stTabs [aria-selected="true"]{color:#4F46E5!important;border-bottom:2px solid #4F46E5!important;font-weight:600!important;}
.stTextInput input,.stTextArea textarea,.stDateInput input,.stNumberInput input{border:1px solid #E5E7EB!important;border-radius:7px!important;background:#fff!important;color:#111!important;font-size:13px!important;}
.stSelectbox>div>div{border:1px solid #E5E7EB!important;border-radius:7px!important;font-size:13px!important;}
</style>"""

# ── helpers ──────────────────────────────────────────────────────
def nav(p): st.session_state.page=p; st.rerun()

def fd(d):
    try: return datetime.strptime(str(d),"%Y-%m-%d").strftime("%d/%m/%Y")
    except: return str(d) if d else ""

def inv_html(doc, s):
    items=doc.get("items",[])
    sub=doc.get("subtotal",doc.get("amount",0))
    tax=doc.get("tax",0); total=doc.get("amount",sub+tax)
    lb=s.get("logo_b64","")
    logo=f'<img src="data:image/png;base64,{lb}" style="max-height:70px;max-width:130px;object-fit:contain;">' if lb else ""
    rows=""
    for it in items:
        rows+=f'<tr><td style="padding:8px 10px;border-bottom:1px solid #f0f0f0;font-weight:600">{it.get("name","")}</td><td style="padding:8px 10px;border-bottom:1px solid #f0f0f0;text-align:center">{it.get("qty",1)}</td><td style="padding:8px 10px;border-bottom:1px solid #f0f0f0;text-align:right">Rs.{it.get("price",0):,.2f}</td><td style="padding:8px 10px;border-bottom:1px solid #f0f0f0;text-align:right">Rs.{it.get("amount",0):,.2f}</td></tr>'
    if not rows: rows=f'<tr><td colspan="3" style="padding:10px;text-align:right;color:#777">Total</td><td style="padding:10px;text-align:right;font-weight:700">Rs.{total:,.2f}</td></tr>'
    tax_row=f'<tr><td style="padding:3px 6px;text-align:right;color:#777;font-size:12px">Tax ({doc.get("tax_rate",0)}%)</td><td style="padding:3px 6px;text-align:right;font-size:12px">Rs.{tax:,.2f}</td></tr>' if tax>0 else ""
    cust_info=""
    for c in st.session_state.customers:
        if isinstance(c,dict) and c.get("name")==doc.get("customer"):
            if c.get("address"): cust_info+=f'<br>{c["address"]}'
            if c.get("phone"): cust_info+=f'<br>Ph: {c["phone"]}'
    a2=s.get("company_address2","")
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{doc["id"]}</title>
<style>*{{margin:0;padding:0;box-sizing:border-box;}}body{{font-family:Arial,sans-serif;font-size:13px;color:#1a1a1a;padding:36px;}}
.wrap{{max-width:700px;margin:0 auto;}}.hdr{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:22px;padding-bottom:16px;border-bottom:2px solid #e5e7eb;}}
.co-info{{font-size:12px;color:#555;line-height:1.7;text-align:right;}}.co-name{{font-size:15px;font-weight:700;color:#111;}}
.inv-h1{{font-size:30px;font-weight:900;color:#1a1a1a;margin-bottom:4px;}}.mid{{display:flex;justify-content:space-between;background:#f8f9fa;border-radius:6px;padding:14px 16px;margin-bottom:18px;}}
.bt h4{{font-size:10px;font-weight:700;color:#999;text-transform:uppercase;letter-spacing:1px;margin-bottom:5px;}}.bt .cn{{font-size:14px;font-weight:700;}}.bt .ci{{font-size:12px;color:#666;line-height:1.6;}}
.im td{{font-size:13px;color:#666;}}.im td:last-child{{font-weight:700;text-align:right;padding-left:16px;}}
table.items{{width:100%;border-collapse:collapse;margin-bottom:18px;}}
table.items thead tr{{background:#1a1a1a;color:#fff;}}
table.items thead th{{padding:9px 10px;text-align:left;font-size:12px;}}
table.items thead th:not(:first-child){{text-align:center;}}table.items thead th:last-child{{text-align:right;}}
.bot{{display:flex;justify-content:space-between;align-items:flex-start;}}.pi h4{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;}}.pi p{{font-size:12px;color:#444;line-height:1.7;}}
.tots table{{width:100%;border-collapse:collapse;}}.tots td{{padding:4px 6px;font-size:13px;}}.tots .l{{color:#777;text-align:right;}}.tots .v{{text-align:right;font-weight:600;}}
.amt{{background:#f8f9fa;border:1px solid #e5e7eb;border-radius:6px;padding:12px 14px;margin-top:8px;text-align:center;}}
.amt .al{{font-size:11px;color:#777;margin-bottom:3px;}}.amt .av{{font-size:22px;font-weight:900;}}
.footer{{margin-top:24px;padding-top:12px;border-top:1px solid #e5e7eb;text-align:center;font-size:11px;color:#aaa;}}
@media print{{button{{display:none!important;}}}}</style></head><body><div class="wrap">
<div class="hdr"><div>{logo}</div><div class="inv-title" style="text-align:right"><div class="inv-h1">Invoice</div><div class="co-name">{s.get("company_name","AP Tech Care")}</div><div class="co-info">{s.get("company_address1","")}<br>{a2}<br>{s.get("company_phone","")}<br>{s.get("company_email","")}</div></div></div>
<div class="mid"><div class="bt"><h4>Bill To</h4><div class="cn">{doc["customer"]}</div><div class="ci">{cust_info}</div></div>
<div><table class="im"><tr><td>Invoice #</td><td>{doc["id"]}</td></tr><tr><td>Date</td><td>{fd(doc["date"])}</td></tr>{"<tr><td>Due</td><td>"+fd(doc["due"])+"</td></tr>" if doc.get("due") else ""}</table></div></div>
<table class="items"><thead><tr><th>Item</th><th style="text-align:center">Quantity</th><th style="text-align:right">Price</th><th style="text-align:right">Amount</th></tr></thead><tbody>{rows}</tbody></table>
<div class="bot"><div class="pi" style="flex:1;margin-right:28px"><h4>Payment Instructions</h4><p>{s.get("payment_instructions","").replace(chr(10),"<br>")}</p></div>
<div class="tots"><table><tr><td class="l">Subtotal</td><td class="v">Rs.{sub:,.2f}</td></tr>{tax_row}<tr><td class="l">Total</td><td class="v">Rs.{total:,.2f}</td></tr></table>
<div class="amt"><div class="al">Amount due</div><div class="av">Rs.{total:,.2f}</div></div></div></div>
<div class="footer">Generated by AP Tech Care Invoice App</div></div></body></html>"""

# ── session ──────────────────────────────────────────────────────
def init():
    D={
      "page":"home","selected_inv":None,"inv_action":None,"show_new_inv":False,
      "show_add_cust":False,"edit_cust_idx":None,"show_add_item":False,"edit_item_idx":None,
      "invoices":[
        {"id":"AP-1001","type":"invoice","customer":"TechSoft Pvt Ltd",   "date":"2025-06-01","due":"2025-06-15","amount":18500,"status":"paid",   "items":[],"subtotal":18500,"tax":0,"tax_rate":0},
        {"id":"AP-1002","type":"invoice","customer":"InfoBridge Solutions","date":"2025-06-05","due":"2025-06-20","amount":32000,"status":"sent",   "items":[],"subtotal":32000,"tax":0,"tax_rate":0},
        {"id":"AP-1003","type":"invoice","customer":"Nexus Digital",      "date":"2025-06-10","due":"2025-06-10","amount":7500, "status":"overdue","items":[],"subtotal":7500, "tax":0,"tax_rate":0},
      ],
      "customers":[
        {"name":"TechSoft Pvt Ltd",   "email":"techsoft@example.com", "phone":"9800001111","address":"Chennai"},
        {"name":"InfoBridge Solutions","email":"info@infobridge.com",  "phone":"9800002222","address":"Bangalore"},
        {"name":"Nexus Digital",      "email":"hello@nexusdigital.in","phone":"9800003333","address":"Hyderabad"},
      ],
      "items_db":[
        {"name":"General Service", "code":"GS001","price":500, "unit":"per visit","desc":""},
        {"name":"AMC Service",     "code":"AMC001","price":5000,"unit":"per year","desc":""},
        {"name":"Hardware Repair", "code":"HW002", "price":1500,"unit":"per unit","desc":""},
        {"name":"Software Install","code":"SW003", "price":800, "unit":"per device","desc":""},
        {"name":"Network Setup",   "code":"NW004", "price":3500,"unit":"per job","desc":""},
      ],
      "settings":{
        "company_name":"AP Tech Care","company_email":"aptechcare.chennai@gmail.com",
        "company_phone":"9940147658","company_address1":"1/4A, Kamaraj Cross Street,",
        "company_address2":"Ambal Nagar, Ramapuram, Chennai - 600 089",
        "gst_no":"","currency":"INR","date_format":"DD/MM/YYYY","tax_rate":0,"logo_b64":None,
        "accounts":["Cash","UPI","Bank Transfer"],
        "payment_instructions":"Bank: SBI, A/c no: 20001142967\nIFSC: SBIN0018229\nName: T.ArunPrasad, BE., MBA.\nGpay No: 9940147658",
        "next_invoice_no":1004,
      },
    }
    for k,v in D.items():
        if k not in st.session_state: st.session_state[k]=v
    st.session_state.customers=[
        {"name":c,"email":"","phone":"","address":""} if isinstance(c,str) else c
        for c in st.session_state.customers
    ]

init()
st.markdown(CSS,unsafe_allow_html=True)

# ── sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    s=st.session_state.settings
    lb=s.get("logo_b64")
    if lb:
        st.markdown(f'<div style="padding:14px 14px 6px"><img src="data:image/png;base64,{lb}" style="width:44px;height:44px;border-radius:9px;object-fit:cover;"></div>',unsafe_allow_html=True)
    st.markdown(f"""<div style="padding:{'6px' if lb else '18px'} 14px 14px">
      <div style="display:flex;align-items:center;gap:9px;margin-bottom:18px;">
        {'' if lb else '<div style="width:34px;height:34px;border-radius:8px;background:#4F46E5;display:flex;align-items:center;justify-content:center;"><span style="color:#fff;font-weight:800;font-size:11px;">AP</span></div>'}
        <div><div style="font-weight:700;font-size:13px;color:#111">{s.get("company_name","AP Tech Care")}</div>
        <div style="font-size:10px;color:#9CA3AF">Smart Tech Solutions</div></div>
      </div></div>""",unsafe_allow_html=True)
    cur=st.session_state.page
    st.markdown(f'<style>[data-testid="stSidebar"] [data-testid="stButton-nav_{cur}"]>button{{background:#EEF2FF!important;color:#4F46E5!important;font-weight:600!important;}}</style>',unsafe_allow_html=True)
    for pid,icon,lbl in [("home","🏠","Home"),("invoice","📄","Invoices"),("customers","👥","Customers"),("items","📦","Items"),("settings","⚙️","Settings")]:
        if st.button(f"{icon}  {lbl}",key=f"nav_{pid}",use_container_width=True): nav(pid)
    st.markdown("---")
    if st.button("🚪  Logout",key="nav_logout",use_container_width=True): st.rerun()

if st.session_state.page!="home":
    if st.button("← Home",key="gb"): nav("home")
    st.markdown("<div class='div'></div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════
def page_home():
    invs=st.session_state.invoices
    st.markdown('<p class="pt">Dashboard</p>',unsafe_allow_html=True)
    st.markdown('<p class="ps">AP Tech Care — Smart Tech Solutions</p>',unsafe_allow_html=True)
    paid=sum(i["amount"] for i in invs if i["status"]=="paid")
    pend=sum(i["amount"] for i in invs if i["status"] not in ["paid","cancelled"])
    ovd=len([i for i in invs if i["status"]=="overdue"])
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric("Total Invoices",len(invs))
    with c2: st.metric("Collected",f"₹{paid/1000:.1f}K")
    with c3: st.metric("Outstanding",f"₹{pend/1000:.1f}K")
    with c4: st.metric("Overdue",ovd)
    st.markdown("<div class='div'></div>",unsafe_allow_html=True)

    # Quick actions
    col_inv,col_cust,col_item=st.columns(3)
    with col_inv:
        if st.button("📄  New Invoice",type="primary",use_container_width=True):
            st.session_state.show_new_inv=True; nav("invoice")
    with col_cust:
        if st.button("👥  Add Customer",use_container_width=True):
            st.session_state.show_add_cust=True; nav("customers")
    with col_item:
        if st.button("📦  Add Item",use_container_width=True):
            st.session_state.show_add_item=True; nav("items")

    st.markdown("<div class='div'></div>",unsafe_allow_html=True)
    left,right=st.columns([2,1])
    with left:
        st.markdown("<p style='font-size:13px;font-weight:600;color:#111;margin-bottom:8px;'>Unpaid Invoices</p>",unsafe_allow_html=True)
        pending=[i for i in invs if i["status"] not in ["paid","cancelled"]]
        if not pending:
            st.markdown('<div class="card" style="text-align:center;padding:24px;color:#9CA3AF">✅ All paid!</div>',unsafe_allow_html=True)
        else:
            bm={"overdue":("#FEE2E2","#991B1B"),"sent":("#DBEAFE","#1E40AF"),"draft":("#F3F4F6","#6B7280"),"read":("#FEF9C3","#854D0E")}
            for inv in pending[:6]:
                bg,fg=bm.get(inv["status"],("#F3F4F6","#6B7280"))
                st.markdown(f'<div class="card" style="display:flex;justify-content:space-between;align-items:center;padding:12px 14px;margin-bottom:6px"><div><div style="font-weight:600;font-size:13px">{inv["customer"]}</div><div style="font-size:11px;color:#9CA3AF">{inv["id"]} • Due {fd(inv["due"])}</div></div><div style="text-align:right"><div style="font-weight:700">₹{inv["amount"]:,.0f}</div><span style="background:{bg};color:{fg};padding:1px 8px;border-radius:20px;font-size:11px;font-weight:600">{inv["status"].title()}</span></div></div>',unsafe_allow_html=True)
        if st.button("View All →",key="h_all"): nav("invoice")
    with right:
        st.markdown("<p style='font-size:13px;font-weight:600;color:#111;margin-bottom:8px;'>Quick Stats</p>",unsafe_allow_html=True)
        sc={"paid":"#166534","sent":"#1E40AF","overdue":"#991B1B","draft":"#6B7280","cancelled":"#991B1B"}
        sts={}
        for i in invs: sts[i["status"]]=sts.get(i["status"],0)+1
        for s2,c in sts.items():
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:8px 12px;background:#fff;border:1px solid #E5E7EB;border-radius:8px;margin-bottom:5px"><span style="font-size:13px">{s2.title()}</span><span style="font-weight:700;color:{sc.get(s2,"#6B7280")}">{c}</span></div>',unsafe_allow_html=True)
        st.markdown("<div class='div'></div>",unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:8px 12px;background:#EEF2FF;border-radius:8px;margin-bottom:5px"><span style="font-size:13px">👥 Customers</span><span style="font-weight:700;color:#4F46E5">{len(st.session_state.customers)}</span></div><div style="display:flex;justify-content:space-between;padding:8px 12px;background:#F0FDF4;border-radius:8px"><span style="font-size:13px">📦 Items</span><span style="font-weight:700;color:#166534">{len(st.session_state.items_db)}</span></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# INVOICES
# ══════════════════════════════════════════════════════════════════
def page_invoices():
    s=st.session_state.settings
    invs=st.session_state.invoices

    # ── Invoice action view ──────────────────────────────────────
    if st.session_state.get("selected_inv"):
        doc=st.session_state.selected_inv
        action=st.session_state.get("inv_action","preview")
        bm={"paid":("#DCFCE7","#166534"),"overdue":("#FEE2E2","#991B1B"),"sent":("#DBEAFE","#1E40AF"),"draft":("#F3F4F6","#6B7280"),"read":("#FEF9C3","#854D0E"),"cancelled":("#FEE2E2","#991B1B")}
        bg,fg=bm.get(doc["status"],("#F3F4F6","#6B7280"))

        # Header row
        cb,_,cid=st.columns([1,2,2])
        with cb:
            if st.button("← Back",key="inv_back",use_container_width=True):
                st.session_state.selected_inv=None; st.session_state.inv_action=None; st.rerun()
        with cid:
            st.markdown(f'<div style="text-align:right;padding-top:6px"><span style="font-weight:700;font-size:15px">{doc["id"]}</span> <span style="background:{bg};color:{fg};padding:2px 10px;border-radius:20px;font-size:12px;font-weight:600">{doc["status"].title()}</span></div>',unsafe_allow_html=True)

        # Action buttons
        a1,a2,a3,a4=st.columns(4)
        btn_style= lambda act: "primary" if action==act else "secondary"
        with a1:
            if st.button("👁 Preview",key="act_p",use_container_width=True,type=btn_style("preview")):
                st.session_state.inv_action="preview"; st.rerun()
        with a2:
            if st.button("📤 Send",key="act_s",use_container_width=True,type=btn_style("send")):
                st.session_state.inv_action="send"; st.rerun()
        with a3:
            if st.button("💰 Payment",key="act_pay",use_container_width=True,type=btn_style("pay")):
                st.session_state.inv_action="pay"; st.rerun()
        with a4:
            if st.button("✕ Cancel",key="act_can",use_container_width=True):
                st.session_state.inv_action="cancel"; st.rerun()
        st.markdown("<div class='div'></div>",unsafe_allow_html=True)

        html=inv_html(doc,s)
        sub=doc.get("subtotal",doc.get("amount",0)); tax=doc.get("tax",0); total=doc.get("amount",sub+tax)

        if action=="preview":
            st.markdown(html,unsafe_allow_html=True)

        elif action=="send":
            st.markdown("### 📤 Send Invoice")
            st.download_button("⬇️ Download as HTML (→ open in Chrome → Ctrl+P → Save as PDF)",
                data=html.encode(), file_name=f"{doc['id']}.html", mime="text/html",
                type="primary",use_container_width=True)
            st.markdown("---")
            phone=""
            for c in st.session_state.customers:
                if isinstance(c,dict) and c.get("name")==doc.get("customer"): phone=c.get("phone","").strip(); break
            phone_clean="91"+phone if phone and not phone.startswith("+") and not phone.startswith("91") else phone.replace("+","")
            msg=f"Dear {doc['customer']},\n\nYour Invoice *{doc['id']}* — *Rs.{total:,.2f}*\nDate: {fd(doc['date'])}  Due: {fd(doc['due'])}\n\n{s.get('payment_instructions','')}\n\nThank you!\n— {s.get('company_name','AP Tech Care')}"
            wa=f"https://wa.me/{phone_clean}?text={urllib.parse.quote(msg)}" if phone_clean else f"https://wa.me/?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{wa}" target="_blank"><button style="width:100%;padding:10px;background:#25D366;color:#fff;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;margin-top:4px">💬 Send on WhatsApp</button></a>',unsafe_allow_html=True)
            st.caption("Tip: Download → Open in Chrome → Ctrl+P → Save as PDF → attach that PDF in WhatsApp")

        elif action=="pay":
            st.markdown("### 💰 Record Payment")
            if doc["status"]=="paid":
                st.success(f"✅ Already paid on {fd(doc.get('paid_date',''))}")
            else:
                with st.form("pay_form"):
                    c1,c2=st.columns(2)
                    with c1: pd=st.date_input("Payment Date",value=date.today())
                    with c2: pm=st.selectbox("Method",["Cash","UPI / GPay","Bank Transfer","Cheque","Other"])
                    pn=st.text_input("Note (optional)")
                    sv,cl=st.columns(2)
                    with sv: ok=st.form_submit_button("✅ Mark as Paid",type="primary",use_container_width=True)
                    with cl: bk=st.form_submit_button("Cancel",use_container_width=True)
                    if ok:
                        for i,inv in enumerate(st.session_state.invoices):
                            if inv["id"]==doc["id"]:
                                st.session_state.invoices[i]["status"]="paid"
                                st.session_state.invoices[i]["paid_date"]=str(pd)
                                st.session_state.invoices[i]["pay_method"]=pm
                                st.session_state.selected_inv=st.session_state.invoices[i]
                                break
                        st.success(f"✅ Marked as Paid!"); st.session_state.inv_action="preview"; st.rerun()
                    if bk: st.session_state.inv_action="preview"; st.rerun()

        elif action=="cancel":
            st.warning(f"Cancel invoice **{doc['id']}** for **{doc['customer']}** (Rs.{total:,.2f})?")
            c1,c2=st.columns(2)
            with c1:
                if st.button("✅ Yes, Cancel",type="primary",use_container_width=True):
                    for i,inv in enumerate(st.session_state.invoices):
                        if inv["id"]==doc["id"]: st.session_state.invoices[i]["status"]="cancelled"; break
                    st.session_state.selected_inv=None; st.session_state.inv_action=None; st.rerun()
            with c2:
                if st.button("← Go Back",use_container_width=True): st.session_state.inv_action="preview"; st.rerun()
        return

    # ── New invoice form ─────────────────────────────────────────
    hc1,hc2=st.columns([3,1])
    with hc1:
        st.markdown('<p class="pt">📄 Invoices</p>',unsafe_allow_html=True)
        st.markdown(f'<p class="ps">{len(invs)} invoices</p>',unsafe_allow_html=True)
    with hc2:
        if st.button("➕ New Invoice",type="primary",use_container_width=True):
            st.session_state.show_new_inv=True; st.session_state.selected_inv=None; st.rerun()

    if st.session_state.get("show_new_inv"):
        st.markdown("---")
        cust_names=[c["name"] if isinstance(c,dict) else c for c in st.session_state.customers]
        with st.form("new_inv_form"):
            st.markdown("**Invoice Details**")
            r1c1,r1c2,r1c3=st.columns(3)
            with r1c1: customer=st.selectbox("Customer *",cust_names)
            with r1c2: inv_no=st.text_input("Invoice #",value=f"AP-{s.get('next_invoice_no',1001)}")
            with r1c3: inv_date=st.date_input("Date",value=date.today())
            r2c1,r2c2,r2c3=st.columns(3)
            with r2c1: due_date=st.date_input("Due Date",value=date.today()+timedelta(days=15))
            with r2c2: inv_status=st.selectbox("Status",["draft","sent","paid"])
            with r2c3: tax_rate=st.number_input("Tax %",min_value=0.0,max_value=100.0,value=float(s.get("tax_rate",0)),step=0.5)

            st.markdown("**Items**")
            n_rows=st.session_state.get("n_rows",1); line_items=[]
            inames=[i["name"] for i in st.session_state.items_db]
            for i in range(n_rows):
                ci1,ci2,ci3,ci4=st.columns([3,1,1,1])
                with ci1: iname=st.selectbox(f"Item {i+1}",["—"]+inames,key=f"in_{i}")
                with ci2: qty=st.number_input("Qty",min_value=1,value=1,key=f"q_{i}")
                with ci3:
                    dp=0
                    if iname!="—":
                        f2=next((x for x in st.session_state.items_db if x["name"]==iname),None)
                        if f2: dp=f2["price"]
                    price=st.number_input("Price",min_value=0,value=dp,key=f"p_{i}")
                with ci4: st.markdown(f"<div style='padding-top:26px;font-weight:700;color:#4F46E5;font-size:13px'>₹{qty*price:,}</div>",unsafe_allow_html=True)
                if iname!="—": line_items.append({"name":iname,"qty":qty,"price":price,"amount":qty*price})

            sub=sum(x["amount"] for x in line_items); tax=int(sub*tax_rate/100); total=sub+tax
            if tax>0:
                st.markdown(f'<div style="background:#f8f9fa;border-radius:8px;padding:10px 14px;margin:8px 0;text-align:right"><span style="color:#777;font-size:13px">Subtotal: ₹{sub:,}  |  Tax ({tax_rate}%): ₹{tax:,}  |  </span><span style="font-weight:800;font-size:15px;color:#4F46E5">Total: ₹{total:,}</span></div>',unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background:#f8f9fa;border-radius:8px;padding:10px 14px;margin:8px 0;text-align:right"><span style="font-weight:800;font-size:15px;color:#4F46E5">Total: ₹{total:,}</span></div>',unsafe_allow_html=True)

            fc1,fc2,fc3,fc4=st.columns([2,1,1,1])
            with fc1: save=st.form_submit_button("💾 Save Invoice",type="primary",use_container_width=True)
            with fc2: add_r=st.form_submit_button("➕ Add Row",use_container_width=True)
            with fc3: prev=st.form_submit_button("👁 Preview",use_container_width=True)
            with fc4: canc=st.form_submit_button("✕ Cancel",use_container_width=True)

            new_doc={"id":inv_no,"type":"invoice","customer":customer,"date":str(inv_date),
                     "due":str(due_date),"amount":total,"status":inv_status,
                     "items":line_items,"subtotal":sub,"tax":tax,"tax_rate":tax_rate}
            if save:
                st.session_state.invoices.insert(0,new_doc)
                s["next_invoice_no"]=s.get("next_invoice_no",1001)+1
                st.session_state.show_new_inv=False; st.session_state.n_rows=1
                st.success(f"✅ {inv_no} saved!"); st.rerun()
            if add_r: st.session_state.n_rows=n_rows+1; st.rerun()
            if prev:
                st.session_state.selected_inv=new_doc; st.session_state.inv_action="preview"; st.rerun()
            if canc: st.session_state.show_new_inv=False; st.session_state.n_rows=1; st.rerun()

    # ── Invoice list ─────────────────────────────────────────────
    tabs=st.tabs(["All","Draft","Sent","Paid","Overdue","Cancelled"])
    for tab,flt in zip(tabs,["all","draft","sent","paid","overdue","cancelled"]):
        with tab:
            fl=invs if flt=="all" else [d for d in invs if d["status"]==flt]
            srch=st.text_input("🔍",placeholder="Search customer or invoice #...",key=f"s_{flt}",label_visibility="collapsed")
            if srch: fl=[d for d in fl if srch.lower() in d["customer"].lower() or srch.lower() in d["id"].lower()]
            if not fl:
                st.markdown(f'<div class="card" style="text-align:center;padding:28px;color:#9CA3AF">No invoices</div>',unsafe_allow_html=True)
            else:
                bm={"paid":("#DCFCE7","#166534"),"overdue":("#FEE2E2","#991B1B"),"sent":("#DBEAFE","#1E40AF"),"draft":("#F3F4F6","#6B7280"),"read":("#FEF9C3","#854D0E"),"cancelled":("#FEE2E2","#991B1B")}
                for doc in fl:
                    bg2,fg2=bm.get(doc["status"],("#F3F4F6","#6B7280"))
                    lc1,lc2,lc3,lc4,lc5=st.columns([3,1,1,1,1])
                    with lc1: st.markdown(f'<div style="padding:6px 0"><div style="font-weight:600;font-size:14px">{doc["customer"]}</div><div style="font-size:11px;color:#9CA3AF">{doc["id"]} • {fd(doc["date"])}</div></div>',unsafe_allow_html=True)
                    with lc2: st.markdown(f'<div style="padding:6px 0;text-align:right"><div style="font-weight:700;font-size:13px">₹{doc["amount"]:,.0f}</div><span style="background:{bg2};color:{fg2};padding:1px 8px;border-radius:20px;font-size:11px;font-weight:600">{doc["status"].title()}</span></div>',unsafe_allow_html=True)
                    with lc3:
                        if st.button("👁",key=f"v_{flt}_{doc['id']}",use_container_width=True):
                            st.session_state.selected_inv=doc; st.session_state.inv_action="preview"; st.rerun()
                    with lc4:
                        if st.button("📤",key=f"snd_{flt}_{doc['id']}",use_container_width=True):
                            st.session_state.selected_inv=doc; st.session_state.inv_action="send"; st.rerun()
                    with lc5:
                        if st.button("💰",key=f"pay_{flt}_{doc['id']}",use_container_width=True):
                            st.session_state.selected_inv=doc; st.session_state.inv_action="pay"; st.rerun()
                    st.markdown("<hr style='margin:3px 0;border-color:#F3F4F6'>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CUSTOMERS
# ══════════════════════════════════════════════════════════════════
def page_customers():
    custs=st.session_state.customers
    st.markdown('<p class="pt">👥 Customers</p>',unsafe_allow_html=True)
    _,c2=st.columns([3,1])
    with c2:
        if st.button("➕ Add",type="primary",use_container_width=True):
            st.session_state.show_add_cust=True; st.session_state.edit_cust_idx=None
    srch=st.text_input("🔍",placeholder="Search...",label_visibility="collapsed",key="cs")
    fl=[c for c in custs if not srch or srch.lower() in c["name"].lower()]
    for cust in fl:
        ri=custs.index(cust); cc1,cc2,cc3=st.columns([4,1,1])
        with cc1:
            invs=[i for i in st.session_state.invoices if i["customer"]==cust["name"]]
            st.markdown(f'<div style="padding:5px 0"><div style="font-weight:600;font-size:14px">{cust["name"]}</div><div style="font-size:11px;color:#9CA3AF">{cust.get("phone","—")} • {cust.get("email","—")} • {len(invs)} invoices</div></div>',unsafe_allow_html=True)
        with cc2:
            if st.button("✏️",key=f"ec{ri}"): st.session_state.edit_cust_idx=ri; st.session_state.show_add_cust=False
        with cc3:
            if st.button("🗑️",key=f"dc{ri}"): custs.pop(ri); st.rerun()
        st.markdown("<hr style='margin:3px 0;border-color:#F3F4F6'>",unsafe_allow_html=True)

    ei=st.session_state.get("edit_cust_idx")
    if ei is not None and ei<len(custs):
        c=custs[ei]; st.markdown("---")
        with st.form("ecf"):
            st.markdown(f"**✏️ Edit — {c['name']}**")
            fc1,fc2=st.columns(2)
            with fc1: n=st.text_input("Name *",value=c.get("name","")); p=st.text_input("Phone",value=c.get("phone",""))
            with fc2: e=st.text_input("Email",value=c.get("email","")); a=st.text_input("Address",value=c.get("address",""))
            s1,s2=st.columns(2)
            with s1: sv=st.form_submit_button("💾 Save",type="primary",use_container_width=True)
            with s2: cl=st.form_submit_button("✕ Close",use_container_width=True)
            if sv and n: custs[ei]={"name":n,"email":e,"phone":p,"address":a}; st.session_state.edit_cust_idx=None; st.success("✅ Updated!"); st.rerun()
            if cl: st.session_state.edit_cust_idx=None; st.rerun()

    if st.session_state.get("show_add_cust"):
        st.markdown("---")
        with st.form("acf"):
            st.markdown("**➕ New Customer**")
            fc1,fc2=st.columns(2)
            with fc1: n=st.text_input("Name *"); p=st.text_input("Phone")
            with fc2: e=st.text_input("Email"); a=st.text_input("Address")
            s1,s2=st.columns(2)
            with s1: sv=st.form_submit_button("💾 Save Customer",type="primary",use_container_width=True)
            with s2: cl=st.form_submit_button("✕ Close",use_container_width=True)
            if sv and n: custs.append({"name":n,"email":e,"phone":p,"address":a}); st.session_state.show_add_cust=False; st.success(f"✅ '{n}' added!"); st.rerun()
            if cl: st.session_state.show_add_cust=False; st.rerun()

# ══════════════════════════════════════════════════════════════════
# ITEMS
# ══════════════════════════════════════════════════════════════════
def page_items():
    items=st.session_state.items_db
    st.markdown('<p class="pt">📦 Items</p>',unsafe_allow_html=True)
    _,c2=st.columns([3,1])
    with c2:
        if st.button("➕ Add",type="primary",use_container_width=True):
            st.session_state.show_add_item=True; st.session_state.edit_item_idx=None
    srch=st.text_input("🔍",placeholder="Search...",label_visibility="collapsed",key="is")
    fl=[i for i in items if not srch or srch.lower() in i["name"].lower()]
    for item in fl:
        ri=items.index(item); ic1,ic2,ic3,ic4=st.columns([3,1,1,1])
        with ic1: st.markdown(f'<div style="padding:5px 0"><div style="font-weight:600;font-size:14px">{item["name"]}</div><div style="font-size:11px;color:#9CA3AF">Code: {item.get("code","—")} • {item.get("unit","")}</div></div>',unsafe_allow_html=True)
        with ic2: st.markdown(f"<div style='padding-top:6px;font-weight:700;color:#166534;font-size:13px'>₹{item['price']:,}</div>",unsafe_allow_html=True)
        with ic3:
            if st.button("✏️",key=f"ei{ri}"): st.session_state.edit_item_idx=ri; st.session_state.show_add_item=False
        with ic4:
            if st.button("🗑️",key=f"di{ri}"): items.pop(ri); st.rerun()
        st.markdown("<hr style='margin:3px 0;border-color:#F3F4F6'>",unsafe_allow_html=True)

    ei2=st.session_state.get("edit_item_idx")
    if ei2 is not None and ei2<len(items):
        it=items[ei2]; st.markdown("---")
        with st.form("eif"):
            st.markdown(f"**✏️ Edit — {it['name']}**")
            ic1,ic2=st.columns(2)
            with ic1: n=st.text_input("Name *",value=it.get("name","")); pr=st.number_input("Price ₹",min_value=0,value=int(it.get("price",0)))
            with ic2: cd=st.text_input("Code",value=it.get("code","")); u=st.text_input("Unit",value=it.get("unit","per unit"))
            s1,s2=st.columns(2)
            with s1: sv=st.form_submit_button("💾 Save",type="primary",use_container_width=True)
            with s2: cl=st.form_submit_button("✕ Close",use_container_width=True)
            if sv and n: items[ei2]={"name":n,"code":cd,"price":pr,"unit":u,"desc":it.get("desc","")}; st.session_state.edit_item_idx=None; st.success("✅ Updated!"); st.rerun()
            if cl: st.session_state.edit_item_idx=None; st.rerun()

    if st.session_state.get("show_add_item"):
        st.markdown("---")
        with st.form("aif"):
            st.markdown("**➕ New Item**")
            ic1,ic2=st.columns(2)
            with ic1: n=st.text_input("Item Name *"); pr=st.number_input("Price ₹",min_value=0)
            with ic2: cd=st.text_input("Product Code"); u=st.text_input("Unit",value="per visit")
            s1,s2=st.columns(2)
            with s1: sv=st.form_submit_button("💾 Save Item",type="primary",use_container_width=True)
            with s2: cl=st.form_submit_button("✕ Close",use_container_width=True)
            if sv and n: items.append({"name":n,"code":cd,"price":pr,"unit":u,"desc":""}); st.session_state.show_add_item=False; st.success(f"✅ '{n}' added!"); st.rerun()
            if cl: st.session_state.show_add_item=False; st.rerun()

# ══════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════
def page_settings():
    st.markdown('<p class="pt">⚙️ Settings</p>',unsafe_allow_html=True)
    s=st.session_state.settings
    sec=st.radio("",["🏢 Company","💳 Payment","🏦 Accounts","🧾 Tax & Currency"],horizontal=True,label_visibility="collapsed")
    st.markdown("---")

    if sec=="🏢 Company":
        lf=st.file_uploader("Upload Logo",type=["png","jpg","jpeg"])
        if lf: s["logo_b64"]=base64.b64encode(lf.read()).decode(); st.success("✅ Logo saved!"); st.rerun()
        if s.get("logo_b64"):
            st.markdown(f'<img src="data:image/png;base64,{s["logo_b64"]}" style="height:60px;border-radius:8px;margin-bottom:10px">',unsafe_allow_html=True)
            if st.button("🗑️ Remove Logo"): s["logo_b64"]=None; st.rerun()
        c1,c2=st.columns(2)
        with c1:
            n=st.text_input("Company Name",value=s.get("company_name",""))
            p=st.text_input("Phone",value=s.get("company_phone",""))
            a1=st.text_input("Address Line 1",value=s.get("company_address1",""))
            a2=st.text_input("Address Line 2",value=s.get("company_address2",""))
        with c2:
            e=st.text_input("Email",value=s.get("company_email",""))
            g=st.text_input("GST No",value=s.get("gst_no",""))
        if st.button("💾 Save",type="primary"):
            s.update({"company_name":n,"company_phone":p,"company_email":e,"gst_no":g,"company_address1":a1,"company_address2":a2}); st.success("✅ Saved!"); st.rerun()

    elif sec=="💳 Payment":
        ins=st.text_area("Payment Instructions",value=s.get("payment_instructions",""),height=120)
        if st.button("💾 Save",type="primary"): s["payment_instructions"]=ins; st.success("✅ Saved!")

    elif sec=="🏦 Accounts":
        accs=s.get("accounts",["Cash","UPI","Bank Transfer"])
        for i,a in enumerate(accs):
            fc1,fc2=st.columns([5,1])
            with fc1: st.markdown(f'<div style="padding:10px 14px;background:#f8f9fa;border:1px solid #E5E7EB;border-radius:7px;font-weight:600">💰 {a}</div>',unsafe_allow_html=True)
            with fc2:
                if st.button("🗑️",key=f"da{i}"): accs.pop(i); s["accounts"]=accs; st.rerun()
        na=st.text_input("New Account")
        if st.button("➕ Add",type="primary"):
            if na: accs.append(na); s["accounts"]=accs; st.rerun()

    elif sec=="🧾 Tax & Currency":
        c1,c2=st.columns(2)
        with c1: tr=st.number_input("Default Tax %",min_value=0.0,max_value=100.0,value=float(s.get("tax_rate",0)),step=0.5)
        with c2: df=st.selectbox("Date Format",["DD/MM/YYYY","MM/DD/YYYY","YYYY/MM/DD"],index=["DD/MM/YYYY","MM/DD/YYYY","YYYY/MM/DD"].index(s.get("date_format","DD/MM/YYYY")))
        if st.button("💾 Save",type="primary"): s.update({"tax_rate":tr,"date_format":df}); st.success("✅ Saved!")

# ══════════════════════════════════════════════════════════════════
# ROUTING
# ══════════════════════════════════════════════════════════════════
p=st.session_state.page
if p=="home": page_home()
elif p=="invoice": page_invoices()
elif p=="customers": page_customers()
elif p=="items": page_items()
elif p=="settings": page_settings()
