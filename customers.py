import streamlit as st

def render():
    st.markdown('<p class="page-title">👥 Customers</p>', unsafe_allow_html=True)

    # Store customers as list of dicts
    if not isinstance(st.session_state.customers[0] if st.session_state.customers else None, dict):
        st.session_state.customers = [{"name": c, "email": "", "phone": "", "address": ""} for c in st.session_state.customers]

    customers = st.session_state.customers

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Add Customer", type="primary", use_container_width=True):
            st.session_state.show_add_customer = True

    search = st.text_input("🔍 Search customers", label_visibility="collapsed", placeholder="Name, email...")
    filtered = [c for c in customers if not search or search.lower() in c["name"].lower()]

    for idx, cust in enumerate(filtered):
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            invoices = [i for i in st.session_state.invoices if i["customer"] == cust["name"]]
            total = sum(i["amount"] for i in invoices)
            st.markdown(f"""
            <div style="padding:4px 0;">
              <div style="font-weight:700;font-size:14px;">{cust['name']}</div>
              <div style="font-size:12px;color:#6b7280;">{cust.get('email','')} • {len(invoices)} invoices • ₹{total:,} total</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            if st.button("✏️ Edit", key=f"edit_cust_{idx}"):
                st.session_state.edit_customer_idx = idx
        with col3:
            if st.button("🗑️", key=f"del_cust_{idx}"):
                customers.pop(idx)
                st.rerun()
        st.markdown("<hr style='margin:4px 0;border-color:#f3f4f6;'>", unsafe_allow_html=True)

    # ── Add Customer Form ─────────────────────────────────────────
    if st.session_state.get("show_add_customer"):
        st.markdown("---")
        st.markdown("### ➕ New Customer")
        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name *")
                phone = st.text_input("Phone")
            with col2:
                email = st.text_input("Email")
                address = st.text_input("Address")

            col_save, col_close = st.columns(2)
            with col_save:
                save = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
            with col_close:
                close = st.form_submit_button("✕ Close", use_container_width=True)

            if save and name:
                customers.append({"name": name, "email": email, "phone": phone, "address": address})
                st.session_state.show_add_customer = False
                st.success(f"✅ '{name}' added!")
                st.rerun()
            if close:
                st.session_state.show_add_customer = False
                st.rerun()
