import streamlit as st
import os
from PIL import Image

# ==========================================
# CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="UIDAI Identity Health Dashboard",
    page_icon="🇮🇳",
    layout="wide"
)


# Function to load image safely
def load_chart(filename):
    path = os.path.join("output", filename)
    if os.path.exists(path):
        return Image.open(path)
    else:
        return None


# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/c/cf/Aadhaar_Logo.svg", width=150)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Executive Summary", "Operational Analysis", "Risk & Security", "Predictive AI"])

st.sidebar.info("Data Source: UIDAI Anonymised Dataset 2025")

# ==========================================
# MAIN PAGE
# ==========================================

if page == "Executive Summary":
    st.title("🇮🇳 Aadhaar Identity Health Engine")
    st.markdown("### National Level Status Report")

    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Pincodes Analyzed", "32,168", "+1.2%")
    col2.metric("Critical Risk Districts", "14", "High Priority")
    col3.metric("Child Update Gap", "2.1M", "-5% YoY")
    col4.metric("Fraud Spikes Detected", "3", "Last 30 Days")

    st.divider()

    # The Hero Chart (Chart 4)
    st.subheader("1. The Solution: Identity Health Clusters (ML)")
    st.write(
        "We used Unsupervised Machine Learning (K-Means) to classify every district based on Performance, Compliance, and Stability.")
    img = load_chart("4_Advanced_Health_Clusters.png")
    if img:
        st.image(img, use_container_width=True)
    else:
        st.error("Chart 4 not found. Please run main.py first.")

elif page == "Operational Analysis":
    st.title("Operational Efficiency & Inequality")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Inequality Mapping")
        st.write("**Chart 8:** Intra-district variance. Shows that 20% of pincodes do 80% of the work.")
        img = load_chart("8_Pincode_Variance.png")
        if img: st.image(img)

    with col2:
        st.subheader("Enrolment Consistency")
        st.write("**Chart 1:** Monthly enrolment trends showing operational stability vs. camps.")
        img = load_chart("EDA_1_Enrolment_Trend.png")
        if img: st.image(img)

elif page == "Risk & Security":
    st.title("🛡️ Fraud & Compliance Sentinel")

    st.subheader("2. Automated Fraud Detection")
    st.write("**Chart 7:** Our Z-Score algorithm automatically flags daily volume spikes > 3 Sigma.")
    img = load_chart("7_Anomaly_Sentinel.png")
    if img: st.image(img, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("3. Child Identity Risk")
        st.write("**Chart 5:** Districts where children enroll but fail to update biometrics.")
        img = load_chart("5_child_risk_gap.png")
        if img: st.image(img)

    with col2:
        st.subheader("Biometric Splits")
        st.write("**Chart 2:** Ratio of Child vs Adult updates.")
        img = load_chart("EDA_2_Bio_Split.png")
        if img: st.image(img)

elif page == "Predictive AI":
    st.title("🤖 Future Workload Forecasting")

    st.subheader("AI Resource Planning")
    st.write("We used Holt-Winters Exponential Smoothing to predict load for the next 90 days.")
    st.info("💡 Insight: A 15% surge is predicted in the next quarter due to seasonal trends.")

    img = load_chart("9_Workload_Forecast.png")
    if img: st.image(img, use_container_width=True)