# 🔥 FULL FIXED ORIGINAL APP (NO DATA LOSS + MOBILE FIX)

import streamlit as st
import json, os
from datetime import datetime, date

st.set_page_config(page_title="AP Tech Care", layout="wide")

DATA_FILE = "data.json"

# ── LOAD / SAVE ─────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "invoices": st.session_state.invoices,
            "customers": st.session_state.customers,
            "items_db": st.session_state.items_db,
            "settings": st.session_state.settings
        }, f)

# ── INIT ─────────────────────────
data = load_data()

if "invoices" not in st.session_state:
    st.session_state.invoices = data.get("invoices", [])

if "customers" not in st.session_state:
    st.session_state.customers = data.get("customers", [])

if "items_db" not in st.session_state:
    st.session_state.items_db = data.get("items_db", [
        {"name": "General Service", "price": 500},
        {"name": "Repair", "price": 1500}
    ])

if "settings" not in st.session_state:
    st.session_state.settings = data.get("settings", {})

# ── MOBILE FIX ─────────────────────────
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    width: 220px !important;
}

@media (max-width: 768px) {
    section[data-testid="stSidebar"] {
        position: fixed;
        z-index: 999;
        width: 200px !important;
    }
    .main {
        margin-left: 0 !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ─────────────────────────
with st.sidebar:
    st.title("AP Tech Care")
    page = st.radio("Menu", [
        "Dashboard", "Invoices", "Customers", "Items"
    ])

# ── DASHBOARD ─────────────────────────
if page == "Dashboard":
    st.title("Dashboard")

    total = len(st.session_state.invoices)
    collected = sum(i.get("amount", 0) for i in st.session_state.invoices)

    c1, c2 = st.columns(2)
    c1.metric("Invoices", total)
    c2.metric("Revenue", f"Rs.{collected}")

# ── INVOICES ─────────────────────────
if page == "Invoices":
    st.title("Invoices")

    cust = st.text_input("Customer Name")
    amount = st.number_input("Amount", min_value=0)

    if st.button("Create Invoice"):
        inv = {
            "id": f"INV-{len(st.session_state.invoices)+1}",
            "customer": cust,
            "amount": amount,
            "date": str(date.today())
        }
        st.session_state.invoices.append(inv)
        save_data()
        st.success("Saved ✅")

    st.divider()

    for inv in st.session_state.invoices:
        st.write(inv)

# ── CUSTOMERS ─────────────────────────
if page == "Customers":
    st.title("Customers")

    cname = st.text_input("Customer Name")

    if st.button("Add Customer"):
        st.session_state.customers.append({"name": cname})
        save_data()
        st.success("Saved")

    for c in st.session_state.customers:
        st.write(c)

# ── ITEMS ─────────────────────────
if page == "Items":
    st.title("Items")

    name = st.text_input("Item Name")
    price = st.number_input("Price", min_value=0)

    if st.button("Add Item"):
        st.session_state.items_db.append({"name": name, "price": price})
        save_data()
        st.success("Item Saved")

    for i in st.session_state.items_db:
        st.write(i)
