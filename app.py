✅ FIXED VERSION - DATA PERSIST + MOBILE SIDEBAR FIX

import streamlit as st import json, os from datetime import datetime, date

st.set_page_config(page_title="AP Tech Care", layout="wide")

DATA_FILE = "data.json"

── LOAD / SAVE LOCAL DATA ─────────────────────────

def load_data(): if os.path.exists(DATA_FILE): with open(DATA_FILE, "r") as f: return json.load(f) return {"invoices": [], "customers": []}

def save_data(data): with open(DATA_FILE, "w") as f: json.dump(data, f)

── INIT ─────────────────────────

data = load_data()

if "invoices" not in st.session_state: st.session_state.invoices = data["invoices"]

if "customers" not in st.session_state: st.session_state.customers = data["customers"]

── MOBILE SIDEBAR FIX ─────────────────────────

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
</style>""", unsafe_allow_html=True)

── SIDEBAR ─────────────────────────

with st.sidebar: st.title("AP Tech Care") page = st.radio("Menu", ["Home", "Add Invoice", "Customers"])

── HOME ─────────────────────────

if page == "Home": st.title("Dashboard") st.write(f"Total Invoices: {len(st.session_state.invoices)}")

for inv in st.session_state.invoices:
    st.write(inv)

── ADD INVOICE ─────────────────────────

if page == "Add Invoice": st.title("Create Invoice")

name = st.text_input("Customer Name")
amount = st.number_input("Amount", min_value=0)

if st.button("Save Invoice"):
    new_inv = {
        "customer": name,
        "amount": amount,
        "date": str(date.today())
    }
    st.session_state.invoices.append(new_inv)

    # ✅ SAVE TO FILE
    save_data({
        "invoices": st.session_state.invoices,
        "customers": st.session_state.customers
    })

    st.success("Saved! (Will not delete on refresh)")

── CUSTOMERS ─────────────────────────

if page == "Customers": st.title("Customers")

cname = st.text_input("Customer Name")

if st.button("Add Customer"):
    st.session_state.customers.append({"name": cname})

    # ✅ SAVE
    save_data({
        "invoices": st.session_state.invoices,
        "customers": st.session_state.customers
    })

    st.success("Customer saved!")

for c in st.session_state.customers:
    st.write
