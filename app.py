import streamlit as st
import pandas as pd

st.set_page_config(page_title="Order-to-Cash | Exception Control", page_icon="📦", layout="wide")
st.title("📦 Order-to-Cash — Sales Order Exception Control")
st.caption("RedEarth Minerals | SAP S/4HANA concept prototype | Sample data only")

SAMPLE_DATA = [
    {"Sales Order":"SO1001","Customer":"ABC Industries","Exception":"Credit Limit","Priority":"High","Status":"Pending","Amount (£)":92500,"Days Open":4,"Owner":"Credit Team"},
    {"Sales Order":"SO1002","Customer":"XYZ Mining","Exception":"Pricing Error","Priority":"Medium","Status":"Pending","Amount (£)":18700,"Days Open":2,"Owner":"Sales Operations"},
    {"Sales Order":"SO1003","Customer":"Global Minerals","Exception":"Stock Shortage","Priority":"High","Status":"Resolved","Amount (£)":46300,"Days Open":0,"Owner":"Warehouse"},
    {"Sales Order":"SO1004","Customer":"Prime Steel","Exception":"Credit Limit","Priority":"High","Status":"Pending","Amount (£)":71200,"Days Open":6,"Owner":"Credit Team"},
    {"Sales Order":"SO1005","Customer":"Nova Metals","Exception":"Delivery Delay","Priority":"Medium","Status":"Pending","Amount (£)":28900,"Days Open":3,"Owner":"Logistics"},
    {"Sales Order":"SO1006","Customer":"Apex Ltd","Exception":"Pricing Error","Priority":"Low","Status":"Resolved","Amount (£)":8400,"Days Open":0,"Owner":"Sales Operations"},
    {"Sales Order":"SO1007","Customer":"Eastern Corp","Exception":"Stock Shortage","Priority":"High","Status":"Pending","Amount (£)":55800,"Days Open":8,"Owner":"Warehouse"},
    {"Sales Order":"SO1008","Customer":"BlueRock","Exception":"Credit Limit","Priority":"Medium","Status":"Pending","Amount (£)":31700,"Days Open":1,"Owner":"Credit Team"},
]

if "orders" not in st.session_state:
    st.session_state.orders = pd.DataFrame(SAMPLE_DATA)
if "action_log" not in st.session_state:
    st.session_state.action_log = []

df = st.session_state.orders
st.subheader("📊 Exception Control Dashboard")
open_mask = df["Status"].eq("Pending")
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Total Orders", len(df))
k2.metric("Open Exceptions", int(open_mask.sum()))
k3.metric("Resolved", int(df["Status"].eq("Resolved").sum()))
k4.metric("High Priority Open", int((df["Priority"].eq("High") & open_mask).sum()))
k5.metric("Open Value Exposure", f"£{df.loc[open_mask, 'Amount (£)'].sum():,.0f}")

st.divider()
st.subheader("🔎 Exception Queue")
f1,f2,f3,f4 = st.columns(4)
with f1: pf = st.selectbox("Priority", ["All","High","Medium","Low"])
with f2: sf = st.selectbox("Status", ["All","Pending","Resolved"])
with f3: ef = st.selectbox("Exception type", ["All"] + sorted(df["Exception"].unique().tolist()))
with f4: search = st.text_input("Search order/customer", placeholder="e.g. SO1001 or ABC")

filtered = df.copy()
if pf != "All": filtered = filtered[filtered["Priority"] == pf]
if sf != "All": filtered = filtered[filtered["Status"] == sf]
if ef != "All": filtered = filtered[filtered["Exception"] == ef]
if search.strip():
    q = search.strip().lower()
    filtered = filtered[filtered["Sales Order"].str.lower().str.contains(q) | filtered["Customer"].str.lower().str.contains(q)]

