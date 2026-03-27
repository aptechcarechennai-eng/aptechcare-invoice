
✅ FIXED VERSION (Key stability fixes applied)

Changes:

1. Removed unnecessary st.rerun() from navigation

2. Added st.stop() after navigation clicks

3. Removed rerun loops from text inputs

4. Safe session handling

import streamlit as st from datetime import datetime, date, timedelta import base64, urllib.parse, json, os

st.set_page_config(page_title="AP Tech Care", layout="wide")

---------------- SESSION INIT ----------------

if "page" not in st.session_state: st.session_state.page = "home" if "invoices" not in st.session_state: st.session_state.invoices = [] if "customers" not in st.session_state: st.session_state.customers = []

---------------- NAVIGATION FIX ----------------

def nav(p): st.session_state.page = p st.session_state.selected_inv = None st.session_state.inv_action = None

---------------- SIDEBAR ----------------

with st.sidebar: st.title("AP Tech Care")

if st.button("🏠 Home"):
    nav("home")
    st.stop()

if st.button("📄 Invoice"):
    nav("invoice")
    st.stop()

if st.button("⚙️ Settings"):
    nav("settings")
    st.stop()

if st.button("🚪 Logout"):
    st.session_state.clear()
    st.stop()

---------------- HOME ----------------

if st.session_state.page == "home": st.title("Dashboard") st.write("Welcome to AP Tech Care App")

---------------- INVOICE ----------------

elif st.session_state.page == "invoice": st.title("Invoices")

name = st.text_input("Customer Name")
amount = st.number_input("Amount", min_value=0)

if st.button("Save Invoice"):
    if name:
        st.session_state.invoices.append({"name": name, "amount": amount})
        st.success("Saved ✅")

for inv in st.session_state.invoices:
    st.write(inv)

---------------- SETTINGS ----------------

elif st.session_state.page == "settings": st.title("Settings")

cname = st.text_input("Company Name", "AP Tech Care")

if st.button("Save"):
    st.success("Saved (local)")

---------------- END ----------------
