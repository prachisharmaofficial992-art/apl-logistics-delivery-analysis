"""
Delivery Performance, Delay Risk, and Logistics Efficiency Analysis
APL Logistics (KWE Group) — Global Supply Chain Operations
Streamlit Dashboard
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="APL Logistics | Delivery Performance & Delay Risk Dashboard",
    page_icon="🚚",
    layout="wide",
)

# ---------------------------------------------------------
# Data Loading
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("APL_Logistics_cleaned_slim.csv")
    return df

df = load_data()

# ---------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------
st.sidebar.title("🔎 Filters")

shipping_modes = st.sidebar.multiselect(
    "Shipping Mode",
    options=sorted(df["Shipping Mode"].dropna().unique()),
    default=sorted(df["Shipping Mode"].dropna().unique()),
)

markets = st.sidebar.multiselect(
    "Market",
    options=sorted(df["Market"].dropna().unique()),
    default=sorted(df["Market"].dropna().unique()),
)

regions = st.sidebar.multiselect(
    "Order Region",
    options=sorted(df["Order Region"].dropna().unique()),
    default=sorted(df["Order Region"].dropna().unique()),
)

segments = st.sidebar.multiselect(
    "Customer Segment",
    options=sorted(df["Customer Segment"].dropna().unique()),
    default=sorted(df["Customer Segment"].dropna().unique()),
)

# Apply filters
fdf = df[
    df["Shipping Mode"].isin(shipping_modes)
    & df["Market"].isin(markets)
    & df["Order Region"].isin(regions)
    & df["Customer Segment"].isin(segments)
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(fdf):,}** of {len(df):,} orders")

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.title("🚚 Delivery Performance, Delay Risk & Logistics Efficiency")
st.caption("Global Supply Chain Operations — APL Logistics (KWE Group)")

# ---------------------------------------------------------
# KPI Row
# ---------------------------------------------------------
on_time_rate = (fdf["Late_delivery_risk"] == 0).mean() * 100
avg_delay = fdf["Delivery Delay Gap"].mean()
late_risk_ratio = fdf["Late_delivery_risk"].mean() * 100
total_orders = len(fdf)

k1, k2, k3, k4 = st.columns(4)
k1.metric("On-Time Delivery Rate", f"{on_time_rate:.1f}%")
k2.metric("Average Delivery Delay", f"{avg_delay:.2f} days")
k3.metric("Late Delivery Risk Ratio", f"{late_risk_ratio:.1f}%")
k4.metric("Total Orders", f"{total_orders:,}")

st.markdown("---")

# ---------------------------------------------------------
# Tabs for Dashboard Modules
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📦 Delivery Performance Overview",
        "⚠️ Delay Risk Analysis",
        "🚛 Shipping Mode Comparison",
        "🌍 Regional & Segment Diagnostics",
    ]
)

# ---------------- TAB 1: Overview ----------------
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        status_counts = fdf["Delay Classification"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig = px.pie(
            status_counts, names="Status", values="Count",
            title="On-time vs Delayed vs Early Deliveries",
            color="Status",
            color_discrete_map={"On-time": "#2ecc71", "Delayed": "#e74c3c", "Early": "#3498db"},
            hole=0.4,
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        delivery_status_counts = fdf["Delivery Status"].value_counts().reset_index()
        delivery_status_counts.columns = ["Delivery Status", "Count"]
        fig2 = px.bar(
            delivery_status_counts, x="Delivery Status", y="Count",
            title="Delivery Status Breakdown", color="Delivery Status",
            text="Count",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Average Delay Scorecard by Category")
    cat_delay = (
        fdf.groupby("Category Name")["Delivery Delay Gap"]
        .mean()
        .sort_values(ascending=False)
        .head(15)
        .reset_index()
    )
    fig3 = px.bar(
        cat_delay, x="Delivery Delay Gap", y="Category Name",
        orientation="h", title="Top 15 Categories by Average Delay (days)",
        color="Delivery Delay Gap", color_continuous_scale="RdYlGn_r",
    )
    st.plotly_chart(fig3, use_container_width=True)

# ---------------- TAB 2: Delay Risk ----------------
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        fig4 = px.histogram(
            fdf, x="Delivery Delay Gap", nbins=15,
            title="Delay Gap Distribution",
            color_discrete_sequence=["#e67e22"],
        )
        st.plotly_chart(fig4, use_container_width=True)

    with c2:
        risk_by_mode = (
            fdf.groupby("Shipping Mode")["Late_delivery_risk"]
            .mean()
            .mul(100)
            .sort_values(ascending=False)
            .reset_index()
        )
        fig5 = px.bar(
            risk_by_mode, x="Shipping Mode", y="Late_delivery_risk",
            title="Late Delivery Risk (%) by Shipping Mode",
            text_auto=".1f", color="Late_delivery_risk",
            color_continuous_scale="Reds",
        )
        fig5.update_yaxes(title="Late Delivery Risk (%)")
        st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Late Delivery Risk Distribution by Region")
    risk_region = (
        fdf.groupby("Order Region")["Late_delivery_risk"]
        .mean()
        .mul(100)
        .sort_values(ascending=False)
        .reset_index()
    )
    fig6 = px.bar(
        risk_region, x="Order Region", y="Late_delivery_risk",
        title="Late Delivery Risk (%) by Order Region",
        color="Late_delivery_risk", color_continuous_scale="OrRd",
    )
    fig6.update_yaxes(title="Late Delivery Risk (%)")
    st.plotly_chart(fig6, use_container_width=True)

# ---------------- TAB 3: Shipping Mode ----------------
with tab3:
    c1, c2 = st.columns(2)

    with c1:
        mode_delay = (
            fdf.groupby("Shipping Mode")["Delivery Delay Gap"]
            .mean()
            .sort_values()
            .reset_index()
        )
        fig7 = px.bar(
            mode_delay, x="Shipping Mode", y="Delivery Delay Gap",
            title="Average Delay Gap by Shipping Mode (days)",
            color="Delivery Delay Gap", color_continuous_scale="RdYlGn_r",
            text_auto=".2f",
        )
        st.plotly_chart(fig7, use_container_width=True)

    with c2:
        sla = (
            fdf.groupby("Shipping Mode")["Late_delivery_risk"]
            .apply(lambda x: (x == 0).mean() * 100)
            .sort_values(ascending=False)
            .reset_index()
        )
        sla.columns = ["Shipping Mode", "SLA Compliance (%)"]
        fig8 = px.bar(
            sla, x="Shipping Mode", y="SLA Compliance (%)",
            title="SLA Compliance (%) by Shipping Mode",
            color="SLA Compliance (%)", color_continuous_scale="Greens",
            text_auto=".1f",
        )
        st.plotly_chart(fig8, use_container_width=True)

    st.subheader("Shipping Mode × Delivery Status Cross-tab")
    cross = pd.crosstab(fdf["Shipping Mode"], fdf["Delivery Status"])
    st.dataframe(cross, use_container_width=True)

# ---------------- TAB 4: Regional & Segment ----------------
with tab4:
    c1, c2 = st.columns(2)

    with c1:
        market_delay = (
            fdf.groupby("Market")["Delivery Delay Gap"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )
        fig9 = px.bar(
            market_delay, x="Market", y="Delivery Delay Gap",
            title="Average Delay by Market (Logistics Efficiency)",
            color="Delivery Delay Gap", color_continuous_scale="RdYlGn_r",
            text_auto=".2f",
        )
        st.plotly_chart(fig9, use_container_width=True)

    with c2:
        seg_delay = (
            fdf.groupby("Customer Segment")["Delivery Delay Gap"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )
        fig10 = px.bar(
            seg_delay, x="Customer Segment", y="Delivery Delay Gap",
            title="Average Delay by Customer Segment",
            color="Delivery Delay Gap", color_continuous_scale="RdYlGn_r",
            text_auto=".2f",
        )
        st.plotly_chart(fig10, use_container_width=True)

    st.subheader("SLA Risk Exposure — Premium/Corporate Segments")
    seg_risk = (
        fdf.groupby("Customer Segment")["Late_delivery_risk"]
        .mean()
        .mul(100)
        .sort_values(ascending=False)
        .reset_index()
    )
    seg_risk.columns = ["Customer Segment", "Late Delivery Risk (%)"]
    fig11 = px.bar(
        seg_risk, x="Customer Segment", y="Late Delivery Risk (%)",
        color="Late Delivery Risk (%)", color_continuous_scale="Reds",
        text_auto=".1f",
    )
    st.plotly_chart(fig11, use_container_width=True)

    st.subheader("Top 10 High-Risk Order Countries")
    country_risk = (
        fdf.groupby("Order Country")["Late_delivery_risk"]
        .agg(["mean", "count"])
        .query("count >= 30")
        .sort_values("mean", ascending=False)
        .head(10)
        .reset_index()
    )
    country_risk["mean"] = (country_risk["mean"] * 100).round(1)
    country_risk.columns = ["Order Country", "Late Delivery Risk (%)", "Order Count"]
    st.dataframe(country_risk, use_container_width=True)

st.markdown("---")
st.caption("Built for APL Logistics (KWE Group) | Data Analyst Project — Unified Mentor")
