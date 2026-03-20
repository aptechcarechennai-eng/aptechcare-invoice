import streamlit as st


def render():
    # ✅ Session state safety
    if "invoices" not in st.session_state:
        st.session_state.invoices = []

    if "customers" not in st.session_state:
        st.session_state.customers = []

    if "items_db" not in st.session_state:
        st.session_state.items_db = []

    invoices = st.session_state.invoices

    st.title("Welcome back!")
    st.caption("AP Tech Care - Smart Tech Solutions")

    # ✅ Safe calculations
    total = len(invoices)
    paid_amt = sum(i.get("amount", 0) for i in invoices if i.get("status") == "paid")
    pending_amt = sum(i.get("amount", 0) for i in invoices if i.get("status") != "paid")
    overdue_n = len([i for i in invoices if i.get("status") == "overdue"])

    # ✅ Metrics with proper currency
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Invoices", total)
    c2.metric("Paid", f"₹ {paid_amt:,.0f}")
    c3.metric("Pending", f"₹ {pending_amt:,.0f}")
    c4.metric("Overdue", overdue_n)

    st.divider()
    st.subheader("Quick Actions")

    # ✅ Buttons
    q1, q2, q3, q4, q5, q6 = st.columns(6)

    with q1:
        if st.button("Create Invoice", use_container_width=True):
            st.session_state.page = "invoice"
            st.rerun()

    with q2:
        if st.button("Create Estimate", use_container_width=True):
            st.session_state.page = "estimate"
            st.rerun()

    with q3:
        if st.button("Credit Note", use_container_width=True):
            st.session_state.page = "credit"
            st.rerun()

    with q4:
        if st.button("Delivery", use_container_width=True):
            st.session_state.page = "delivery"
            st.rerun()

    with q5:
        if st.button("Purchase", use_container_width=True):
            st.session_state.page = "purchase"
            st.rerun()

    with q6:
        if st.button("Cash Flow", use_container_width=True):
            st.session_state.page = "cashflow"
            st.rerun()

    st.divider()

    left, right = st.columns([3, 1])

    # ✅ Pending list
    with left:
        st.subheader("Pending List")

        pending = [i for i in invoices if i.get("status") != "paid"]

        if not pending:
            st.success("All invoices are paid!")
        else:
            for inv in pending[:5]:
                s = inv.get("status", "pending")

                with st.container(border=True):
                    col_a, col_b = st.columns([3, 1])

                    with col_a:
                        st.markdown(f"**{inv.get('customer', 'Unknown')}**")
                        st.caption(f"{inv.get('id', '-') } | Due: {inv.get('due', '-')}")
                        
                        if s == "overdue":
                            st.error("Overdue - Payment Pending")

                    with col_b:
                        st.markdown(f"**₹ {inv.get('amount', 0):,.0f}**")

                        # ✅ Status colors
                        if s == "paid":
                            st.success("Paid")
                        elif s == "pending":
                            st.warning("Pending")
                        elif s == "overdue":
                            st.error("Overdue")

        if st.button("View All Invoices", use_container_width=True):
            st.session_state.page = "invoice"
            st.rerun()

    # ✅ Summary section
    with right:
        st.subheader("Summary")

        statuses = {}
        for inv in invoices:
            s = inv.get("status", "pending")
            statuses[s] = statuses.get(s, 0) + 1

        for s, count in statuses.items():
            st.write(f"{s.title()}: {count}")

        st.divider()

        st.info(f"Customers: {len(st.session_state.customers
