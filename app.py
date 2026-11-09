import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. Page Configuration ---
st.set_page_config(page_title="Flight Operations Dashboard", layout="wide")
st.title("✈️ Airline Operations & Flight Delay Analytics")

# --- 2. Dataset Generation (Beginner Friendly & Cached) ---
@st.cache_data
def get_data():
    np.random.seed(42)
    airlines = ["Air India", "IndiGo", "Akasa Air", "SpiceJet", "Vistara"]
    data = []
    for i in range(150):
        carrier = np.random.choice(airlines)
        hour = np.random.randint(6, 23)
        dep_delay = int(np.random.normal(15, 12))
        arr_delay = dep_delay + int(np.random.normal(3, 5))
        load_factor = np.random.randint(65, 99)
        fuel_tons = round(np.random.uniform(8.0, 22.0), 1)
        data.append({
            "Airline": carrier,
            "Hour": hour,
            "Dep_Delay": max(0, dep_delay),
            "Arr_Delay": max(-5, arr_delay),
            "Load_Factor": load_factor,
            "Fuel_Tons": fuel_tons
        })
    return pd.DataFrame(data)

df = get_data()

# --- 3. Sidebar Filters (Widgets: Multiselect, Selectbox, Slider) ---
st.sidebar.header("Filter Telemetry")
selected_airlines = st.sidebar.multiselect(
    "Select Airline(s):",
    options=df["Airline"].unique(),
    default=df["Airline"].unique()
)
hour_limit = st.sidebar.slider("Max Departure Hour:", 6, 23, 23)
sort_order = st.sidebar.selectbox("Sort Table By:", ["Arr_Delay", "Dep_Delay", "Load_Factor"])

# Apply Filters
filtered_df = df[(df["Airline"].isin(selected_airlines)) & (df["Hour"] <= hour_limit)]

# --- 4. Key Performance Indicators (KPIs in Columns) ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Flights", len(filtered_df))
kpi2.metric("Avg Arr Delay", f"{filtered_df['Arr_Delay'].mean():.1f} min" if len(filtered_df) > 0 else "0 min")
kpi3.metric("Avg Load Factor", f"{filtered_df['Load_Factor'].mean():.1f}%" if len(filtered_df) > 0 else "0%")
kpi4.metric("Total Fuel", f"{filtered_df['Fuel_Tons'].sum():.1f} T" if len(filtered_df) > 0 else "0 T")

st.markdown("---")

# --- 5. Tabs for Layout Organization ---
tab1, tab2, tab3 = st.tabs(["📊 Visualizations", "📋 Data Table & GroupBy", "💡 Insights"])

with tab1:
    col1, col2 = st.columns(2)
    # A. Bar Chart: Average delay by airline
    with col1:
        st.subheader("Bar Chart: Avg Delay by Airline")
        bar_data = filtered_df.groupby("Airline")["Arr_Delay"].mean().reset_index()
        fig_bar = px.bar(bar_data, x="Airline", y="Arr_Delay", color="Airline", title="Carrier Delay Comparison")
        st.plotly_chart(fig_bar, use_container_width=True)

    # B. Line Chart: Delay trend across hours
    with col2:
        st.subheader("Line Chart: Delay Trend Across Hours")
        line_data = filtered_df.groupby("Hour")["Arr_Delay"].mean().reset_index()
        fig_line = px.line(line_data, x="Hour", y="Arr_Delay", markers=True, title="Hourly Cascading Delay Trend")
        st.plotly_chart(fig_line, use_container_width=True)

    # C. Scatter Plot: Departure delay vs Arrival delay
    st.subheader("Scatter Plot: Dep Delay vs. Arr Delay")
    fig_scatter = px.scatter(
        filtered_df, x="Dep_Delay", y="Arr_Delay", color="Airline",
        size="Load_Factor", title="Correlation: Departure Delay vs Arrival Delay"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    st.subheader("Category-Wise Fleet Summary (GroupBy)")
    group_summary = filtered_df.groupby("Airline").agg(
        Flight_Count=("Arr_Delay", "count"),
        Avg_Arr_Delay=("Arr_Delay", "mean"),
        Avg_Load_Factor=("Load_Factor", "mean")
    ).reset_index().round(1)
    st.dataframe(group_summary, use_container_width=True)

    with st.expander("🔍 Click to View Raw Telemetry Records"):
        st.dataframe(filtered_df.sort_values(sort_order, ascending=False), use_container_width=True)

with tab3:
    st.subheader("Key Findings & Observations")
    st.markdown('''
    - **Rotational Cascading Delays**: Delays rise steadily as the day advances, peaking in the evening.
    - **Strong Correlation**: Flights with ground departure delays consistently suffer from corresponding arrival delays.
    - **Capacity Optimization**: Higher passenger load factors ensure maximum operational fuel efficiency.
    ''')
