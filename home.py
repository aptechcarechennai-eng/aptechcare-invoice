import streamlit as st
from datetime import datetime, date

def render():
    invoices = st.session_state.invoices
    settings = st.session_state.settings

    # ── Title ─────────────────────────────────────────────────────
    st.markdown("""
    <p class="page-title">Welcome back! 👋</p>
    <p class="page-sub">AP Tech Care — Smart Tech Solutions</p>
    """, unsafe_allow_html=True)

    # ── Stats ─────────────────────────────────────────────────────
    total = len(invoices)
    paid_amt   = sum(i["amount"] for i in invoices if i["status"] == "paid")
    pending_amt = sum(i["amount"] for i in invoices if i["status"] != "paid")
    overdue_n  = len([i for i in invoices if i["status"] == "overdue"])
    draft_n    = len([i for i in invoices if i["status"] == "draft"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📄 Total Invoices", total)
    with c2:
        st.metric("✅ Paid", f"₹{paid_amt/1000:.1f}K")
    with c3:
        st.metric("⏳ Pending", f"₹{pending_amt/1000:.1f}K")
    with c4:
        st.metric("⚠️ Overdue", overdue_n)

    st.markdown("<div class='ap-divider'></div>", unsafe_allow_html=True)

    # ── Quick Actions ─────────────────────────────────────────────
    st.markdown("<p style='font-weight:800;font-size:16px;margin-bottom:12px;'>Quick Actions</p>", unsafe_allow_html=True)

    q1, q2, q3, q4, q5, q6 = st.columns(6)
    actions = [
        (q1, "invoice",   "📄", "Invoice"),
        (q2, "estimate",  "📋", "Estimate"),
        (q3, "credit",    "💳", "Credit Note"),
        (q4, "delivery",  "🚚", "Delivery"),
        (q5, "purchase",  "🛒", "Purchase"),
        (q6, "cashflow",  "📊", "Cash Flow"),
    ]
    for col, pid, icon, label in actions:
        with col:
            if st.button(f"{icon}\n\n{label}", key=f"qa_{pid}", use_container_width=True):
                st.session_state.page = pid
                st.rerun()

    st.markdown("<div class='ap-divider'></div>", unsafe_allow_html=True)

    # ── Two columns: Pending + Summary ────────────────────────────
    left, right = st.columns([2, 1])

    with left:
        st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <span style="font-weight:800;font-size:16px;">📋 Pending List</span>
        </div>
        """, unsafe_allow_html=True)

        pending = [i for i in invoices if i["status"] != "paid"]
        if not pending:
            st.markdown('<div class="ap-card" style="text-align:center;color:#6b7280;padding:32px;">🎉 All invoices are paid!</div>', unsafe_allow_html=True)
        else:
            for inv in pending[:5]:
                is_overdue = inv["status"] == "overdue"
                status_icon = "⚠️" if is_overdue else "→"
                color = "#EF4444" if is_overdue else "#6B7280"
                overdue_tag = f'<div style="font-size:11px;color:#EF4444;font-weight:700;margin-top:2px;">⚠ Overdue — Payment Pending</div>' if is_overdue else ""

                st.markdown(f"""
                <div class="ap-card" style="margin-bottom:8px;cursor:pointer;">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                      <div class="inv-customer">{status_icon} {inv["customer"]}</div>
                      <div class="inv-meta">{inv["id"]} • Due: {inv["due"]}</div>
                      {overdue_tag}
                    </div>
                    <div style="text-align:right;">
                      <div class="inv-amount">₹{inv["amount"]:,.0f}</div>
                      <span class="badge-{inv['status']}" style="font-size:11px;">{inv["status"].title()}</span>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        if st.button("View All Invoices →", key="home_view_all"):
            st.session_state.page = "invoice"
            st.rerun()

    with right:
        st.markdown("<p style='font-weight:800;font-size:16px;margin-bottom:12px;'>📊 Summary</p>", unsafe_allow_html=True)

        # Status breakdown
        statuses = {}
        for inv in invoices:
            statuses[inv["status"]] = statuses.get(inv["status"], 0) + 1

        for status, count in statuses.items():
            icon = {"paid":"✅","sent":"📤","overdue":"⚠️","draft":"✎","read":"👁"}.get(status, "•")
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:8px 12px;background:var(--card,#fff);border:1px solid #e5e7eb;border-radius:8px;margin-bottom:6px;">
              <span style="font-size:13px;">{icon} {status.title()}</span>
              <span style="font-weight:700;font-size:13px;">{count}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='ap-divider'></div>", unsafe_allow_html=True)

        # Customers count
        cust_count = len(st.session_state.customers)
        items_count = len(st.session_state.items_db)
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:8px;">
          <div style="display:flex;justify-content:space-between;padding:8px 12px;background:#EFF6FF;border-radius:8px;">
            <span style="font-size:13px;">👥 Customers</span>
            <span style="font-weight:700;font-size:13px;color:#1D4ED8;">{cust_count}</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:8px 12px;background:#F0FDF4;border-radius:8px;">
            <span style="font-size:13px;">📦 Items</span>
            <span style="font-weight:700;font-size:13px;color:#166534;">{items_count}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # New customer / item quick-add
        st.markdown("<div class='ap-divider'></div>", unsafe_allow_html=True)
        if st.button("➕ Add Customer", use_container_width=True, key="home_add_cust"):
            st.session_state.page = "customers"
            st.rerun()
        if st.button("➕ Add Item", use_container_width=True, key="home_add_item"):
            st.session_state.page = "items"
            st.rerun()
