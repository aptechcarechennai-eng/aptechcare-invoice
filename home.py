row1 = st.columns(3)
row2 = st.columns(3)

if row1[0].button("Create Invoice", use_container_width=True):
    st.session_state.page = "invoice"
    st.rerun()

if row1[1].button("Create Estimate", use_container_width=True):
    st.session_state.page = "estimate"
    st.rerun()

if row1[2].button("Credit Note", use_container_width=True):
    st.session_state.page = "credit"
    st.rerun()

if row2[0].button("Delivery", use_container_width=True):
    st.session_state.page = "delivery"
    st.rerun()

if row2[1].button("Purchase", use_container_width=True):
    st.session_state.page = "purchase"
    st.rerun()

if row2[2].button("Cash Flow", use_container_width=True):
    st.session_state.page = "cashflow"
    st.rerun()
