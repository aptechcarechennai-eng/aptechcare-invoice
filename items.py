import streamlit as st

# ── ITEMS ──────────────────────────────────────────────────────
def render():
    st.markdown('<p class="page-title">📦 Items</p>', unsafe_allow_html=True)

    items = st.session_state.items_db

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Add Item", type="primary", use_container_width=True):
            st.session_state.show_add_item = True

    search = st.text_input("🔍 Search items", placeholder="Item name or code...", label_visibility="collapsed")
    filtered = [i for i in items if not search or search.lower() in i["name"].lower() or search.lower() in i["code"].lower()]

    for idx, item in enumerate(filtered):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.markdown(f"""
            <div style="padding:4px 0;">
              <div style="font-weight:700;font-size:14px;">{item['name']}</div>
              <div style="font-size:12px;color:#6b7280;">Code: {item['code']} • {item.get('unit','')}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='padding-top:8px;font-weight:700;color:#00C896;'>₹{item['price']:,}</div>", unsafe_allow_html=True)
        with col3:
            if st.button("✏️", key=f"edit_item_{idx}"):
                st.session_state.edit_item_idx = idx
        with col4:
            if st.button("🗑️", key=f"del_item_{idx}"):
                items.pop(idx)
                st.rerun()
        st.markdown("<hr style='margin:4px 0;border-color:#f3f4f6;'>", unsafe_allow_html=True)

    # ── Add Item Form ─────────────────────────────────────────────
    if st.session_state.get("show_add_item"):
        st.markdown("---")
        st.markdown("### ➕ New Item")
        with st.form("add_item_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Item Name *")
                price = st.number_input("Price ₹ *", min_value=0)
            with col2:
                code = st.text_input("Product Code")
                unit = st.text_input("Unit Type", value="per unit")
            desc = st.text_area("Description (up to 10,000 characters)", max_chars=10000)

            col_save, col_close = st.columns(2)
            with col_save:
                save = st.form_submit_button("💾 Save Item", type="primary", use_container_width=True)
            with col_close:
                close = st.form_submit_button("✕ Close", use_container_width=True)

            if save and name:
                items.append({"name": name, "code": code, "price": price, "unit": unit, "desc": desc})
                st.session_state.show_add_item = False
                st.success(f"✅ '{name}' added!")
                st.rerun()
            if close:
                st.session_state.show_add_item = False
                st.rerun()
