import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Manufacturing Analytics",
    layout="wide"
)

# Sidebar Color Customization
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #C8E6C9;
}

[data-testid="stSidebar"] * {
    color: #1B4332;
}

[data-testid="stSidebar"] button {
    background-color: #A5D6A7;
    color: #1B4332;
    border-radius: 8px;
    border: 1px solid #81C784;
}

[data-testid="stSidebar"] button:hover {
    background-color: #81C784;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Dashboard
st.title("Manufacturing Sensor Analytics")
st.subheader("Predictive Maintenance Dashboard")

st.success("Application is running successfully!")

st.write("Welcome to Manufacturing Sensor Analytics Project")

data = pd.DataFrame({
    "Machine": ["M1", "M2", "M3", "M4", "M5"],
    "Temperature": [65, 72, 80, 90, 75],
    "Vibration": [20, 30, 45, 60, 35]
})

st.write("Machine Sensor Data")
st.dataframe(data)

st.bar_chart(data.set_index("Machine"))

st.write("Project Status: Running")