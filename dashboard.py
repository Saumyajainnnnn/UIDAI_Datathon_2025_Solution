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
        st.image(img, width=700)
    else:
        st.error("Chart 4 not found. Please run main.py first.")

    st.info("💡 Insight: High Aadhaar volume does not guarantee system health—compliance and stability matter more.")

    with st.expander("📘 How to interpret this chart"):
        st.markdown("""
        **What this chart shows**  
        Each dot represents a district, clustered using Machine Learning based on Aadhaar volume, operational stability, and compliance quality.

        **How to read the axes**  
        • **X-axis (Total Volume – Log Scale):** Left = low-activity districts, Right = high-activity districts  
        • **Y-axis (Health Index 0–100):** Bottom = unstable or non-compliant systems, Top = stable and reliable systems  

        **What the colors mean**  
        • 🔴 **Critical Risk:** High operational stress or poor compliance  
        • 🟡 **Moderate:** Functional but inconsistent performance  
        • 🟢 **Healthy:** High throughput with strong stability and compliance  

        **Why this matters**  
        • High activity does not automatically imply a healthy identity system  
        • Some large districts process massive volumes but fail to maintain biometric freshness  

        **Key insight**  
        • Most large districts perform better due to stronger infrastructure  
        • The most important signals are large districts below the trend — they have scale but are failing  
        • These are the highest-value targets for audits, compliance checks, and fraud monitoring
        """)


elif page == "Operational Analysis":
    st.title("⚙️ Operational Efficiency & Inequality")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Intra-District Inequality (Pincode Variance)")
        st.write(
            "**Chart 8:** Distribution of total Aadhaar workload across pincodes within a district, "
            "highlighting operational imbalance."
        )
        img = load_chart("8_Pincode_Variance.png")
        if img: st.image(img)

        st.info("💡 Insight: Districts may appear functional overall, yet hide severe service overload at specific pincodes.")
        with st.expander("📘 How to interpret this chart"):
            st.markdown("""
            **What this shows**  
            This chart visualizes how Aadhaar enrolment and update transactions are distributed across 
            pincodes within a single district.

            **Key observations**  
            • A small number of pincodes handle a disproportionately high workload.  
            • The high Coefficient of Variation (CV = 0.96) indicates severe intra-district imbalance.

            **Why this happens**  
            • Urban and high-density pincodes attract more transactions due to accessibility and awareness.  
            • Peripheral areas face lower demand or limited service access.

            **Why this matters**  
            • Uneven workload creates service pressure in high-demand areas.  
            • Underutilized capacity persists elsewhere.

            **Recommended action**  
            • Reallocate staff and kits at the pincode level.  
            • Deploy mobile enrolment units in high-load zones.  
            • Monitor variance metrics to detect early stress.
            """)

    with col2:
        st.subheader("Enrolment Temporal Consistency")
        st.write("**Chart 1:** Monthly enrolment trends showing operational stability vs. camps.")
        img = load_chart("EDA_1_Enrolment_Trend.png")
        if img: st.image(img)
        
        st.info("💡 Insight: Aadhaar enrolment demand is not uniform—child enrolments are seasonal, adults are structural.")
        with st.expander("📘 How to interpret this chart"):
            st.markdown("""
            **What this shows**  
            This chart compares monthly enrolment volumes for children and adults from March to December 2025.

            **Key observations**  
            • Child enrolments show strong seasonality with sharp peaks around August–September.  
            • Adult enrolments remain consistently low with only minor month-to-month variation.

            **Why this happens**  
            • Child enrolments are driven by academic admission cycles and school calendars.  
            • Adult enrolments are need-based and less dependent on fixed timelines.

            **Why this matters**  
            • Seasonal dependence makes child enrolment vulnerable to short-term disruptions.  
            • Adult enrolments provide a stable baseline demand across the year.

            **Recommended action**  
            • Increase enrolment capacity during school admission periods.  
            • Maintain steady infrastructure for adult enrolments year-round.
            """)


