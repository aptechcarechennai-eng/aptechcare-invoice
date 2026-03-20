import streamlit as st


def render():
    # Session state safety
    if "invoices" not in st.session_state:
        st.session_state.invoices = []

    if "customers" not in st.session_state:
        st.session_state.customers = []

    if "items_db" not in st.session_state:
        st.session_state.items_db = []

    invoices = st.session_state.invoices

    st.title("Welcome back!")
    st.caption("AP Tech Care - Smart Tech Solutions")

    # Calculations
    total = len(invoices)
    paid_amt = sum(i.get("amount", 0) for i in invoices if i.get("status") == "paid")
    pending_amt = sum(i.get("amount", 0) for i in invoices if i.get("status") != "paid")
    overdue_n = len([i for i in invoices if i.get("status") == "overdue"])

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Invoices", total)
    c2.metric("Paid", f"₹ {paid_amt:,.0
