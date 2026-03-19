import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import base64
from PIL import Image
import json
from supabase import create_client, Client

# ---------------- SUPABASE CONNECTION ----------------

@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

sb = get_supabase()

# ---------------- COMPANY INFO ----------------

COMPANY_NAME    = "AP Tech Care"
COMPANY_TAGLINE = "Smart Tech Solutions"
COMPANY_ADDRESS = "1/4A, Kamaraj Cross Street,\nAmbal Nagar, Ramapuram,\nChennai, Tamilnadu 600 089"
COMPANY_PERSON  = "T.ArunPrasad, BE., MBA."
COMPANY_PHONE   = "9940147658"
COMPANY_EMAIL   = "aptechcare.chennai@gmail.com"
BANK_NAME       = "SBI"
BANK_ACNO       = "20001142967"
BANK_IFSC       = "SBIN0018229"
GPAY_NO         = "9940147658"
LOGO_PATH       = "saved_logo.png"
MATERIALS_DIR   = "material_photos"

os.makedirs(MATERIALS_DIR, exist_ok=True)

# ---------------- HELPERS ----------------

def get_next_invoice_no():
    res = sb.table("invoices").select("invoice_no").execute()
    if res.data:
        nums = []
        for r in res.data:
            try:
                nums.append(int(r["invoice_no"].replace("AP-", "")))
            except: pass
        return f"AP-{max(nums) + 1}" if nums else "AP-1000"
    return "AP-1000"

def save_logo(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    img.save(LOGO_PATH, "PNG")

def logo_exists():
    return os.path.exists(LOGO_PATH)

def get_services():
    res = sb.table("services").select("*").order("name").execute()
    return res.data or []

def pdf_to_images(pdf_path):
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path, dpi=200)
        img_paths = []
        for i, img in enumerate(images):
            p = pdf_path.replace(".pdf", f"_page{i+1}.jpg")
            img.save(p, "JPEG", quality=95)
            img_paths.append(p)
        return img_paths
    except:
        return []

# ---------------- PDF ----------------

