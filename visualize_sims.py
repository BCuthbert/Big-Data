import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="Simulation Visualizer",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔍 Simulation Results Dashboard")
st.markdown(
    "Use the controls in the sidebar to explore how different policies perform across metrics."
)

# Sidebar controls
data_file = st.sidebar.file_uploader("Upload simulation_summary.csv", type="csv")

if data_file:
    df = pd.read_csv(data_file)

    # Sidebar: metric and axis
    metric = st.sidebar.selectbox(
        "Select metric to plot",
        options=["run_time_mean", "quality_mean", "avg_uncertainty_mean"]
    )
    x_axis = st.sidebar.selectbox(
        "Select X-axis",
        options=["bandwidth", "arrival_rate"]
    )
    policies = st.sidebar.multiselect(
        "Select policies",
        options=df['policy'].unique(),
        default=list(df['policy'].unique())
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("Data preview:")
    st.sidebar.dataframe(df.head(), height=200)

    # Filter data
    filtered = df[df['policy'].isin(policies)]

    # Plot
    fig, ax = plt.subplots()
    for p in policies:
        subset = filtered[filtered['policy'] == p]
        ax.plot(subset[x_axis], subset[metric], marker='o', label=p)

    ax.set_xlabel(x_axis.replace('_', ' ').title())
    ax.set_ylabel(metric.replace('_', ' ').title())
    ax.set_title(f"{metric.replace('_', ' ').title()} vs {x_axis.replace('_', ' ').title()}")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # Show raw table
    with st.expander("Show full data table"):
        st.dataframe(filtered)
else:
    st.info("Please upload the simulation_summary.csv file in the sidebar to get started.")

