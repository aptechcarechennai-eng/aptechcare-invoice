import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date, timedelta
import base64, urllib.parse, json
from supabase import create_client

st.set_page_config(page_title="AP Tech Care", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ── Supabase Setup ──────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def db_load(key, default=None):
    """Load data from Supabase"""
    try:
        supabase = get_supabase()
        result = supabase.table("ap_settings").select("value").eq("key", key).execute()
        if result.data and len(result.data) > 0:
            return json.loads(result.data[0]["value"])
        return default
    except Exception as e:
        st.error(f"❌ Load error for {key}: {e}")
        return default

def db_save(key, value):
    """Save data to Supabase"""
    try:
        supabase = get_supabase()
        data = {"key": key, "value": json.dumps(value, default=str)}
        existing = supabase.table("ap_settings").select("key").eq("key", key).execute()
        if existing.data and len(existing.data) > 0:
            supabase.table("ap_settings").update(data).eq("key", key).execute()
        else:
            supabase.table("ap_settings").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"❌ Save error for {key}: {e}")
        return False

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
@media(max-width:768px){.block-container{padding:1rem!important;}[data-testid="stSidebar"]{min-width:180px!important;width:180px!important;}}
</style>"""

# ── helpers ──────────────────────────────────────────────────────
def nav(p):
    st.session_state.page=p
    st.session_state.selected_inv=None
    st.session_state.inv_action=None
    st.rerun()

def fd(d):
    try: return datetime.strptime(str(d),"%Y-%m-%d").strftime("%d/%m/%Y")
    except: return str(d) if d else ""

def inv_html(doc, s, doc_label="Invoice"):
    items=doc.get("items",[])
    sub=doc.get("subtotal",doc.get("amount",0))
    tax=doc.get("tax",0)
    total=doc.get("amount",sub+tax)
    lb=s.get("logo_b64","")
    logo=f'<img src="data:image/png;base64,{lb}" style="max-height:80px;max-width:140px;object-fit:contain;">' if lb else ""
    rows=""
    for it in items:
        rows+=f"""<tr>
          <td style="padding:10px 12px;font-weight:600;border-bottom:1px solid #eee;">{it.get("name","")}</td>
          <td style="padding:10px 12px;text-align:center;border-bottom:1px solid #eee;">{it.get("qty",1)}</td>
          <td style="padding:10px 12px;text-align:right;border-bottom:1px solid #eee;">Rs.{it.get("price",0):,.2f}</td>
          <td style="padding:10px 12px;text-align:right;border-bottom:1px solid #eee;">Rs.{it.get("amount",0):,.2f}</td>
        </tr>"""
    if not rows:
        rows=f'<tr><td colspan="3" style="padding:12px;text-align:right;color:#777">Total</td><td style="padding:12px;text-align:right;font-weight:700">Rs.{total:,.2f}</td></tr>'
    tax_row=""
    if tax>0:
        tax_row=f'<tr><td style="padding:6px 12px;font-size:13px;color:#555;text-align:left;border-bottom:1px solid #eee;">Tax ({doc.get("tax_rate",0)}%)</td><td style="padding:6px 12px;font-size:13px;text-align:right;font-weight:600;border-bottom:1px solid #eee;">Rs.{tax:,.2f}</td></tr>'
    caddr=""; cphone=""
    for c in st.session_state.customers:
        if isinstance(c,dict) and c.get("name")==doc.get("customer"):
            caddr=c.get("address",""); cphone=c.get("phone",""); break
    a2=s.get("company_address2","")
    tagline=s.get("company_tagline","Smart Tech Solutions")
    owner=s.get("owner_name","")
    due_row=""
    if doc.get("due"):
        due_row=f'<tr><td style="padding:3px 8px;color:#555">Due</td><td style="padding:3px 8px;font-weight:700;text-align:right">{fd(doc["due"])}</td></tr>'
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
    {owner_line}
    <div class="co-tagline">{tagline}</div>
    <div class="co-info">{s.get("company_address1","")}<br>{a2}<br>📞 {s.get("company_phone","")}<br>✉ {s.get("company_email","")}</div>
  </div>
</div>
<div class="mid">
  <div class="bill-to">
    <h4>Bill To</h4>
    <div class="cn">{doc.get("customer","")}</div>
    <div class="ci">{caddr}<br>📞 {cphone}</div>
  </div>
  <div class="inv-meta"><table>
    <tr><td style="padding:3px 8px;color:#555">Invoice #</td><td style="padding:3px 8px;font-weight:700;text-align:right">{doc["id"]}</td></tr>
    <tr><td style="padding:3px 8px;color:#555">Date</td><td style="padding:3px 8px;font-weight:700;text-align:right">{fd(doc["date"])}</td></tr>
    {due_row}
  </table></div>
</div>
<table class="items"><thead><tr><th>Item</th><th>Qty</th><th>Price</th><th>Amount</th></tr></thead><tbody>{rows}</tbody></table>
<div class="bot">
  <div class="pi"><h4>Payment Instructions</h4><p>{s.get("payment_instructions","Bank transfer or UPI accepted.")}</p></div>
  <div class="tots">
    <table>{tots_rows}</table>
    <div class="amt-box"><div class="amt-label">Amount Due</div><div class="amt-val">Rs.{total:,.2f}</div></div>
  </div>
</div>
<div class="footer">Thank you for your business!</div>
</div></body></html>"""