elif page == "Risk & Security":
    st.title("🛡️ Fraud & Compliance Sentinel")

    st.subheader("Automated Fraud Detection (Security Sentinel)")
    st.write(
        "**Chart 7:** A Z-score–based algorithm that automatically flags abnormal "
        "daily Aadhaar transaction spikes (> 3σ)."
    )
    img = load_chart("7_Anomaly_Sentinel.png")
    if img: st.image(img, width=700)

    st.info(
    "💡 Insight: The Security Sentinel identifies statistically extreme anomalies "
    "within observed transaction data, enabling proactive investigation and response.")

    with st.expander("📘 How to interpret this chart"):
        st.markdown("""
        **What this shows**  
        This chart tracks daily Aadhaar transaction volumes and highlights days that deviate sharply from normal behavior using a Z-score–based method.

        **Key observations**  
        • A single, extreme spike on **01 March** is flagged as a **>3σ anomaly**  
        • All other observed days fall within expected statistical bounds  

        **Why this spike is high-risk**  
        • It is isolated relative to surrounding days  
        • It exceeds normal operational variation by a large margin  
        • It is statistically unlikely under normal conditions  

        **Why most days are not flagged**  
        • Routine fluctuations stay within ±1σ to ±2σ  
        • The algorithm adapts to historical variance and avoids false alarms  

        **Why this matters**  
        • Enables rapid audits and investigations  
        • Supports log correlation across devices, locations, and systems  
        • Helps contain damage before wider systemic impact  

        **Why Z-score**  
        • Statistically grounded and explainable  
        • Unsupervised (no labeled fraud data required)  
        • Scalable for large, real-time transaction streams
        """)

    with st.expander("ℹ️ Data Coverage Note"):
        st.markdown("""
       **Data availability note**  
        • Transaction-level data is unavailable between **March and August**  
        • The flat segment reflects **missing records**, not operational inactivity 

        **How to interpret the anomaly**  
        • The detection algorithm operates only on observed data points  
        • The flagged spike represents a statistically extreme deviation **within available data**

        This limitation has been explicitly acknowledged to ensure accurate and responsible interpretation.
        """)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Biometric Splits")

        st.write(
            "**Chart 2:** Distribution of biometric updates between children (5–17) "
            "and adults (18+) across the dataset."
        )

        img = load_chart("EDA_2_Bio_Split.png")
        if img: st.image(img)

        st.info("💡 Insight: Equal biometric updates for children and adults are a warning sign—children should dominate update volume.")

        with st.expander("📘 How to interpret this chart"):
            st.markdown("""
            **What this shows**  
            This chart compares the share of biometric updates performed for children versus adults.

            **Why this matters**  
            • Children’s biometrics change rapidly and require periodic updates  
            • Adults require far fewer updates over time  

            **Key insight**  
            • A near-50 split is not healthy parity  
            • It signals systemic under-updating of child biometrics  

            **What this indicates**  
            • Silent accumulation of outdated child records  
            • Increased risk of future authentication failures  
            • Gaps in awareness, access, or operational prioritization

            This serves as a diagnostic check before deeper district-level risk analysis,
            motivating the identification of Child Identity Risk Zones.
            """)

    with col2:
        st.subheader("Child Identity Risk Zones")

        st.write(
            "**Chart 5:** Districts where children are enrolled in Aadhaar "
            "but fail to complete mandatory biometric updates."
        )

        img = load_chart("5_child_risk_gap.png")
        if img: st.image(img)

        st.info("💡 Insight: Aadhaar enrolment without biometric updates creates silent identity failure among children.")

        with st.expander("📘 How to interpret this chart"):
            st.markdown("""
            **What this shows**  
            This chart highlights districts with large gaps between child enrolments and biometric updates, indicating incomplete or outdated identities.

            **Why this is critical**  
            • Children’s biometrics change as they grow  
            • Without updates, Aadhaar authentication reliability degrades  
            • These identities exist but fail at the point of use  

            **Why certain districts are high-risk**  
            • Strong enrolment drives but weak follow-through  
            • High migration and urban churn  
            • Geographic barriers and limited access to update centers  

            **Why this matters**  
            • Service denial in PDS, DBT, and scholarships  
            • Increased risk of identity misuse or proxy authentication  
            • Overestimation of true identity coverage  

            **Recommended action**  
            • Age-triggered biometric update reminders  
            • Mobile update units in high-gap districts  
            • Shift district KPIs from enrolment counts to update completion
            """)



elif page == "Predictive AI":
    st.title("🤖 Future Workload Forecasting")

    st.subheader("AI Resource Planning")
    st.write("We used Holt-Winters Exponential Smoothing to predict load for the next 90 days.")
    st.info("💡 Insight: A 15% surge is predicted in the next quarter due to seasonal trends.")

    img = load_chart("9_Workload_Forecast.png")
    if img: st.image(img, use_container_width=True)
