import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Order to Cash - Exception Control",
    page_icon="📦",
    layout="wide"
)

# ---------------- DATA ----------------
data = {
    "Sales Order": ["SO1001", "SO1002", "SO1003", "SO1004", "SO1005",
                    "SO1006", "SO1007", "SO1008"],
    "Customer": ["ABC Industries", "XYZ Mining", "Global Minerals",
                 "Prime Steel", "Nova Metals", "Apex Ltd",
                 "Eastern Corp", "BlueRock"],
    "Exception": ["Credit Limit", "Pricing Error", "Stock Shortage",
                  "Credit Limit", "Delivery Delay", "Pricing Error",
                  "Stock Shortage", "Credit Limit"],
    "Priority": ["High", "Medium", "High", "High",
                 "Medium", "Low", "High", "Medium"],
    "Status": ["Pending", "Pending", "Resolved", "Pending",
               "Pending", "Resolved", "Pending", "Pending"]
}

df = pd.DataFrame(data)

# ---------------- HEADER ----------------
st.title("📦 Order to Cash – Sales Order Exception Control")
st.caption(
    "RedEarth Minerals | SAP S/4HANA | Sales Order Exception Management"
)

st.divider()

# ---------------- DYNAMIC KPIs ----------------
st.markdown("### 📊 Exception Control Dashboard")

total_orders = len(df)
total_exceptions = len(df[df["Status"] == "Pending"])
pending = len(df[df["Status"] == "Pending"])
resolved = len(df[df["Status"] == "Resolved"])

high_priority = len(
    df[(df["Priority"] == "High") & (df["Status"] == "Pending")]
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Orders", total_orders)
col2.metric("Open Exceptions", total_exceptions)
col3.metric("Resolved", resolved)
col4.metric("High Priority", high_priority)

st.divider()

# ---------------- FILTERS ----------------
st.markdown("### 🔎 Exception Queue")

col1, col2, col3 = st.columns(3)

with col1:
    priority_filter = st.selectbox(
        "Priority",
        ["All", "High", "Medium", "Low"]
    )

with col2:
    status_filter = st.selectbox(
        "Status",
        ["All", "Pending", "Resolved"]
    )

with col3:
    exception_filter = st.selectbox(
        "Exception Type",
        ["All"] + sorted(df["Exception"].unique().tolist())
    )

filtered_df = df.copy()

if priority_filter != "All":
    filtered_df = filtered_df[
        filtered_df["Priority"] == priority_filter
    ]

if status_filter != "All":
    filtered_df = filtered_df[
        filtered_df["Status"] == status_filter
    ]

if exception_filter != "All":
    filtered_df = filtered_df[
        filtered_df["Exception"] == exception_filter
    ]

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ---------------- DECISION PANEL ----------------
st.markdown("### 🎯 Sales Order Decision Panel")

if len(filtered_df) > 0:

    selected_order = st.selectbox(
        "Select Sales Order to Review",
        filtered_df["Sales Order"].tolist()
    )

    row = df[df["Sales Order"] == selected_order].iloc[0]

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Sales Order:** {row['Sales Order']}")
        st.write(f"**Customer:** {row['Customer']}")
        st.write(f"**Exception:** {row['Exception']}")

    with col2:
        st.write(f"**Priority:** {row['Priority']}")
        st.write(f"**Status:** {row['Status']}")

    # ---------------- DECISION LOGIC ----------------
    if row["Status"] == "Resolved":
        recommendation = "No immediate action required."
        decision = "Resolved"
    elif row["Priority"] == "High":
        recommendation = (
            "Urgent attention required. Review the exception "
            "and resolve it before order processing continues."
        )
        decision = "Escalate"
    else:
        recommendation = (
            "Review the exception and assign the appropriate "
            "team for resolution."
        )
        decision = "Review"

    st.markdown("#### 🤖 AI Decision Recommendation")

    st.info(
        f"**Decision: {decision}**\n\n"
        f"{recommendation}\n\n"
        f"Reason: {row['Exception']} exception with "
        f"{row['Priority']} priority."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Mark Complete"):
            st.success(
                f"{selected_order} marked for completion."
            )

    with col2:
        if st.button("🚨 Escalate"):
            st.warning(
                f"{selected_order} escalated to the responsible team."
            )

else:
    st.warning("No orders match the selected filters.")

st.divider()

st.caption(
    "Decision Support Cockpit | SAP S/4HANA | Order-to-Cash"
)