# ── Initialize Session State ──────────────────────────────────────
if "initialized" not in st.session_state:
    st.session_state.page = "home"
    st.session_state.invoices = db_load("invoices", [])
    st.session_state.purchases = db_load("purchases", [])
    st.session_state.customers = db_load("customers", [])
    st.session_state.items_db = db_load("items", [])
    st.session_state.cashflow = db_load("cashflow", [])
    st.session_state.settings = db_load("settings", {
        "company_name": "AP Tech Care",
        "company_tagline": "Smart Tech Solutions",
        "owner_name": "T.Arunprasad, BE., MBA.,",
        "logo_b64": None,
        "company_phone": "",
        "company_email": "",
        "company_address1": "",
        "company_address2": "",
        "gst_no": "",
        "payment_instructions": "",
        "tax_rate": 0,
        "accounts": ["Cash", "UPI", "Bank Transfer"],
        "date_format": "DD/MM/YYYY"
    })
    st.session_state.initialized = True

st.markdown(CSS, unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    s = st.session_state.settings
    lb = s.get("logo_b64", "")
    if lb:
        st.markdown(f'<div style="text-align:center;margin-bottom:10px"><img src="data:image/png;base64,{lb}" style="max-height:70px;max-width:150px;object-fit:contain;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;margin-bottom:4px"><div style="font-size:17px;font-weight:800;color:#1a1a1a">{s.get("company_name","AP Tech Care")}</div><div style="font-size:11px;font-weight:600;color:#4F46E5;margin-bottom:2px">{s.get("company_tagline","Smart Tech Solutions")}</div><div style="font-size:11px;font-weight:600;color:#6B7280">{s.get("owner_name","")}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    pg = st.session_state.page
    if st.button("🏠 Home", key="nav_home"): nav("home")
    if st.button("📄 Invoice", key="nav_inv"): nav("invoice")
    if st.button("🛒 Purchase", key="nav_pur"): nav("purchase")
    if st.button("💰 Cashflow", key="nav_cash"): nav("cashflow")
    if st.button("📊 Reports", key="nav_rep"): nav("reports")
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    if st.button("👥 Customers", key="nav_cust"): nav("customers")
    if st.button("📦 Items", key="nav_item"): nav("items")
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    if st.button("⚙️ Settings", key="nav_set"): nav("settings")

# ══════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════
def page_home():
    st.markdown('<p class="pt">🏠 Dashboard</p><p class="ps">Overview of your business</p>', unsafe_allow_html=True)
    inv = st.session_state.invoices
    pur = st.session_state.purchases
    cf = st.session_state.cashflow
    
    tot_inv = sum(d.get("amount", 0) for d in inv)
    tot_pur = sum(d.get("amount", 0) for d in pur)
    tot_in = sum(t.get("amount", 0) for t in cf if t.get("type") == "in")
    tot_out = sum(t.get("amount", 0) for t in cf if t.get("type") == "out")
    bal = tot_in - tot_out
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💵 Total Invoices", f"₹{tot_inv:,.0f}")
    c2.metric("🛒 Total Purchases", f"₹{tot_pur:,.0f}")
    c3.metric("💰 Cash In", f"₹{tot_in:,.0f}")
    c4.metric("💸 Cash Out", f"₹{tot_out:,.0f}")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<p style="font-weight:600;font-size:15px;margin-bottom:8px">📄 Recent Invoices</p>', unsafe_allow_html=True)
        recent = sorted(inv, key=lambda x: x.get("date", ""), reverse=True)[:5]
        if recent:
            for r in recent:
                st.markdown(f'<div style="padding:8px 12px;background:#fff;border:1px solid #E5E7EB;border-radius:6px;margin-bottom:6px"><div style="font-weight:600;font-size:13px">{r["id"]}</div><div style="font-size:11px;color:#9CA3AF">{r.get("customer","")} • ₹{r.get("amount",0):,}</div></div>', unsafe_allow_html=True)
        else:
            st.info("No invoices yet")
    
    with c2:
        st.markdown('<p style="font-weight:600;font-size:15px;margin-bottom:8px">💰 Cashflow Balance</p>', unsafe_allow_html=True)
        st.metric("Balance", f"₹{bal:,.0f}", delta=f"₹{tot_in-tot_out:,.0f}")

# ══════════════════════════════════════════════════════════════════
# DOCUMENTS (INVOICE / PURCHASE)
# ══════════════════════════════════════════════════════════════════
def page_documents(dtype):
    docs = st.session_state.invoices if dtype == "invoice" else st.session_state.purchases
    label = "Invoice" if dtype == "invoice" else "Purchase"
    icon = "📄" if dtype == "invoice" else "🛒"
    
    st.markdown(f'<p class="pt">{icon} {label}s</p>', unsafe_allow_html=True)
    
    _, c2 = st.columns([3, 1])
    with c2:
        if st.button(f"➕ New {label}", type="primary", use_container_width=True, key=f"new_{dtype}"):
            st.session_state.selected_inv = None
            st.session_state.inv_action = "create"
    
    act = st.session_state.get("inv_action")
    sel = st.session_state.get("selected_inv")
    
    if act == "create" or (act == "edit" and sel is not None):
        st.markdown("---")
        is_edit = (act == "edit" and sel is not None)
        doc = docs[sel] if is_edit else {}
        
        st.markdown(f"**{'✏️ Edit' if is_edit else '➕ New'} {label}**")
        
        with st.form(f"doc_form_{dtype}"):
            c1, c2 = st.columns(2)
            with c1:
                doc_id = st.text_input(f"{label} # *", value=doc.get("id", f"AP-{len(docs)+1001}"))
                
                # Smart customer search with inline add
                custs = st.session_state.customers
                cust_names = [c["name"] for c in custs if isinstance(c, dict)]
                
                search = st.text_input("🔍 Search Customer", value=doc.get("customer", ""), key=f"cust_search_{dtype}")
                matches = [n for n in cust_names if search.lower() in n.lower()] if search else cust_names
                
                if matches:
                    cust = st.selectbox("Select Customer *", [""] + matches, index=0 if not doc.get("customer") else (matches.index(doc.get("customer")) + 1 if doc.get("customer") in matches else 0), key=f"cust_sel_{dtype}")
                else:
                    cust = ""
                    if search:
                        st.info(f"No match for '{search}'")
                        if st.form_submit_button(f"➕ Add '{search}' as new customer", key=f"quick_add_{dtype}"):
                            custs.append({"name": search, "email": "", "phone": "", "address": ""})
                            db_save("customers", custs)
                            st.success(f"✅ '{search}' added!")
                            st.rerun()
                
                dt = st.date_input("Date *", value=datetime.strptime(doc.get("date", str(date.today())), "%Y-%m-%d") if doc.get("date") else date.today(), key=f"dt_{dtype}")
            
            with c2:
                due = st.date_input("Due Date", value=datetime.strptime(doc.get("due", ""), "%Y-%m-%d") if doc.get("due") else None, key=f"due_{dtype}")
                tax_en = st.checkbox("Enable Tax", value=doc.get("tax", 0) > 0, key=f"tax_en_{dtype}")
                tax_rate = st.number_input("Tax %", min_value=0.0, max_value=100.0, value=float(doc.get("tax_rate", st.session_state.settings.get("tax_rate", 0))), step=0.5, key=f"tax_rate_{dtype}") if tax_en else 0
            
            st.markdown("**Items**")
            items_list = doc.get("items", [{"name": "", "qty": 1, "price": 0, "amount": 0}])
            
            if "temp_items" not in st.session_state:
                st.session_state.temp_items = items_list
            
            for i, it in enumerate(st.session_state.temp_items):
                ic1, ic2, ic3, ic4, ic5 = st.columns([3, 1, 1, 1, 0.5])
                with ic1:
                    item_db = st.session_state.items_db
                    item_names = [itm["name"] for itm in item_db if isinstance(itm, dict)]
                    sel_item = st.selectbox(f"Item {i+1}", [""] + item_names, index=0, key=f"it_sel_{dtype}_{i}")
                    if sel_item:
                        for itm in item_db:
                            if itm["name"] == sel_item:
                                st.session_state.temp_items[i]["name"] = sel_item
                                st.session_state.temp_items[i]["price"] = itm.get("price", 0)
                    else:
                        st.session_state.temp_items[i]["name"] = st.text_input(f"Custom", value=it.get("name", ""), key=f"it_name_{dtype}_{i}", label_visibility="collapsed")
                
                with ic2:
                    st.session_state.temp_items[i]["qty"] = st.number_input("Qty", min_value=0, value=int(it.get("qty", 1)), key=f"it_qty_{dtype}_{i}", label_visibility="collapsed")
                with ic3:
                    st.session_state.temp_items[i]["price"] = st.number_input("Price", min_value=0, value=int(it.get("price", 0)), key=f"it_price_{dtype}_{i}", label_visibility="collapsed")
                with ic4:
                    amt = st.session_state.temp_items[i]["qty"] * st.session_state.temp_items[i]["price"]
                    st.session_state.temp_items[i]["amount"] = amt
                    st.markdown(f"<div style='padding-top:6px;font-weight:700;font-size:13px'>₹{amt:,}</div>", unsafe_allow_html=True)
                with ic5:
                    if len(st.session_state.temp_items) > 1:
                        if st.form_submit_button("🗑️", key=f"del_{dtype}_{i}"):
                            st.session_state.temp_items.pop(i)
                            st.rerun()
            
            if st.form_submit_button("➕ Add Item Row"):
                st.session_state.temp_items.append({"name": "", "qty": 1, "price": 0, "amount": 0})
                st.rerun()
            
            sub = sum(it["amount"] for it in st.session_state.temp_items)
            tax = (sub * tax_rate / 100) if tax_en else 0
            total = sub + tax
            
            st.markdown(f"<div style='text-align:right;padding:10px 0'><div style='font-size:13px;color:#666'>Subtotal: ₹{sub:,.2f}</div><div style='font-size:13px;color:#666'>Tax: ₹{tax:,.2f}</div><div style='font-size:16px;font-weight:700'>Total: ₹{total:,.2f}</div></div>", unsafe_allow_html=True)
            
            s1, s2, s3 = st.columns(3)
            with s1:
                save_btn = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
            with s2:
                preview_btn = st.form_submit_button("👁️ Preview", use_container_width=True)
            with s3:
                close_btn = st.form_submit_button("✕ Close", use_container_width=True)
            
            if save_btn and doc_id and cust:
                new_doc = {
                    "id": doc_id,
                    "customer": cust,
                    "date": str(dt),
                    "due": str(due) if due else "",
                    "items": [it for it in st.session_state.temp_items if it["name"]],
                    "subtotal": sub,
                    "tax": tax,
                    "tax_rate": tax_rate,
                    "amount": total
                }
                
                if is_edit:
                    docs[sel] = new_doc
                else:
                    docs.append(new_doc)
                
                # SAVE TO DATABASE
                db_save("invoices" if dtype == "invoice" else "purchases", docs)
                
                st.session_state.inv_action = None
                st.session_state.temp_items = []
                st.success(f"✅ {label} saved!")
                st.rerun()
            
            if preview_btn and doc_id and cust:
                preview_doc = {
                    "id": doc_id,
                    "customer": cust,
                    "date": str(dt),
                    "due": str(due) if due else "",
                    "items": [it for it in st.session_state.temp_items if it["name"]],
                    "subtotal": sub,
                    "tax": tax,
                    "tax_rate": tax_rate,
                    "amount": total
                }
                html = inv_html(preview_doc, st.session_state.settings, label)
                components.html(html, height=800, scrolling=True)
            
            if close_btn:
                st.session_state.inv_action = None
                st.session_state.temp_items = []
                st.rerun()
    
    else:
        # List view
        srch = st.text_input("🔍", placeholder=f"Search {label.lower()}s...", label_visibility="collapsed", key=f"srch_{dtype}")
        fl = [d for d in docs if not srch or srch.lower() in d.get("id", "").lower() or srch.lower() in d.get("customer", "").lower()]
        
        for d in reversed(fl):
            idx = docs.index(d)
            c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
            with c1:
                st.markdown(f'<div style="padding:5px 0"><div style="font-weight:700;font-size:14px">{d["id"]}</div><div style="font-size:11px;color:#9CA3AF">{d.get("customer","")} • {fd(d.get("date",""))}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div style='padding-top:6px;font-weight:700;font-size:14px;color:#059669'>₹{d.get('amount',0):,}</div>", unsafe_allow_html=True)
            with c3:
                if st.button("✏️", key=f"e_{dtype}_{idx}"):
                    st.session_state.selected_inv = idx
                    st.session_state.inv_action = "edit"
                    st.session_state.temp_items = d.get("items", [])
                    st.rerun()
            with c4:
                if st.button("🗑️", key=f"d_{dtype}_{idx}"):
                    if st.session_state.get(f"confirm_del_{idx}"):
                        docs.pop(idx)
                        db_save("invoices" if dtype == "invoice" else "purchases", docs)
                        st.session_state[f"confirm_del_{idx}"] = False
                        st.rerun()
                    else:
                        st.session_state[f"confirm_del_{idx}"] = True
                        st.warning("⚠️ Click again to confirm delete")
                        st.rerun()
            
            st.markdown("<hr style='margin:3px 0;border-color:#F3F4F6'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CASHFLOW
# ══════════════════════════════════════════════════════════════════
def page_cashflow():
    st.markdown('<p class="pt">💰 Cashflow</p>', unsafe_allow_html=True)
    cf = st.session_state.cashflow
    
    _, c2 = st.columns([3, 1])
    with c2:
        if st.button("➕ Add", type="primary", use_container_width=True):
            st.session_state.show_cf_form = True
    
    if st.session_state.get("show_cf_form"):
        st.markdown("---")
        with st.form("cf_form"):
            st.markdown("**➕ New Transaction**")
            c1, c2 = st.columns(2)
            with c1:
                typ = st.selectbox("Type *", ["in", "out"])
                amt = st.number_input("Amount ₹ *", min_value=0)
                dt = st.date_input("Date *", value=date.today())
            with c2:
                acc = st.selectbox("Account", st.session_state.settings.get("accounts", ["Cash", "UPI", "Bank Transfer"]))
                cat = st.text_input("Category")
                note = st.text_area("Notes", height=60)
            
            s1, s2 = st.columns(2)
            with s1:
                save = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
            with s2:
                close = st.form_submit_button("✕ Close", use_container_width=True)
            
            if save and amt > 0:
                cf.append({
                    "type": typ,
                    "amount": amt,
                    "date": str(dt),
                    "account": acc,
                    "category": cat,
                    "notes": note
                })
                db_save("cashflow", cf)
                st.session_state.show_cf_form = False
                st.success("✅ Transaction saved!")
                st.rerun()
            
            if close:
                st.session_state.show_cf_form = False
                st.rerun()
    
    tot_in = sum(t.get("amount", 0) for t in cf if t.get("type") == "in")
    tot_out = sum(t.get("amount", 0) for t in cf if t.get("type") == "out")
    bal = tot_in - tot_out
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💵 Total In", f"₹{tot_in:,.0f}")
    c2.metric("💸 Total Out", f"₹{tot_out:,.0f}")
    c3.metric("💰 Balance", f"₹{bal:,.0f}")
    
    st.markdown("---")
    srch = st.text_input("🔍", placeholder="Search transactions...", label_visibility="collapsed")
    fl = [t for t in cf if not srch or srch.lower() in t.get("category", "").lower() or srch.lower() in t.get("notes", "").lower()]
    
    for t in reversed(fl):
        idx = cf.index(t)
        c1, c2, c3 = st.columns([3, 1, 0.5])
        with c1:
            icon = "📥" if t["type"] == "in" else "📤"
            st.markdown(f'<div style="padding:5px 0"><div style="font-weight:600;font-size:13px">{icon} {t.get("category","")} • {t.get("account","")}</div><div style="font-size:11px;color:#9CA3AF">{fd(t.get("date",""))} • {t.get("notes","")}</div></div>', unsafe_allow_html=True)
        with c2:
            color = "#059669" if t["type"] == "in" else "#DC2626"
            st.markdown(f"<div style='padding-top:6px;font-weight:700;font-size:14px;color:{color}'>₹{t.get('amount',0):,}</div>", unsafe_allow_html=True)
        with c3:
            if st.button("🗑️", key=f"dcf{idx}"):
                cf.pop(idx)
                db_save("cashflow", cf)
                st.rerun()
        st.markdown("<hr style='margin:3px 0;border-color:#F3F4F6'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════════
def page_reports():
    st.markdown('<p class="pt">📊 Reports</p>', unsafe_allow_html=True)
    
    inv = st.session_state.invoices
    pur = st.session_state.purchases
    cf = st.session_state.cashflow
    
    tab1, tab2 = st.tabs(["Monthly Revenue", "Summary"])
    
    with tab1:
        by_month = {}
        for d in inv:
            try:
                m = datetime.strptime(d.get("date", ""), "%Y-%m-%d").strftime("%Y-%m")
                by_month[m] = by_month.get(m, 0) + d.get("amount", 0)
            except:
                pass
        
        if by_month:
            months = sorted(by_month.keys())
            amounts = [by_month[m] for m in months]
            
            st.markdown("**📈 Monthly Revenue Chart**")
            for m, a in zip(months, amounts):
                st.markdown(f'<div style="margin-bottom:8px"><div style="font-size:12px;color:#666">{m}</div><div style="background:#4F46E5;height:20px;border-radius:4px;width:{min(100, a/max(amounts)*100) if max(amounts) > 0 else 0}%"></div><div style="font-size:14px;font-weight:700;margin-top:2px">₹{a:,.0f}</div></div>', unsafe_allow_html=True)
        else:
            st.info("No data yet")
    
    with tab2:
        tot_inv = sum(d.get("amount", 0) for d in inv)
        tot_pur = sum(d.get("amount", 0) for d in pur)
        tot_in = sum(t.get("amount", 0) for t in cf if t.get("type") == "in")
        tot_out = sum(t.get("amount", 0) for t in cf if t.get("type") == "out")
        
        st.markdown("**📊 Business Summary**")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Total Invoices", f"₹{tot_inv:,.0f}")
            st.metric("Cash In", f"₹{tot_in:,.0f}")
        with c2:
            st.metric("Total Purchases", f"₹{tot_pur:,.0f}")
            st.metric("Cash Out", f"₹{tot_out:,.0f}")
        
        st.metric("Net Profit/Loss", f"₹{tot_inv - tot_pur:,.0f}")

# ══════════════════════════════════════════════════════════════════
# CUSTOMERS
# ══════════════════════════════════════════════════════════════════
def page_customers():
    custs = st.session_state.customers
    st.markdown('<p class="pt">👥 Customers</p>', unsafe_allow_html=True)
    
    _, c2 = st.columns([3, 1])
    with c2:
        if st.button("➕ Add", type="primary", use_container_width=True):
            st.session_state.show_add_cust = True
            st.session_state.edit_cust_idx = None
    
    srch = st.text_input("🔍", placeholder="Search customers...", label_visibility="collapsed", key="csrch")
    fl = [c for c in custs if not srch or srch.lower() in c.get("name", "").lower()]
    
    for c in fl:
        ri = custs.index(c)
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            st.markdown(f'<div style="padding:5px 0"><div style="font-weight:600;font-size:14px">{c.get("name","")}</div><div style="font-size:11px;color:#9CA3AF">📞 {c.get("phone","")} • ✉ {c.get("email","")}</div></div>', unsafe_allow_html=True)
        with c2:
            if st.button("✏️", key=f"ec{ri}"):
                st.session_state.edit_cust_idx = ri
                st.session_state.show_add_cust = False
        with c3:
            if st.button("🗑️", key=f"dc{ri}"):
                custs.pop(ri)
                db_save("customers", custs)
                st.rerun()
        st.markdown("<hr style='margin:3px 0;border-color:#F3F4F6'>", unsafe_allow_html=True)
    
    ec = st.session_state.get("edit_cust_idx")
    if ec is not None and ec < len(custs):
        cu = custs[ec]
        st.markdown("---")
        with st.form("ecf"):
            st.markdown(f"**✏️ Edit — {cu['name']}**")
            c1, c2 = st.columns(2)
            with c1:
                an = st.text_input("Name *", value=cu.get("name", ""))
                ap2 = st.text_input("Phone", value=cu.get("phone", ""))
            with c2:
                ae = st.text_input("Email", value=cu.get("email", ""))
                aa = st.text_area("Address", value=cu.get("address", ""), height=60)
            s1, s2 = st.columns(2)
            with s1:
                esv = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
            with s2:
                ecl = st.form_submit_button("✕ Close", use_container_width=True)
            if esv and an:
                custs[ec] = {"name": an, "email": ae, "phone": ap2, "address": aa}
                db_save("customers", custs)
                st.session_state.edit_cust_idx = None
                st.success("✅ Updated!")
                st.rerun()
            if ecl:
                st.session_state.edit_cust_idx = None
                st.rerun()
    
    if st.session_state.get("show_add_cust"):
        st.markdown("---")
        with st.form("acf"):
            st.markdown("**➕ New Customer**")
            c1, c2 = st.columns(2)
            with c1:
                an = st.text_input("Name *")
                ap2 = st.text_input("Phone")
            with c2:
                ae = st.text_input("Email")
                aa = st.text_area("Address", height=60)
            s1, s2 = st.columns(2)
            with s1:
                asv = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
            with s2:
                acl = st.form_submit_button("✕ Close", use_container_width=True)
            if asv and an:
                custs.append({"name": an, "email": ae, "phone": ap2, "address": aa})
                db_save("customers", custs)
                st.session_state.show_add_cust = False
                st.success(f"✅ '{an}' added!")
                st.rerun()
            if acl:
                st.session_state.show_add_cust = False
                st.rerun()

# ══════════════════════════════════════════════════════════════════
# ITEMS
# ══════════════════════════════════════════════════════════════════
def page_items():
    items = st.session_state.items_db
    st.markdown('<p class="pt">📦 Items</p>', unsafe_allow_html=True)
    
    _, c2 = st.columns([3, 1])
    with c2:
        if st.button("➕ Add", type="primary", use_container_width=True, key="item_add_btn"):
            st.session_state.show_add_item = True
            st.session_state.edit_item_idx = None
    
    srch = st.text_input("🔍", placeholder="Search items...", label_visibility="collapsed", key="isrch")
    fl = [i for i in items if not srch or srch.lower() in i["name"].lower()]
    
    for item in fl:
        ri = items.index(item)
        ic1, ic2, ic3, ic4 = st.columns([3, 1, 1, 1])
        with ic1:
            st.markdown(f'<div style="padding:5px 0"><div style="font-weight:600;font-size:14px">{item["name"]}</div><div style="font-size:11px;color:#9CA3AF">Code: {item.get("code","—")} • {item.get("unit","")}</div></div>', unsafe_allow_html=True)
        with ic2:
            st.markdown(f"<div style='padding-top:6px;font-weight:700;color:#166534;font-size:13px'>₹{item['price']:,}</div>", unsafe_allow_html=True)
        with ic3:
            if st.button("✏️", key=f"ei{ri}"):
                st.session_state.edit_item_idx = ri
                st.session_state.show_add_item = False
        with ic4:
            if st.button("🗑️", key=f"di{ri}"):
                items.pop(ri)
                db_save("items", items)
                st.rerun()
        st.markdown("<hr style='margin:3px 0;border-color:#F3F4F6'>", unsafe_allow_html=True)
    
    ei2 = st.session_state.get("edit_item_idx")
    if ei2 is not None and ei2 < len(items):
        it = items[ei2]
        st.markdown("---")
        with st.form("eif"):
            st.markdown(f"**✏️ Edit — {it['name']}**")
            ic1, ic2 = st.columns(2)
            with ic1:
                n = st.text_input("Name *", value=it.get("name", ""))
                pr = st.number_input("Price ₹", min_value=0, value=int(it.get("price", 0)))
            with ic2:
                cd = st.text_input("Code", value=it.get("code", ""))
                u = st.text_input("Unit", value=it.get("unit", "per unit"))
            s1, s2 = st.columns(2)
            with s1:
                isv = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
            with s2:
                icl = st.form_submit_button("✕ Close", use_container_width=True)
            if isv and n:
                items[ei2] = {"name": n, "code": cd, "price": pr, "unit": u, "desc": ""}
                db_save("items", items)
                st.session_state.edit_item_idx = None
                st.success("✅ Updated!")
                st.rerun()
            if icl:
                st.session_state.edit_item_idx = None
                st.rerun()
    
    if st.session_state.get("show_add_item"):
        st.markdown("---")
        with st.form("aif"):
            st.markdown("**➕ New Item**")
            ic1, ic2 = st.columns(2)
            with ic1:
                n = st.text_input("Item Name *")
                pr = st.number_input("Price ₹", min_value=0)
            with ic2:
                cd = st.text_input("Code")
                u = st.text_input("Unit", value="per visit")
            s1, s2 = st.columns(2)
            with s1:
                aIsv = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
            with s2:
                aIcl = st.form_submit_button("✕ Close", use_container_width=True)
            if aIsv and n:
                items.append({"name": n, "code": cd, "price": pr, "unit": u, "desc": ""})
                db_save("items", items)
                st.session_state.show_add_item = False
                st.success(f"✅ '{n}' added!")
                st.rerun()
            if aIcl:
                st.session_state.show_add_item = False
                st.rerun()

# ══════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════
def page_settings():
    st.markdown('<p class="pt">⚙️ Settings</p>', unsafe_allow_html=True)
    s = st.session_state.settings
    sec = st.radio("", ["🏢 Company", "💳 Payment", "🏦 Accounts", "🧾 Tax & Currency"], horizontal=True, label_visibility="collapsed")
    st.markdown("---")
    
    if sec == "🏢 Company":
        lf = st.file_uploader("Upload Logo", type=["png", "jpg", "jpeg"])
        if lf:
            s["logo_b64"] = base64.b64encode(lf.read()).decode()
            db_save("settings", s)
            st.success("✅ Logo saved!")
            st.rerun()
        if s.get("logo_b64"):
            st.markdown(f'<img src="data:image/png;base64,{s["logo_b64"]}" style="height:60px;border-radius:8px;margin-bottom:10px">', unsafe_allow_html=True)
            if st.button("🗑️ Remove Logo"):
                s["logo_b64"] = None
                db_save("settings", s)
                st.rerun()
        c1, c2 = st.columns(2)
        with c1:
            sn = st.text_input("Company Name", value=s.get("company_name", ""))
            st_line = st.text_input("Tagline", value=s.get("company_tagline", "Smart Tech Solutions"))
            sown = st.text_input("Owner Name", value=s.get("owner_name", ""))
            sp = st.text_input("Phone", value=s.get("company_phone", ""))
            sa1 = st.text_input("Address Line 1", value=s.get("company_address1", ""))
            sa2 = st.text_input("Address Line 2", value=s.get("company_address2", ""))
        with c2:
            se = st.text_input("Email", value=s.get("company_email", ""))
            sg = st.text_input("GST No", value=s.get("gst_no", ""))
        if st.button("💾 Save Company", type="primary"):
            s.update({"company_name": sn, "company_tagline": st_line, "owner_name": sown, "company_phone": sp, "company_email": se, "gst_no": sg, "company_address1": sa1, "company_address2": sa2})
            db_save("settings", s)
            st.success("✅ Saved!")
            st.rerun()
    
    elif sec == "💳 Payment":
        ins = st.text_area("Payment Instructions", value=s.get("payment_instructions", ""), height=120)
        if st.button("💾 Save", type="primary"):
            s["payment_instructions"] = ins
            db_save("settings", s)
            st.success("✅ Saved!")
    
    elif sec == "🏦 Accounts":
        accs = s.get("accounts", ["Cash", "UPI", "Bank Transfer"])
        for i, a in enumerate(accs):
            rc1, rc2 = st.columns([5, 1])
            with rc1:
                st.markdown(f'<div style="padding:10px 14px;background:#f8f9fa;border:1px solid #E5E7EB;border-radius:7px;font-weight:600">💰 {a}</div>', unsafe_allow_html=True)
            with rc2:
                if st.button("🗑️", key=f"da{i}"):
                    accs.pop(i)
                    s["accounts"] = accs
                    db_save("settings", s)
                    st.rerun()
        na = st.text_input("New Account Name")
        if st.button("➕ Add", type="primary"):
            if na:
                accs.append(na)
                s["accounts"] = accs
                db_save("settings", s)
                st.rerun()
    
    elif sec == "🧾 Tax & Currency":
        c1, c2 = st.columns(2)
        with c1:
            tr = st.number_input("Default Tax %", min_value=0.0, max_value=100.0, value=float(s.get("tax_rate", 0)), step=0.5)
        with c2:
            df2 = st.selectbox("Date Format", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY/MM/DD"], index=["DD/MM/YYYY", "MM/DD/YYYY", "YYYY/MM/DD"].index(s.get("date_format", "DD/MM/YYYY")))
        if st.button("💾 Save", type="primary"):
            s.update({"tax_rate": tr, "date_format": df2})
            db_save("settings", s)
            st.success("✅ Saved!")

# ══════════════════════════════════════════════════════════════════
# ROUTING
# ══════════════════════════════════════════════════════════════════
pg = st.session_state.page
if pg == "home":
    page_home()
elif pg == "invoice":
    page_documents("invoice")
elif pg == "purchase":
    page_documents("purchase")
elif pg == "cashflow":
    page_cashflow()
elif pg == "reports":
    page_reports()
elif pg == "customers":
    page_customers()
elif pg == "items":
    page_items()
elif pg == "settings":
    page_settings()