def generate_pdf(invoice_no, customer, cust_address, cust_phone, date_str, items, paid_amount):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    if logo_exists():
        pdf.image(LOGO_PATH, x=15, y=8, w=50)

    pdf.set_xy(120, 12)
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(75, 10, "Invoice", ln=True, align="R")
    pdf.set_font("Arial", "B", 13); pdf.set_text_color(30, 30, 30)
    pdf.set_x(120); pdf.cell(75, 7, COMPANY_NAME, ln=True, align="R")
    pdf.set_font("Arial", "", 9); pdf.set_text_color(80, 80, 80)
    pdf.set_x(120); pdf.cell(75, 5, COMPANY_TAGLINE, ln=True, align="R")
    for line in COMPANY_ADDRESS.split("\n"):
        pdf.set_x(120); pdf.cell(75, 5, line, ln=True, align="R")
    pdf.set_x(120); pdf.cell(75, 5, "IN", ln=True, align="R")
    pdf.set_x(120); pdf.cell(75, 5, COMPANY_PERSON, ln=True, align="R")
    pdf.set_x(120); pdf.cell(75, 5, COMPANY_PHONE, ln=True, align="R")
    pdf.set_x(120); pdf.cell(75, 5, COMPANY_EMAIL, ln=True, align="R")

    pdf.ln(5)
    current_y  = pdf.get_y()
    bill_height = 28 if (cust_address or cust_phone) else 18
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(15, current_y, 180, bill_height, 'F')
    pdf.set_xy(18, current_y + 2)
    pdf.set_font("Arial", "B", 9); pdf.set_text_color(50, 50, 50)
    pdf.cell(60, 5, "BILL TO", ln=True)
    pdf.set_xy(18, current_y + 8)
    pdf.set_font("Arial", "B", 10); pdf.cell(80, 5, customer, ln=True)
    if cust_address:
        pdf.set_x(18); pdf.set_font("Arial", "", 8); pdf.set_text_color(80, 80, 80)
        pdf.cell(80, 4, cust_address, ln=True)
    if cust_phone:
        pdf.set_x(18); pdf.set_font("Arial", "", 8)
        pdf.cell(80, 4, f"Ph: {cust_phone}", ln=True)

    pdf.set_xy(130, current_y + 2)
    pdf.set_font("Arial", "B", 9); pdf.set_text_color(50, 50, 50)
    pdf.cell(25, 5, "Invoice #", ln=False)
    pdf.set_font("Arial", "", 9); pdf.cell(40, 5, str(invoice_no), ln=True, align="R")
    pdf.set_xy(130, current_y + 8)
    pdf.set_font("Arial", "B", 9); pdf.cell(25, 5, "Date", ln=False)
    pdf.set_font("Arial", "", 9); pdf.cell(40, 5, date_str, ln=True, align="R")

    pdf.ln(8)
    pdf.set_draw_color(200, 200, 200); pdf.set_text_color(30, 30, 30)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(80, 8, "Item", border="B", ln=False)
    pdf.cell(30, 8, "Quantity", border="B", align="C", ln=False)
    pdf.cell(35, 8, "Price", border="B", align="R", ln=False)
    pdf.cell(35, 8, "Amount", border="B", align="R", ln=True)

    subtotal = 0
    for item in items:
        pdf.set_font("Arial", "B", 10); pdf.set_text_color(30, 30, 30)
        pdf.cell(80, 7, item["Item"], ln=False)
        pdf.set_font("Arial", "", 10)
        pdf.cell(30, 7, str(item["Qty"]), align="C", ln=False)
        pdf.cell(35, 7, f"Rs.{item['Price']:,.2f}", align="R", ln=False)
        pdf.cell(35, 7, f"Rs.{item['Amount']:,.2f}", align="R", ln=True)
        if item.get("Notes"):
            pdf.set_font("Arial", "", 8); pdf.set_text_color(120, 120, 120)
            pdf.set_x(15); pdf.multi_cell(80, 4, item["Notes"])
            pdf.set_text_color(30, 30, 30)
        pdf.ln(2)
        subtotal += item["Amount"]

    pdf.line(15, pdf.get_y(), 195, pdf.get_y()); pdf.ln(5)
    pay_y = pdf.get_y()
    pdf.set_xy(15, pay_y)
    pdf.set_font("Arial", "B", 10); pdf.set_text_color(30, 30, 30)
    pdf.cell(80, 6, "Payment Instructions", ln=True)
    pdf.set_font("Arial", "", 9); pdf.set_text_color(80, 80, 80)
    pdf.set_x(15); pdf.cell(80, 5, f"Bank: {BANK_NAME}, A/c no: {BANK_ACNO}", ln=True)
    pdf.set_x(15); pdf.cell(80, 5, f"IFSC: {BANK_IFSC}", ln=True)
    pdf.set_x(15); pdf.cell(80, 5, f"Name: {COMPANY_PERSON}", ln=True)
    pdf.set_x(15); pdf.cell(80, 5, f"Gpay No: {GPAY_NO}", ln=True)

    total = subtotal; amount_due = total - paid_amount
    pdf.set_xy(120, pay_y)
    pdf.set_font("Arial", "", 10); pdf.set_text_color(50, 50, 50)
    pdf.cell(40, 7, "Subtotal", ln=False); pdf.cell(35, 7, f"Rs.{subtotal:,.2f}", align="R", ln=True)
    pdf.set_x(120); pdf.cell(40, 7, "Total", ln=False); pdf.cell(35, 7, f"Rs.{total:,.2f}", align="R", ln=True)
    if paid_amount > 0:
        pdf.set_x(120); pdf.cell(40, 7, "Paid", ln=False)
        pdf.cell(35, 7, f"Rs.{paid_amount:,.2f}", align="R", ln=True)

    pdf.ln(5); pdf.set_x(120)
    pdf.set_fill_color(245, 245, 245); pdf.set_draw_color(200, 200, 200)
    pdf.set_font("Arial", "", 10); pdf.set_text_color(80, 80, 80)
    pdf.cell(75, 7, "Amount due", border=1, fill=True, ln=True, align="C")
    pdf.set_x(120); pdf.set_font("Arial", "B", 16); pdf.set_text_color(30, 30, 30)
    pdf.cell(75, 12, f"Rs.{amount_due:,.2f}", border=1, fill=True, ln=True, align="C")
    pdf.set_y(-20); pdf.set_font("Arial", "I", 8); pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "Generated by AP Tech Care Invoice App", align="C")

    file_name = f"invoice_{invoice_no}.pdf"
    pdf.output(file_name)
    return file_name, total, amount_due

