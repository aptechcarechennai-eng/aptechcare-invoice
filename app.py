import streamlit as st
import json
import base64
from datetime import date, timedelta
from supabase import create_client, Client

# ── Page Config (MUST be first) ───────────────────────────────────────────────
st.set_page_config(
    page_title="AP Tech Care Invoice",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Supabase ──────────────────────────────────────────────────────────────────
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

sb = init_supabase()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  #MainMenu, footer, header { display: none !important; }
  .stDeployButton { display: none !important; }
  .main .block-container { padding: 1rem !important; max-width: 900px; }
  .stButton > button { border-radius: 10px !important; font-weight: 600 !important; }
  @media (max-width: 768px) {
    .main .block-container { padding: 0.4rem !important; }
  }
</style>
""", unsafe_allow_html=True)

# ── DB: Settings ──────────────────────────────────────────────────────────────
def db_get_settings():
    try:
        res = sb.table("ap_settings").select("*").execute()
        return {r["key"]: r["value"] for r in (res.data or [])}
    except:
        return {}

def db_save_setting(key, value):
    try:
        existing = sb.table("ap_settings").select("id").eq("key", key).execute()
        if existing.data:
            sb.table("ap_settings").update({"value": value}).eq("key", key).execute()
        else:
            sb.table("ap_settings").insert({"key": key, "value": value}).execute()
    except Exception as e:
        st.error(f"Settings error: {e}")

# ── DB: Invoices ──────────────────────────────────────────────────────────────
def db_next_inv_no():
    try:
        res = sb.table("ap_invoices").select("invoice_no").order("id", desc=True).limit(1).execute()
        if res.data:
            last_no = res.data[0]["invoice_no"]  # e.g. AP-1001
            num = int(last_no.split("-")[1]) + 1
            return f"AP-{num}"
        return "AP-1001"
    except:
        return "AP-1001"

def db_save_invoice(data):
    try:
        res = sb.table("ap_invoices").insert(data).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        st.error(f"Save invoice error: {e}")
        return None

def db_get_invoices():
    try:
        res = sb.table("ap_invoices").select("*").order("id", desc=True).execute()
        return res.data or []
    except:
        return []

def db_get_invoice(inv_id):
    try:
        res = sb.table("ap_invoices").select("*").eq("id", inv_id).execute()
        return res.data[0] if res.data else None
    except:
        return None

def db_update_status(inv_id, status):
    try:
        sb.table("ap_invoices").update({"payment_status": status}).eq("id", inv_id).execute()
        return True
    except:
        return False

def db_delete_invoice(inv_id):
    try:
        sb.table("ap_invoices").delete().eq("id", inv_id).execute()
        return True
    except Exception as e:
        st.error(f"Delete error: {e}")
        return False

# ── HTML Invoice Generator ────────────────────────────────────────────────────
def make_invoice_html(inv, settings):
    co   = settings.get("company_name", "AP Tech Care")
    tag  = settings.get("tagline", "Smart Tech Solutions")
    own  = settings.get("owner_name", "T.Arunprasad, BE., MBA.,")
    addr = settings.get("address", "1/4A, Kamaraj Cross Street, Ambal Nagar, Ramapuram, Chennai, Tamilnadu 600 089")
    ph   = settings.get("phone", "9940147658")
    em   = settings.get("email", "aptechcare.chennai@gmail.com")
    bank = settings.get("bank_name", "SBI")
    acc  = settings.get("acc_no", "20001142967")
    ifsc = settings.get("ifsc", "SBIN0018229")
    gpay = settings.get("gpay", "9940147658")
    logo_b64 = settings.get("logo_b64", "")

    items = json.loads(inv.get("items_json", "[]"))
    subtotal   = float(inv.get("subtotal", 0))
    tax_rate   = float(inv.get("tax_rate", 0))
    tax_amount = float(inv.get("tax_amount", 0))
    total      = float(inv.get("total", 0))

    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:90px;height:90px;object-fit:contain;">' if logo_b64 else ""

    rows = ""
    for it in items:
        if it.get("name"):
            amt = float(it["qty"]) * float(it["price"])
            rows += f"""<tr>
              <td style="padding:10px 14px;border-bottom:1px solid #eee;">{it['name']}</td>
              <td style="padding:10px 14px;border-bottom:1px solid #eee;text-align:center;">{it['qty']}</td>
              <td style="padding:10px 14px;border-bottom:1px solid #eee;text-align:right;">Rs.{float(it['price']):.2f}</td>
              <td style="padding:10px 14px;border-bottom:1px solid #eee;text-align:right;">Rs.{amt:.2f}</td>
            </tr>"""

    tax_row = f"""<tr>
      <td colspan="3" style="text-align:right;padding:5px 12px;color:#666;">GST ({tax_rate}%)</td>
      <td style="text-align:right;padding:5px 12px;">Rs.{tax_amount:.2f}</td>
    </tr>""" if tax_rate > 0 else ""

    cust_email_row = f'<div style="font-size:13px;color:#555;">{inv.get("customer_email","")}</div>' if inv.get("customer_email") else ""

    return f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Invoice {inv.get('invoice_no','')}</title>
<style>
  body{{font-family:Arial,sans-serif;margin:0;padding:20px;background:#f5f5f5;color:#333}}
  .box{{max-width:800px;margin:auto;background:white;padding:40px;box-shadow:0 2px 20px rgba(0,0,0,.12);border-radius:4px}}
  .hdr{{display:flex;justify-content:space-between;align-items:flex-start;padding-bottom:24px;border-bottom:2px solid #eee;margin-bottom:28px}}
  .co-right{{text-align:right}}
  .co-right h1{{font-size:38px;letter-spacing:3px;margin:0 0 4px 0;color:#222}}
  .co-right .nm{{font-size:19px;font-weight:700}}
  .co-right .tg{{color:#1a73e8;font-size:13px;margin:2px 0}}
  .co-right .dt{{font-size:12px;color:#666;line-height:1.9;margin-top:6px}}
  .billing{{display:flex;justify-content:space-between;margin-bottom:28px}}
  .bill-to{{background:#f8f9fa;padding:16px 20px;border-radius:8px}}
  .bl{{font-size:11px;color:#999;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}}
  .bc{{font-size:17px;font-weight:700}}
  .bi{{font-size:13px;color:#555;margin-top:3px}}
  .meta td{{padding:4px 10px;font-size:14px}}
  .ml{{color:#888}}.mv{{font-weight:700}}.md{{color:#e53935;font-weight:700;font-size:16px}}
  table.it{{width:100%;border-collapse:collapse;margin-bottom:20px}}
  table.it thead tr{{background:#1a1a2e;color:white}}
  table.it thead td{{padding:12px 14px;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:.5px}}
  .foot{{display:flex;justify-content:space-between;align-items:flex-start;margin-top:10px}}
  .pay h4{{margin:0 0 8px;font-size:12px;text-transform:uppercase;letter-spacing:1px;color:#444}}
  .pay p{{margin:3px 0;font-size:12px;color:#555}}
  .tot td{{padding:5px 12px;font-size:14px}}
  .due-box{{border:2px solid #333;border-radius:4px;padding:14px 22px;text-align:center;margin-top:14px}}
  .due-box .dl{{font-size:12px;color:#999}}
  .due-box .da{{font-size:30px;font-weight:700;color:#222}}
  .footer{{text-align:center;color:#bbb;font-size:11px;margin-top:30px;padding-top:16px;border-top:1px solid #eee}}
  @media print{{body{{background:white;padding:0}}.box{{box-shadow:none}}}}
</style>
</head>
<body><div class="box">
  <div class="hdr">
    <div>{logo_html}</div>
    <div class="co-right">
      <h1>Invoice</h1>
      <div class="nm">{co}</div>
      <div class="tg">{tag}</div>
      <div class="dt">{own}<br>{addr}<br>{ph}<br>{em}</div>
    </div>
  </div>
  <div class="billing">
    <div class="bill-to">
      <div class="bl">Bill To</div>
      <div class="bc">{inv.get('customer_name','')}</div>
      <div class="bi">{inv.get('customer_address','')}</div>
      <div class="bi">Ph: {inv.get('customer_phone','')}</div>
      {cust_email_row}
    </div>
    <table class="meta">
      <tr><td class="ml">Invoice #</td><td class="mv">{inv.get('invoice_no','')}</td></tr>
      <tr><td class="ml">Date</td><td class="mv">{inv.get('invoice_date','')}</td></tr>
      <tr><td class="ml">Due</td><td class="md">{inv.get('due_date','')}</td></tr>
    </table>
  </div>
  <table class="it">
    <thead><tr>
      <td>Item</td>
      <td style="text-align:center">Quantity</td>
      <td style="text-align:right">Price</td>
      <td style="text-align:right">Amount</td>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <div class="foot">
    <div class="pay">
      <h4>Payment Instructions</h4>
      <p>Bank: {bank}, A/c no: {acc}</p>
      <p>IFSC: {ifsc}</p>
      <p>Name: {own}</p>
      <p>Gpay No: {gpay}</p>
    </div>
    <div>
      <table class="tot">
        <tr><td style="text-align:right;color:#888">Subtotal</td><td style="text-align:right;font-weight:700">Rs.{subtotal:.2f}</td></tr>
        {tax_row}
        <tr><td style="text-align:right;color:#888">Total</td><td style="text-align:right;font-weight:700">Rs.{total:.2f}</td></tr>
      </table>
      <div class="due-box">
        <div class="dl">Amount due</div>
        <div class="da">Rs.{total:.2f}</div>
      </div>
    </div>
  </div>
  <div class="footer">Generated by AP Tech Care Invoice App</div>
</div></body></html>"""

# ── Navigation ────────────────────────────────────────────────────────────────
def go(page, **kw):
    st.session_state.page = page
    for k, v in kw.items():
        st.session_state[k] = v
    st.rerun()

if "page" not in st.session_state:
    st.session_state.page = "home"

def topbar(title, back=True):
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        if back and st.button("◀ Back"):
            go("home")
    with c2:
        st.markdown(f"<h3 style='text-align:center;margin:4px 0'>{title}</h3>", unsafe_allow_html=True)
    with c3:
        if st.button("⚙️"):
            go("settings")

# ── PAGE: HOME ────────────────────────────────────────────────────────────────
def page_home():
    settings = db_get_settings()
    co  = settings.get("company_name", "AP Tech Care")
    tag = settings.get("tagline", "Smart Tech Solutions")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);
                padding:22px;border-radius:14px;margin-bottom:20px;text-align:center;">
      <div style="color:#4fc3f7;font-size:12px;letter-spacing:2px;text-transform:uppercase;">{tag}</div>
      <div style="color:white;font-size:26px;font-weight:700;margin-top:4px;">{co}</div>
    </div>
    """, unsafe_allow_html=True)

    invs = db_get_invoices()
    tot_rev  = sum(float(i.get("total", 0)) for i in invs)
    paid_ct  = sum(1 for i in invs if i.get("payment_status") == "paid")
    unpaid_ct = sum(1 for i in invs if i.get("payment_status") == "unpaid")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📄 Total", len(invs))
    c2.metric("💰 Revenue", f"₹{tot_rev:,.0f}")
    c3.metric("✅ Paid", paid_ct)
    c4.metric("⏳ Unpaid", unpaid_ct)

    st.markdown("---")

    b1, b2 = st.columns(2)
    if b1.button("➕  New Invoice", use_container_width=True, type="primary"):
        go("new_invoice")
    if b2.button("📋  All Invoices", use_container_width=True):
        go("invoices")

    b3, b4 = st.columns(2)
    if b3.button("👥  Customers", use_container_width=True):
        go("customers")
    if b4.button("⚙️  Settings", use_container_width=True):
        go("settings")

    if invs:
        st.markdown("### 🕐 Recent Invoices")
        for inv in invs[:5]:
            ca, cb, cc = st.columns([3, 2, 1])
            ca.markdown(f"**{inv['invoice_no']}** — {inv['customer_name']}")
            status_icon = "🟢" if inv.get("payment_status") == "paid" else "🔴"
            cb.write(f"₹{float(inv['total']):,.0f}  {status_icon}")
            if cc.button("View", key=f"h_{inv['id']}"):
                go("view_invoice", view_inv_id=inv["id"])

# ── PAGE: NEW INVOICE ─────────────────────────────────────────────────────────
def page_new_invoice():
    topbar("New Invoice ➕")
    settings = db_get_settings()
    next_no  = db_next_inv_no()

    with st.form("inv_form"):
        st.markdown("#### 👤 Customer Details")
        r1c1, r1c2 = st.columns(2)
        cust_name  = r1c1.text_input("Customer Name *", placeholder="Meenu Subbu Diamond")
        cust_phone = r1c2.text_input("Phone No.", placeholder="95001 01557")
        r2c1, r2c2 = st.columns(2)
        cust_addr  = r2c1.text_input("Address", placeholder="Nandhanam")
        cust_email = r2c2.text_input("Email", placeholder="customer@email.com")

        st.markdown("#### 🧾 Invoice Details")
        d1, d2, d3 = st.columns(3)
        inv_no   = d1.text_input("Invoice No.", value=next_no)
        inv_date = d2.date_input("Invoice Date", value=date.today())
        due_date = d3.date_input("Due Date", value=date.today() + timedelta(days=15))

        tax_on   = st.toggle("GST / Tax On", value=False)
        tax_rate = 0.0
        if tax_on:
            tax_rate = st.number_input("Tax Rate (%)", 0.0, 100.0, 18.0, 0.5)

        st.markdown("#### 📦 Items (upto 15)")
        hc = st.columns([5, 1.5, 2.5, 2])
        hc[0].markdown("**Item Name**")
        hc[1].markdown("**Qty**")
        hc[2].markdown("**Price (₹)**")
        hc[3].markdown("**Amount**")

        items = []
        for i in range(15):
            ic = st.columns([5, 1.5, 2.5, 2])
            nm  = ic[0].text_input("", key=f"n{i}", placeholder=f"Item {i+1}", label_visibility="collapsed")
            qty = ic[1].number_input("", key=f"q{i}", value=1, min_value=1, label_visibility="collapsed")
            prc = ic[2].number_input("", key=f"p{i}", value=0.0, min_value=0.0, format="%.2f", label_visibility="collapsed")
            amt = qty * prc
            ic[3].markdown(f"<div style='padding-top:6px'>₹{amt:.2f}</div>", unsafe_allow_html=True)
            if nm.strip():
                items.append({"name": nm.strip(), "qty": qty, "price": prc, "amount": amt})

        notes = st.text_area("Notes (optional)", placeholder="Thank you for your business!")

        sc1, sc2 = st.columns(2)
        save_btn    = sc1.form_submit_button("💾 Save", use_container_width=True, type="primary")
        preview_btn = sc2.form_submit_button("👁️ Preview & Download", use_container_width=True)

        if save_btn or preview_btn:
            if not cust_name.strip():
                st.error("⚠️ Customer name is required!")
            elif not items:
                st.error("⚠️ Add at least one item!")
            else:
                subtotal   = sum(it["amount"] for it in items)
                tax_amount = round(subtotal * tax_rate / 100, 2)
                total      = subtotal + tax_amount

                inv_data = {
                    "invoice_no":       inv_no,
                    "customer_name":    cust_name.strip(),
                    "customer_phone":   cust_phone,
                    "customer_address": cust_addr,
                    "customer_email":   cust_email,
                    "invoice_date":     inv_date.strftime("%d/%m/%Y"),
                    "due_date":         due_date.strftime("%d/%m/%Y"),
                    "items_json":       json.dumps(items),
                    "subtotal":         subtotal,
                    "tax_rate":         tax_rate,
                    "tax_amount":       tax_amount,
                    "total":            total,
                    "notes":            notes,
                    "payment_status":   "unpaid"
                }

                saved = db_save_invoice(inv_data)
                if saved:
                    st.success(f"✅ Invoice **{inv_no}** saved! Total: ₹{total:.2f}")
                    if preview_btn:
                        html  = make_invoice_html(inv_data, settings)
                        b64   = base64.b64encode(html.encode()).decode()
                        fname = f"{inv_no}.html"
                        st.markdown(
                            f'<a href="data:text/html;base64,{b64}" download="{fname}" '
                            f'style="display:block;text-align:center;padding:12px;'
                            f'background:#1a73e8;color:white;border-radius:10px;'
                            f'text-decoration:none;font-weight:600;margin-top:10px;">'
                            f'⬇️ Download Invoice HTML</a>',
                            unsafe_allow_html=True
                        )
                        wa_msg = f"Invoice {inv_no} - Rs.{total:.2f} from AP Tech Care. Please check the invoice file."
                        wa_url = f"https://wa.me/?text={wa_msg.replace(' ', '%20')}"
                        st.markdown(
                            f'<a href="{wa_url}" target="_blank" '
                            f'style="display:block;text-align:center;padding:12px;'
                            f'background:#25d366;color:white;border-radius:10px;'
                            f'text-decoration:none;font-weight:600;margin-top:8px;">'
                            f'📱 Share via WhatsApp</a>',
                            unsafe_allow_html=True
                        )
                        st.info("💡 Tip: Download HTML → Open in Chrome → Ctrl+P → Save as PDF → Share on WhatsApp")

# ── PAGE: ALL INVOICES ────────────────────────────────────────────────────────
def page_invoices():
    topbar("All Invoices 📋")
    invs = db_get_invoices()
    if not invs:
        st.info("No invoices yet.")
        if st.button("➕ Create First Invoice"):
            go("new_invoice")
        return

    search = st.text_input("🔍 Search", placeholder="Customer name / Invoice no...")
    if search:
        invs = [i for i in invs if
                search.lower() in i.get("customer_name","").lower() or
                search.lower() in i.get("invoice_no","").lower()]

    for inv in invs:
        ca, cb, cc = st.columns([4, 2, 1])
        with ca:
            st.markdown(f"**{inv['invoice_no']}** — {inv['customer_name']}")
            st.caption(f"📞 {inv.get('customer_phone','')} | 📅 {inv.get('invoice_date','')}")
        with cb:
            st.markdown(f"**₹{float(inv['total']):,.2f}**")
            status = inv.get("payment_status","unpaid")
            st.caption("🟢 Paid" if status == "paid" else "🔴 Unpaid")
        with cc:
            if st.button("View", key=f"iv_{inv['id']}"):
                go("view_invoice", view_inv_id=inv["id"])
        st.divider()

# ── PAGE: VIEW INVOICE ────────────────────────────────────────────────────────
def page_view_invoice():
    inv_id = st.session_state.get("view_inv_id")
    if not inv_id:
        go("invoices"); return

    inv = db_get_invoice(inv_id)
    if not inv:
        st.error("Invoice not found!"); go("invoices"); return

    topbar(f"Invoice {inv['invoice_no']}")
    settings = db_get_settings()

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"**Customer:** {inv['customer_name']}")
    c1.markdown(f"**Phone:** {inv.get('customer_phone','')}")
    c2.markdown(f"**Date:** {inv.get('invoice_date','')}")
    c2.markdown(f"**Due:** {inv.get('due_date','')}")
    c3.markdown(f"**Total: ₹{float(inv['total']):,.2f}**")

    curr_status = inv.get("payment_status","unpaid")
    new_status  = c3.selectbox("Status", ["unpaid","paid"],
                               index=0 if curr_status == "unpaid" else 1,
                               key="status_sel")
    if new_status != curr_status:
        if db_update_status(inv_id, new_status):
            st.success("✅ Status updated!")
            st.rerun()

    st.markdown("---")

    # Download + WhatsApp + Delete
    html  = make_invoice_html(inv, settings)
    b64   = base64.b64encode(html.encode()).decode()
    fname = f"{inv['invoice_no']}.html"

    bc1, bc2, bc3 = st.columns(3)
    bc1.markdown(
        f'<a href="data:text/html;base64,{b64}" download="{fname}" '
        f'style="display:block;text-align:center;padding:10px;background:#1a73e8;'
        f'color:white;border-radius:10px;text-decoration:none;font-weight:600;">'
        f'⬇️ Download HTML</a>', unsafe_allow_html=True
    )
    wa_msg = f"Invoice {inv['invoice_no']} - Rs.{float(inv['total']):.2f} from AP Tech Care."
    wa_url = f"https://wa.me/?text={wa_msg.replace(' ', '%20')}"
    bc2.markdown(
        f'<a href="{wa_url}" target="_blank" style="display:block;text-align:center;'
        f'padding:10px;background:#25d366;color:white;border-radius:10px;'
        f'text-decoration:none;font-weight:600;">📱 WhatsApp</a>',
        unsafe_allow_html=True
    )
    if bc3.button("🗑️ Delete Invoice", use_container_width=True):
        st.session_state["confirm_del"] = True

    if st.session_state.get("confirm_del"):
        st.warning(f"⚠️ Delete **{inv['invoice_no']}**? This cannot be undone!")
        y, n = st.columns(2)
        if y.button("Yes, Delete"):
            db_delete_invoice(inv_id)
            st.session_state.pop("confirm_del", None)
            go("invoices")
        if n.button("Cancel"):
            st.session_state.pop("confirm_del", None)
            st.rerun()

    # Items preview
    st.markdown("#### Items")
    items = json.loads(inv.get("items_json","[]"))
    for it in items:
        if it.get("name"):
            ic1, ic2, ic3 = st.columns([4, 1, 2])
            ic1.write(it["name"])
            ic2.write(f"× {it['qty']}")
            ic3.write(f"₹{float(it['qty'])*float(it['price']):.2f}")

# ── PAGE: CUSTOMERS ───────────────────────────────────────────────────────────
def page_customers():
    topbar("Customers 👥")
    invs = db_get_invoices()
    custs = {}
    for inv in invs:
        nm = inv.get("customer_name","")
        if nm:
            if nm not in custs:
                custs[nm] = {"phone": inv.get("customer_phone",""),
                             "addr":  inv.get("customer_address",""),
                             "count": 0, "total": 0.0}
            custs[nm]["count"] += 1
            custs[nm]["total"] += float(inv.get("total",0))

    if not custs:
        st.info("No customers yet."); return

    for nm, c in custs.items():
        ca, cb = st.columns([3, 2])
        ca.markdown(f"**{nm}**")
        ca.caption(f"📞 {c['phone']}  📍 {c['addr']}")
        cb.write(f"{c['count']} invoice(s)")
        cb.write(f"₹{c['total']:,.0f}")
        st.divider()

# ── PAGE: SETTINGS ────────────────────────────────────────────────────────────
def page_settings():
    topbar("Settings ⚙️")
    s = db_get_settings()

    with st.form("settings_form"):
        st.markdown("#### 🏢 Company Info")
        co_name = st.text_input("Company Name",    value=s.get("company_name", "AP Tech Care"))
        tagline = st.text_input("Tagline",          value=s.get("tagline",      "Smart Tech Solutions"))
        owner   = st.text_input("Owner Name",       value=s.get("owner_name",   "T.Arunprasad, BE., MBA.,"))
        address = st.text_area("Address",           value=s.get("address",
                    "1/4A, Kamaraj Cross Street, Ambal Nagar, Ramapuram, Chennai, Tamilnadu 600 089"))

        st.markdown("#### 📞 Contact")
        sc1, sc2 = st.columns(2)
        phone = sc1.text_input("Phone",  value=s.get("phone", "9940147658"))
        email = sc2.text_input("Email",  value=s.get("email", "aptechcare.chennai@gmail.com"))

        st.markdown("#### 🏦 Bank Details")
        bc1, bc2 = st.columns(2)
        bank = bc1.text_input("Bank Name",     value=s.get("bank_name", "SBI"))
        acc  = bc2.text_input("Account No.",   value=s.get("acc_no",    "20001142967"))
        ic1, ic2 = st.columns(2)
        ifsc = ic1.text_input("IFSC Code",     value=s.get("ifsc",      "SBIN0018229"))
        gpay = ic2.text_input("GPay No.",      value=s.get("gpay",      "9940147658"))

        st.markdown("#### 🖼️ Logo")
        logo_file = st.file_uploader("Upload Logo (PNG/JPG)", type=["png","jpg","jpeg"])
        if s.get("logo_b64"):
            st.caption("✅ Logo currently uploaded")

        save_btn = st.form_submit_button("💾 Save All Settings", type="primary", use_container_width=True)

        if save_btn:
            fields = {"company_name": co_name, "tagline": tagline,
                      "owner_name": owner, "address": address,
                      "phone": phone, "email": email,
                      "bank_name": bank, "acc_no": acc,
                      "ifsc": ifsc, "gpay": gpay}
            if logo_file:
                fields["logo_b64"] = base64.b64encode(logo_file.read()).decode()
            for k, v in fields.items():
                db_save_setting(k, v)
            st.success("✅ Settings saved!")
            st.rerun()

# ── ROUTER ────────────────────────────────────────────────────────────────────
pg = st.session_state.page

if   pg == "home":          page_home()
elif pg == "new_invoice":   page_new_invoice()
elif pg == "invoices":      page_invoices()
elif pg == "view_invoice":  page_view_invoice()
elif pg == "customers":     page_customers()
elif pg == "settings":      page_settings()
else:                       page_home()
🚀 STEP 6 — GitHub & Streamlit Deployment
GitHub:
github.com → New Repository → Name: aptechcare-invoice-v2
Public ✅ → Create
Upload pannunga: app.py, requirements.txt
.streamlit/secrets.toml → DO NOT upload (local only)
Streamlit Cloud:
share.streamlit.io → New App
Repository: aptechcare-invoice-v2
Main file: app.py
Advanced Settings → Secrets paste pannunga:
SUPABASE_URL = "https://zibexeqgtajeaujjkwqe.supabase.co"
SUPABASE_KEY = "your-anon-key"
Deploy! ✅
✅ Features Summary
Feature
Status
Settings (logo, company, bank)
✅
New Invoice (15 items)
✅
Invoice No. AP-1001+ auto
✅
Date dd/mm/yyyy
✅
GST toggle
✅
Save to Supabase
✅
Download HTML invoice
✅
WhatsApp share button
✅
View / Delete invoices
✅
Payment status (paid/unpaid)
✅
Customer list
✅
Mobile responsive
✅
