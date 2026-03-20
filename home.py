import streamlit as st

def render():
    invoices = st.session_staimport streamlit as st

def render():
    invoices = st.session_state.invoices

    st.title("👋 Welcome back!")
    st.caption("AP Tech Care — Smart Tech Solutions")

    # ── Stats ──────────────────────────────────────────────────────
    total       = len(invoices)
    paid_amt    = sum(i["amouimport streamlit as st


def render():
    invoices = st.session_state.invoices

    st.title("Welcome back!")
    st.caption("AP Tech Care - Smart Tech Solutions")

    total = len(invoices)
    paid_amt = sum(i["amount"] for i in invoices if i["status"] == "paid")
    pending_amt = sum(i["amount"] for i in invoices if i["status"] != "paid")
    overdue_n = len([i for i in invoices if i["status"] == "overdue"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Invoices", total)
    c2.metric("Paid", "Rs." + str(int(paid_amt)))
    c3.metric("Pending", "Rs." + str(int(pending_amt)))
    c4.metric("Overdue", overdue_n)

    st.divider()

    st.subheader("Quick Actions")
    q1, q2, q3, q4, q5, q6 = st.columns(6)

    with q1:
        if st.button("Invoice", key="qa_invoice", use_container_width=True):
            st.session_state.page = "invoice"
            st.rerun()
    with q2:
        if st.button("Estimate", key="qa_estimate", use_container_width=True):
            st.session_state.page = "estimate"
            st.rerun()
    with q3:
        if st.button("Credit", key="qa_credit", use_container_width=True):
            st.session_state.page = "credit"
            st.rerun()
    with q4:
        if st.button("Delivery", key="qa_delivery", use_container_width=True):
            st.session_state.page = "delivery"
            st.rerun()
    with q5:
        if st.button("Purchase", key="qa_purchase", use_container_width=True):
            st.session_state.page = "purchase"
            st.rerun()
    with q6:
        if st.button("Cash Flow", key="qa_cashflow", use_container_width=True):
            st.session_state.page = "cashflow"
            st.rerun()

    st.divider()

    left, right = st.columns([3, 1])

    with left:
        st.subheader("Pending List")
        pending = [i for i in invoices if i["status"] != "paid"]

        if not pending:
            st.success("All invoices are paid!")
        else:
            for inv in pending[:5]:
                s = inv["status"]
                with st.container(border=True):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown("**" + inv["customer"] + "**")
                        st.caption(inv["id"] + " | Due: " + inv["due"])
                        if s == "overdue":
                            st.error("Overdue - Payment Pending")
                    with col_b:
                        st.markdown("**Rs." + str(int(inv["amount"])) + "**")
                        st.caption(s.title())

        if st.button("View All Invoices", key="home_view_all", use_container_width=True):
            st.session_state.page = "invoice"
            st.rerun()

    with right:
        st.subheader("Summary")

        statuses = {}
        for inv in invoices:
            statuses[inv["status"]] = statuses.get(inv["status"], 0) + 1

        for s, count in statuses.items():
            st.write(s.title() + ": " + str(count))

        st.divider()

        cust_count = len(st.session_state.customers)
        items_count = len(st.session_state.items_db)

        st.info("Customers: " + str(cust_count))
        st.success("Items: " + str(items_count))

        if st.button("Add Customer", use_container_width=True, key="home_add_cust"):
            st.session_state.page = "customers"
            st.rerun()

        if st.button("Add Item", use_container_width=True, key="home_add_item"):
            st.session_state.page = "items"
            st.rerun()nt"] for i in invoices if i["status"] == "paid")
    pending_amt = sum(i["amount"] for i in invoices if i["status"] != "paid")
    overdue_n   = len([i for i in invoices if i["status"] == "overdue"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📄 Total", total)
    c2.metric("✅ Paid", f"₹{paid_amt/1000:.1f}K")
    c3.metric("⏳ Pending", f"₹{pending_amt/1000:.1f}K")
    c4.metric("⚠️ Overdue", overdue_n)

    st.divider()

    # ── Quick Actions ──────────────────────────────────────────────
    st.subheader("⚡ Quick Actions")
    q1, q2, q3, q4, q5, q6 = st.columns(6)
    for col, pid, label in [
        (q1,"invoice","📄 Invoice"),
        (q2,"estimate","📋 Estimate"),
        (q3,"credit","💳 Credit"),
        (q4,"delivery","🚚 Delivery"),
        (q5,"purchase","🛒 Purchase"),
        (q6,"cashflow","📊 Cash Flow"),
    ]:
        with col:
            if st.button(label, key=f"qa_{pid}", use_container_width=True):
                st.session_state.page = pid
                st.rerun()

    st.divider()

    # ── Pending List + Summary ─────────────────────────────────────
    left, right = st.columns([3, 1])

    with left:
        st.subheader("📋 Pending List")
        pending = [i for i in invoices if i["status"] != "paid"]

        if not pending:
            st.success("🎉 All invoices are paid!")
        else:
            for inv in pending[:5]:
                s = inv["status"]
                emoji = {"overdue":"⚠️","sent":"📤","draft":"✏️","read":"👁️"}.get(s,"•")
                with st.container(border=True):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"**{emoji} {inv['customer']}**")
                        st.caption(f"{inv['id']} • Due: {inv['due']}")
                        if s == "overdue":
                            st.error("⚠️ Overdue — Payment Pending")
                    with col_b:
                        st.markdown(f"**₹{inv['amount']:,.0f}**")
                        status_colors = {
                            "overdue": "🔴", "sent": "🔵",
                            "draft": "⚪", "read": "🟡"
                        }
                        st.caption(f"{status_colors.get(s,'⚪')} {s.title()}")

        if st.button("View All Invoices →", key="home_view_all", use_container_width=True):
            st.session_state.page = "invoice"
            st.rerun()

    with right:
        st.subheader("📊 Summary")

        # Status breakdown
        statuses = {}
        for inv in invoices:
            statuses[inv["status"]] = statuses.get(inv["status"], 0) + 1

        icons_map = {"paid":"✅","sent":"📤","overdue":"⚠️","draft":"✏️","read":"👁️"}
        for s, count in statuses.items():
            col_x, col_y = st.columns([3,1])
            col_x.write(f"{icons_map.get(s,'•')} {s.title()}")
            col_y.write(f"**{count}**")

        st.divider()

        cust_count  = len(st.session_state.customers)
        items_count = len(st.session_state.items_db)

        st.info(f"👥 Customers: **{cust_count}**")
        st.success(f"📦 Items: **{items_count}**")

        if st.button("➕ Add Customer", use_container_width=True, key="home_add_cust"):
            st.session_state.page = "customers"
            st.rerun()
        if st.button("➕ Add Item", use_container_width=True, key="home_add_item"):
            st.session_state.page = "items"
            st.rerun()te.invoices

    st.markdown("## 👋 Welcome back!")
    st.caption("AP Tech Care — Smart Tech Solutions")

    # Stats
    total       = len(invoices)
    paid_amt    = sum(i["amount"] for i in invoices if i["status"] == "paid")
    pending_amt = sum(i["amount"] for i in invoices if i["status"] != "paid")
    overdue_n   = len([i for i in invoices if i["status"] == "overdue"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📄 Total Invoices", total)
    c2.metric("✅ Paid", f"₹{paid_amt/1000:.1f}K")
    c3.metric("⏳ Pending", f"₹{pending_amt/1000:.1f}K")
    c4.metric("⚠️ Overdue", overdue_n)

    st.markdown("---")

    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    q1, q2, q3, q4, q5, q6 = st.columns(6)
    for col, pid, label in [
        (q1,"invoice","📄 Invoice"),(q2,"estimate","📋 Estimate"),
        (q3,"credit","💳 Credit"),(q4,"delivery","🚚 Delivery"),
        (q5,"purchase","🛒 Purchase"),(q6,"cashflow","📊 Cash Flow")
    ]:
        with col:
            if st.button(label, key=f"qa_{pid}", use_container_width=True):
                st.session_state.page = pid
                st.rerun()

    st.markdown("---")

    left, right = st.columns([2, 1])

    with left:
        st.markdown("### 📋 Pending List")
        pending = [i for i in invoices if i["status"] != "paid"]
        if not pending:
            st.success("🎉 All invoices are paid!")
        else:
            for inv in pending[:5]:
                s = inv["status"]
                colors = {
                    "overdue": ("#FEE2E2","#991B1B","⚠️"),
                    "sent":    ("#DBEAFE","#1E40AF","📤"),
                    "draft":   ("#F3F4F6","#374151","✎"),
                    "read":    ("#FEF3C7","#92400E","👁"),
                }
                bg, clr, icon = colors.get(s, ("#F3F4F6","#374151","•"))
                overdue_html = "<div style='font-size:11px;color:#EF4444;font-weight:700;margin-top:3px;'>⚠ Overdue — Payment Pending</div>" if s=="overdue" else ""
                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e5e7eb;border-left:4px solid {clr};
                     border-radius:12px;padding:14px 18px;margin-bottom:8px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                      <div style="font-weight:700;font-size:14px;">{icon} {inv['customer']}</div>
                      <div style="font-size:12px;color:#6b7280;margin-top:3px;">{inv['id']} • Due: {inv['due']}</div>
                      {overdue_html}
                    </div>
                    <div style="text-align:right;">
                      <div style="font-weight:900;font-size:16px;">₹{inv['amount']:,.0f}</div>
                      <div style="background:{bg};color:{clr};border-radius:999px;padding:2px 10px;
                           font-size:11px;font-weight:700;display:inline-block;margin-top:4px;">{s.title()}</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

        if st.button("View All Invoices →", key="home_view_all"):
            st.session_state.page = "invoice"
            st.rerun()

    with right:
        st.markdown("### 📊 Summary")
        statuses = {}
        for inv in invoices:
            statuses[inv["status"]] = statuses.get(inv["status"], 0) + 1
        icons_map = {"paid":"✅","sent":"📤","overdue":"⚠️","draft":"✎","read":"👁"}
        for s, count in statuses.items():
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:9px 14px;
                 background:#f8f9fa;border:1px solid #e5e7eb;border-radius:8px;margin-bottom:6px;">
              <span style="font-size:13px;">{icons_map.get(s,"•")} {s.title()}</span>
              <span style="font-weight:700;">{count}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        cust_count  = len(st.session_state.customers)
        items_count = len(st.session_state.items_db)
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:12px;">
          <div style="display:flex;justify-content:space-between;padding:10px 14px;background:#EFF6FF;border-radius:8px;">
            <span>👥 Customers</span><span style="font-weight:700;color:#1D4ED8;">{cust_count}</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:10px 14px;background:#F0FDF4;border-radius:8px;">
            <span>📦 Items</span><span style="font-weight:700;color:#166534;">{items_count}</span>
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("➕ Add Customer", use_container_width=True, key="home_add_cust"):
            st.session_state.page = "customers"; st.rerun()
        if st.button("➕ Add Item", use_container_width=True, key="home_add_item"):
            st.session_state.page = "items"; st.rerun()