# ---------------- EMAIL ----------------

def send_email(to_email, subject, body, pdf_path, gmail_user, gmail_password):
    try:
        msg = MIMEMultipart()
        msg["From"] = gmail_user; msg["To"] = to_email; msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(pdf_path)}")
            msg.attach(part)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls(); server.login(gmail_user, gmail_password)
        server.send_message(msg); server.quit()
        return True, "Sent!"
    except Exception as e:
        return False, str(e)

# ================================================================
# UI
# ================================================================

st.set_page_config(page_title="AP Tech Care", page_icon="🖨️", layout="centered")
st.markdown("""
<style>
    .block-container { max-width: 500px; padding: 1rem; }
    .stButton > button {
        width: 100%; border-radius: 12px; padding: 11px; font-size: 15px; font-weight: 600;
        background: linear-gradient(135deg, #1e50b4, #0a2d6e);
        color: white; border: none; box-shadow: 0 4px 12px rgba(30,80,180,0.3);
    }
    .inv-badge { background:#e8f0ff;color:#1e50b4;padding:6px 14px;border-radius:20px;font-weight:bold;font-size:15px;display:inline-block; }
    .amount-due { background:linear-gradient(135deg,#1e50b4,#0a2d6e);color:white;border-radius:14px;padding:16px;text-align:center;margin:10px 0; }
    .amount-due .label { font-size:13px;opacity:.85; }
    .amount-due .value { font-size:28px;font-weight:bold; }
    .cust-info { background:#f0f7ff;border-radius:10px;padding:10px 14px;font-size:13px;color:#333;margin-bottom:8px; }
    .share-box { background:#f0f7ff;border-radius:12px;padding:14px;margin-top:10px; }
    .wa-btn { display:block;background:#25D366;color:white;padding:12px;border-radius:12px;text-align:center;font-size:15px;font-weight:600;text-decoration:none;margin:8px 0; }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# HEADER
if logo_exists():
    c1, c2 = st.columns([1, 3])
    with c1: st.image(LOGO_PATH, width=65)
    with c2:
        st.markdown(f"""<div style='padding-top:8px'>
            <div style='font-size:20px;font-weight:bold;color:#1e50b4'>{COMPANY_NAME}</div>
            <div style='font-size:12px;color:#666'>{COMPANY_TAGLINE}</div></div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""<div style='background:linear-gradient(135deg,#1e50b4,#0a2d6e);color:white;
    padding:18px;border-radius:16px;text-align:center;margin-bottom:20px'>
    <h2 style='margin:0;color:white'>🖨️ {COMPANY_NAME}</h2>
    <p style='margin:2px 0 0;opacity:.85'>{COMPANY_TAGLINE}</p></div>""", unsafe_allow_html=True)

menu = st.sidebar.radio("", ["🧾 Invoice", "💰 Cashflow", "📦 Materials", "📊 Monthly Report", "⚙️ Settings"])

# ================================================================
# INVOICE
# ================================================================
if menu == "🧾 Invoice":
    invoice_no = get_next_invoice_no()

    st.markdown("**👤 Customer**")
    cust_res  = sb.table("customers").select("*").execute()
    cust_data = cust_res.data or []
    cust_names = [c["name"] for c in cust_data]
    customer  = st.selectbox("", ["+ New Customer"] + cust_names, label_visibility="collapsed")

    cust_phone = cust_email = cust_address = ""

    if customer == "+ New Customer":
        customer     = st.text_input("Customer Name",    placeholder="Enter name")
        cust_phone   = st.text_input("Phone",            placeholder="e.g. 9876543210")
        cust_address = st.text_input("Address",          placeholder="e.g. Anna Nagar, Chennai")
        cust_email   = st.text_input("Email (optional)", placeholder="customer@email.com")
    else:
        row = next((c for c in cust_data if c["name"] == customer), None)
        if row:
            cust_phone   = row.get("phone", "") or ""
            cust_email   = row.get("email", "") or ""
            cust_address = row.get("address", "") or ""
        st.markdown(f"""<div class='cust-info'>
            📱 <b>{cust_phone or 'No phone'}</b><br>
            🏠 {cust_address or 'No address'}<br>
            📧 {cust_email or 'No email'}</div>""", unsafe_allow_html=True)
        with st.expander("✏️ Edit Customer"):
            cust_phone   = st.text_input("Phone",   value=cust_phone,   key="ep")
            cust_address = st.text_input("Address", value=cust_address, key="ea")
            cust_email   = st.text_input("Email",   value=cust_email,   key="ee")
            if st.button("Update"):
                sb.table("customers").update({"phone": cust_phone, "email": cust_email, "address": cust_address}).eq("name", customer).execute()
                st.success("Updated!"); st.rerun()

    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<div class='inv-badge'>📄 {invoice_no}</div>", unsafe_allow_html=True)
    with c2: date = st.date_input("Date", datetime.now(), label_visibility="collapsed", format="DD/MM/YYYY")

    st.divider()
    st.markdown("**🛒 Items**")
    num_items = st.number_input("No. of Items", min_value=1, max_value=15, step=1, value=1)

    svcs     = get_services()
    svc_dict = {s["name"]: s["price"] for s in svcs}
    svc_names = list(svc_dict.keys()) or ["General Service"]

    item_list = []; subtotal = 0
    for i in range(int(num_items)):
        st.markdown(f"**Item {i+1}**")
        item_name = st.selectbox("Service", svc_names, key=f"item_{i}")
        c1, c2    = st.columns(2)
        with c1: qty   = st.number_input("Qty",       min_value=1, key=f"qty_{i}")
        with c2: price = st.number_input("Price Rs.", min_value=0,
                                          value=int(svc_dict.get(item_name, 0)), key=f"price_{i}")
        notes  = st.text_area("Notes (optional)", key=f"notes_{i}", height=60, placeholder="Work done details...")
        amount  = qty * price; subtotal += amount
        st.markdown(f"💰 **Rs.{amount:,.2f}**"); st.markdown("---")
        item_list.append({"Item": item_name, "Qty": qty, "Price": price, "Amount": amount, "Notes": notes})

    gst_enabled = st.toggle("Enable GST", value=False)
    tax_amount = tax_percent = 0
    if gst_enabled:
        tax_percent = st.number_input("GST %", value=18)
        tax_amount  = subtotal * tax_percent / 100

    total       = subtotal + tax_amount
    paid_amount = st.number_input("Paid Amount Rs.", min_value=0, value=0)
    amount_due  = total - paid_amount

    c1, c2, c3 = st.columns(3)
    c1.metric("Subtotal", f"Rs.{subtotal:,.0f}")
    c2.metric("Paid",     f"Rs.{paid_amount:,.0f}")
    c3.metric("Due",      f"Rs.{amount_due:,.0f}")

    st.markdown(f"""<div class='amount-due'>
        <div class='label'>Amount Due</div>
        <div class='value'>Rs.{amount_due:,.2f}</div></div>""", unsafe_allow_html=True)

    if st.button("💾 Save & Generate Invoice"):
        if not customer or customer == "+ New Customer":
            st.error("Customer name enter pannanu!")
        else:
            # Save customer
            try:
                sb.table("customers").insert({"name": customer, "phone": cust_phone,
                                               "email": cust_email, "address": cust_address}).execute()
            except:
                sb.table("customers").update({"phone": cust_phone, "email": cust_email,
                                               "address": cust_address}).eq("name", customer).execute()

            date_str = date.strftime("%d/%m/%Y")
            pdf_file, total_c, due_c = generate_pdf(
                invoice_no, customer, cust_address, cust_phone, date_str, item_list, paid_amount)

            sb.table("invoices").insert({
                "invoice_no": invoice_no, "customer": customer,
                "total": total_c, "paid": paid_amount,
                "amount_due": due_c, "date": date_str
            }).execute()

            img_paths = pdf_to_images(pdf_file)
            st.success(f"✅ Invoice {invoice_no} saved!")
            st.session_state.update({
                "last_pdf": pdf_file, "last_imgs": img_paths,
                "last_phone": cust_phone, "last_email": cust_email,
                "last_inv_no": invoice_no, "last_customer": customer,
                "last_total": total_c
            })

    # SHARE
    if "last_pdf" in st.session_state and os.path.exists(st.session_state["last_pdf"]):
        pdf_file  = st.session_state["last_pdf"]
        img_paths = st.session_state.get("last_imgs", [])
        inv_no    = st.session_state["last_inv_no"]
        phone     = st.session_state["last_phone"]
        email     = st.session_state["last_email"]
        cname     = st.session_state["last_customer"]
        tot       = st.session_state["last_total"]

        st.markdown("<div class='share-box'>", unsafe_allow_html=True)
        st.markdown("### 📤 Share Invoice")

        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name=pdf_file, mime="application/pdf", key="dl_pdf")

        st.divider()
        st.markdown("**📱 WhatsApp Image**")
        if img_paths:
            for i, img_path in enumerate(img_paths):
                if os.path.exists(img_path):
                    st.image(img_path, use_column_width=True)
                    with open(img_path, "rb") as f:
                        st.download_button(f"📥 Download Image", f.read(),
                                           file_name=f"invoice_{inv_no}_p{i+1}.jpg",
                                           mime="image/jpeg", key=f"dl_img_{i}")
        wa_num  = phone.replace("+","").replace(" ","")
        msg     = f"Hello {cname},%0AYour invoice {inv_no} from AP Tech Care.%0ATotal: Rs.{tot:,.2f}%0AThank you!"
        wa_link = f"https://wa.me/{wa_num}?text={msg}" if wa_num else f"https://wa.me/?text={msg}"
        st.markdown(f"<a href='{wa_link}' target='_blank' class='wa-btn'>📱 Open WhatsApp</a>",
                    unsafe_allow_html=True)

        st.divider()
        st.markdown("**🖨️ Print**")
        with open(pdf_file, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'''<a href="data:application/pdf;base64,{b64}" target="_blank">
            <button style="background:#1e50b4;color:white;border:none;padding:10px 20px;
            border-radius:10px;cursor:pointer;font-size:14px;width:100%">🖨️ Open & Print</button></a>''',
            unsafe_allow_html=True)

        st.divider()
        st.markdown("**📧 Email**")
        with st.expander("Send via Email"):
            to_email   = st.text_input("Email", value=email, key="to_email")
            gmail_user = st.text_input("Your Gmail")
            gmail_pass = st.text_input("App Password", type="password")
            if st.button("📧 Send"):
                if to_email and gmail_user and gmail_pass:
                    ok, res = send_email(to_email, f"Invoice {inv_no} - AP Tech Care",
                        f"Dear {cname},\n\nInvoice {inv_no}\nTotal: Rs.{tot:,.2f}\n\nThank you!\nAP Tech Care",
                        pdf_file, gmail_user, gmail_pass)
                    st.success("✅ Sent!") if ok else st.error(f"Error: {res}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("**📋 Recent Invoices**")
    inv_res = sb.table("invoices").select("*").order("id", desc=True).limit(10).execute()
    if inv_res.data:
        st.dataframe(pd.DataFrame(inv_res.data)[["invoice_no","customer","total","paid","amount_due","date"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("No invoices yet.")

# ================================================================
# CASHFLOW
# ================================================================
elif menu == "💰 Cashflow":
    st.markdown("**💰 Cashflow**")
    cf_res = sb.table("transactions").select("*").order("id", desc=True).execute()
    df     = pd.DataFrame(cf_res.data) if cf_res.data else pd.DataFrame()

    if not df.empty:
        inc = df[df["type"]=="Income"]["amount"].sum()
        exp = df[df["type"]=="Expense"]["amount"].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Income",  f"Rs.{inc:,.0f}")
        c2.metric("Expense", f"Rs.{exp:,.0f}")
        c3.metric("Balance", f"Rs.{inc-exp:,.0f}")

    st.divider()
    t_type = st.selectbox("Type", ["Income","Expense"])
    amount = st.number_input("Amount Rs.", min_value=0)
    note   = st.text_input("Note")
    if st.button("Save"):
        sb.table("transactions").insert({
            "type": t_type, "amount": amount,
            "note": note, "date": datetime.now().strftime("%d/%m/%Y")
        }).execute()
        st.success("Saved!"); st.rerun()

    if not df.empty:
        st.dataframe(df[["type","amount","note","date"]], use_container_width=True, hide_index=True)

# ================================================================
# MATERIALS
# ================================================================
elif menu == "📦 Materials":
    st.markdown("**📦 Material / Product Entry**")

    with st.form("mat_form"):
        serial_no    = st.text_input("Serial No",    placeholder="e.g. SN123456")
        product_name = st.text_input("Product Name", placeholder="e.g. HP LaserJet Toner")
        notes        = st.text_area("Notes",         height=80)
        photos       = st.file_uploader("Upload Photos (max 10)", type=["jpg","jpeg","png"],
                                         accept_multiple_files=True)
        submitted    = st.form_submit_button("💾 Save")

        if submitted:
            if not product_name:
                st.error("Product name enter pannanu!")
            else:
                saved_paths = []
                if photos:
                    for i, photo in enumerate(photos[:10]):
                        fname = f"{MATERIALS_DIR}/{serial_no or 'item'}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}.jpg"
                        Image.open(photo).convert("RGB").save(fname, "JPEG", quality=90)
                        saved_paths.append(fname)
                sb.table("materials").insert({
                    "serial_no": serial_no, "product_name": product_name,
                    "notes": notes, "photos": json.dumps(saved_paths),
                    "date": datetime.now().strftime("%d/%m/%Y")
                }).execute()
                st.success(f"✅ '{product_name}' saved!")

    st.divider()
    st.markdown("**📋 Material Records**")
    mat_res = sb.table("materials").select("*").order("id", desc=True).execute()
    mat_data = mat_res.data or []

    if not mat_data:
        st.info("No materials yet.")
    else:
        search = st.text_input("🔍 Search")
        if search:
            mat_data = [m for m in mat_data if
                        search.lower() in (m.get("product_name","") or "").lower() or
                        search.lower() in (m.get("serial_no","") or "").lower()]

        for row in mat_data:
            with st.expander(f"📦 {row['product_name']} | {row.get('serial_no') or 'No Serial'} | {row['date']}"):
                st.markdown(f"**Serial No:** {row.get('serial_no') or '-'}")
                st.markdown(f"**Notes:** {row.get('notes') or '-'}")
                photos_list = json.loads(row["photos"]) if row.get("photos") else []
                if photos_list:
                    cols = st.columns(min(len(photos_list), 3))
                    for i, p in enumerate(photos_list):
                        if os.path.exists(p):
                            cols[i % 3].image(p, use_column_width=True)
                if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                    sb.table("materials").delete().eq("id", row["id"]).execute()
                    st.rerun()

# ================================================================
# MONTHLY REPORT
# ================================================================
elif menu == "📊 Monthly Report":
    st.markdown("**📊 Monthly Report**")
    inv_res = sb.table("invoices").select("*").execute()
    if not inv_res.data:
        st.info("No invoices yet.")
    else:
        df = pd.DataFrame(inv_res.data)
        df["date_parsed"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        df["month_str"]   = df["date_parsed"].dt.strftime("%b %Y")
        months    = df["month_str"].dropna().unique().tolist()
        sel_month = st.selectbox("Select Month", months)
        mdf       = df[df["month_str"] == sel_month]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Invoices", len(mdf))
        c2.metric("Revenue",  f"Rs.{mdf['total'].sum():,.0f}")
        c3.metric("Paid",     f"Rs.{mdf['paid'].sum():,.0f}")
        c4.metric("Pending",  f"Rs.{mdf['amount_due'].sum():,.0f}")

        st.bar_chart(df.groupby("month_str")["total"].sum().reset_index().set_index("month_str"))
        st.dataframe(mdf[["invoice_no","customer","total","paid","amount_due","date"]].reset_index(drop=True),
                     use_container_width=True, hide_index=True)
        top = df.groupby("customer")["total"].sum().reset_index().sort_values("total",ascending=False).head(5)
        if not top.empty:
            st.bar_chart(top.set_index("customer"))
        csv = mdf.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, file_name=f"report_{sel_month}.csv", mime="text/csv")

# ================================================================
# SETTINGS
# ================================================================
elif menu == "⚙️ Settings":
    st.markdown("**⚙️ Settings**")

    st.markdown("**🖼️ Logo**")
    if logo_exists():
        st.image(LOGO_PATH, width=120); st.success("✅ Logo saved")
        if st.checkbox("Change Logo"):
            nl = st.file_uploader("New Logo", type=["png","jpg","jpeg"])
            if nl: save_logo(nl); st.success("Updated!"); st.rerun()
    else:
        nl = st.file_uploader("Upload Logo", type=["png","jpg","jpeg"])
        if nl: save_logo(nl); st.success("✅ Saved!"); st.rerun()

    st.divider()
    st.markdown("**🛠️ Service List**")
    svcs = get_services()

    with st.expander("➕ Add New Service"):
        ni   = st.text_input("Service Name")
        np_  = st.number_input("Price Rs.", min_value=0, key="np")
        if st.button("Add Service"):
            if ni:
                try:
                    sb.table("services").insert({"name": ni, "price": np_}).execute()
                    st.success(f"'{ni}' Added!"); st.rerun()
                except: st.error("Already exists!")

    for svc in svcs:
        c1, c2, c3 = st.columns([4, 2, 1])
        with c1: st.markdown(f"**{svc['name']}**")
        with c2:
            new_p = st.number_input("Rs.", value=int(svc["price"]),
                                     key=f"sp_{svc['id']}", label_visibility="collapsed")
            if new_p != svc["price"]:
                sb.table("services").update({"price": new_p}).eq("id", svc["id"]).execute()
        with c3:
            if st.button("🗑️", key=f"ds_{svc['id']}"):
                sb.table("services").delete().eq("id", svc["id"]).execute(); st.rerun()

    st.divider()
    st.markdown("**👥 Customers**")
    cust_res = sb.table("customers").select("*").execute()
    if cust_res.data:
        st.dataframe(pd.DataFrame(cust_res.data)[["name","phone","address","email"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("No customers.")

    st.divider()
    inv_count  = sb.table("invoices").select("id", count="exact").execute().count or 0
    cust_count = sb.table("customers").select("id", count="exact").execute().count or 0
    inv_all    = sb.table("invoices").select("total,amount_due").execute().data or []
    total_rev  = sum(r["total"] for r in inv_all)
    total_due  = sum(r["amount_due"] for r in inv_all)

    c1, c2 = st.columns(2)
    c1.metric("Invoices",  inv_count);  c2.metric("Customers", cust_count)
    c1.metric("Revenue",   f"Rs.{total_rev:,.0f}"); c2.metric("Pending", f"Rs.{total_due:,.0f}")