cols = ["Sales Order","Customer","Exception","Priority","Status","Amount (£)","Days Open","Owner"]
st.dataframe(filtered[cols], use_container_width=True, hide_index=True)
st.caption(f"Showing {len(filtered)} of {len(df)} orders.")
st.download_button("⬇️ Download filtered queue (CSV)", filtered[cols].to_csv(index=False).encode("utf-8"),
                   file_name="o2c_exception_queue.csv", mime="text/csv")

st.divider()
st.subheader("🎯 Sales Order Decision Panel")
if filtered.empty:
    st.info("No orders match these filters. Change one or more filters.")
else:
    selected = st.selectbox("Select an order to review", filtered["Sales Order"].tolist())
    idx = st.session_state.orders.index[st.session_state.orders["Sales Order"].eq(selected)][0]
    row = st.session_state.orders.loc[idx]
    left,right = st.columns(2)
    with left:
        st.markdown("#### Order details")
        st.write(f"**Sales order:** {row['Sales Order']}")
        st.write(f"**Customer:** {row['Customer']}")
        st.write(f"**Exception:** {row['Exception']}")
        st.write(f"**Owner:** {row['Owner']}")
    with right:
        st.markdown("#### Current position")
        st.write(f"**Priority:** {row['Priority']}")
        st.write(f"**Status:** {row['Status']}")
        st.write(f"**Days open:** {row['Days Open']}")
        st.write(f"**Amount:** £{row['Amount (£)']:,.2f}")

    # Transparent rules, not machine-learning AI.
    if row["Status"] == "Resolved":
        decision, recommendation = "Resolved", "No immediate action required. Retain resolution evidence for audit."
        reason = "This order is already marked as resolved in the demo data."
    elif row["Priority"] == "High":
        decision, recommendation = "Escalate / urgent review", "Contact the responsible team, verify the evidence, and resolve or escalate before proceeding where required."
        reason = f"Pending exception with High priority: {row['Exception']}."
    elif int(row["Days Open"]) >= 5:
        decision, recommendation = "Review ageing", "Ask the assigned owner for an update and agree a target resolution time."
        reason = f"The pending case has been open for {row['Days Open']} days."
    else:
        decision, recommendation = "Review with owner", "Validate order details and assign the next action to the responsible team."
        reason = f"Pending exception with {row['Priority']} priority."
    st.info(f"**Suggested decision: {decision}**\n\n{recommendation}\n\n**Reason:** {reason}")
    st.caption("This is transparent, rule-based decision support. A person must validate the case before taking business action.")

    b1,b2,b3 = st.columns(3)
    with b1:
        if st.button("✅ Mark as resolved", use_container_width=True, disabled=(row["Status"] == "Resolved")):
            st.session_state.orders.loc[idx, "Status"] = "Resolved"
            st.session_state.orders.loc[idx, "Days Open"] = 0
            st.session_state.action_log.append({"Time":pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),"Sales Order":selected,"Action":"Marked as resolved","Note":"Demo action; not written back to SAP"})
            st.rerun()
    with b2:
        if st.button("🚨 Escalate", use_container_width=True, disabled=(row["Status"] == "Resolved")):
            st.session_state.action_log.append({"Time":pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),"Sales Order":selected,"Action":"Escalated","Note":f"Suggested escalation for {row['Priority']} priority {row['Exception']} exception"})
            st.warning("Escalation recorded in this demo session. No real notification was sent.")
    with b3:
        if st.button("↩️ Reset demo data", use_container_width=True):
            st.session_state.orders = pd.DataFrame(SAMPLE_DATA)
            st.session_state.action_log = []
            st.rerun()

st.divider()
st.subheader("🧾 Demo Action Log")
if st.session_state.action_log:
    st.dataframe(pd.DataFrame(st.session_state.action_log), use_container_width=True, hide_index=True)
else:
    st.caption("No actions recorded yet in this session.")
st.divider()
st.caption("Limitations: sample data only; no authentication, database persistence, live SAP/OData integration, real notifications, approval workflow, or production security.")
