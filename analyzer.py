import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from src.config import DATA_DIR, OUTPUT_DIR


# ==========================================
# 1. DATA LOADING & MERGING
# ==========================================
def load_and_combine_chunks(file_pattern):
    search_path = os.path.join(DATA_DIR, file_pattern)
    files = glob.glob(search_path)
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
        except:
            pass
    if not dfs: return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


def clean_domain_df(df, prefix):
    if df.empty: return df
    df.columns = df.columns.str.lower().str.strip()

    # Rename columns to standard format
    rename_map = {}
    if prefix == 'enrol':
        rename_map = {'age_0_5': 'enrol_infant', 'age_5_17': 'enrol_child', 'age_18_greater': 'enrol_adult'}
    elif prefix == 'bio':
        rename_map = {'bio_age_5_17': 'bio_child', 'bio_age_17_': 'bio_adult'}
    elif prefix == 'demo':
        rename_map = {'demo_age_5_17': 'demo_child', 'demo_age_17_': 'demo_adult'}

    df = df.rename(columns=rename_map)

    # Fix States
    df['state'] = df['state'].str.title().str.strip()

    # --- NEW: GARBAGE FILTER ---
    # Remove rows where state is '100000' or contains numbers
    df = df[~df['state'].str.contains(r'\d', regex=True)]
    # ---------------------------

    state_map = {'Westbengal': 'West Bengal', 'Orissa': 'Odisha', 'Uttaranchal': 'Uttarakhand', 'Delhi': 'NCT Of Delhi'}
    df['state'] = df['state'].replace(state_map)

    # Date & Aggregation
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    df['month'] = df['date'].dt.to_period('M')

    # Aggregate to District-Month
    group_cols = ['state', 'district', 'month']
    numeric_cols = [c for c in df.columns if c not in group_cols and c not in ['date', 'pincode']]
    return df.groupby(group_cols)[numeric_cols].sum().reset_index()


def load_and_clean_data():
    """Builds the Master Dataset from all 3 domains."""
    print("Building Master Dataset...")

    # 1. Load Chunks
    raw_enrol = load_and_combine_chunks("api_data_aadhar_enrolment_*.csv")
    raw_bio = load_and_combine_chunks("api_data_aadhar_biometric_*.csv")
    raw_demo = load_and_combine_chunks("api_data_aadhar_demographic_*.csv")

    # 2. Clean Domains
    df_enrol = clean_domain_df(raw_enrol, 'enrol')
    df_bio = clean_domain_df(raw_bio, 'bio')
    df_demo = clean_domain_df(raw_demo, 'demo')

    # 3. Merge (Outer Join)
    master = df_enrol
    if master.empty and not df_bio.empty:
        master = df_bio
    elif not master.empty and not df_bio.empty:
        master = pd.merge(master, df_bio, on=['state', 'district', 'month'], how='outer')

    if master.empty and not df_demo.empty:
        master = df_demo
    elif not master.empty and not df_demo.empty:
        master = pd.merge(master, df_demo, on=['state', 'district', 'month'], how='outer')

    master = master.fillna(0)

    # 4. Feature Engineering
    cols = ['enrol_child', 'enrol_adult', 'bio_child', 'bio_adult', 'demo_child', 'demo_adult']
    master['total_activity'] = master[[c for c in cols if c in master.columns]].sum(axis=1)

    # MBU Compliance
    if 'bio_child' in master.columns and 'enrol_child' in master.columns:
        master['mbu_compliance'] = master['bio_child'] / (master['enrol_child'] + 1)
    else:
        master['mbu_compliance'] = 0

    return master


# ==========================================
# 2. ANALYSIS FUNCTIONS
# ==========================================
def generate_health_index(df):
    """Calculates Risk Index using ML."""
    print("Generating Identity Health Index...")

    # Aggregating for ML
    stats = df.groupby(['state', 'district']).agg({
        'total_activity': ['sum', 'mean', 'std'],
        'mbu_compliance': 'mean'
    }).reset_index()

    # Fix Multi-level columns
    stats.columns = ['state', 'district', 'total_vol', 'daily_avg', 'daily_std', 'avg_mbu_compliance']

    # Stability Score
    stats['volatility_cv'] = stats['daily_std'] / (stats['daily_avg'] + 1)
    stats['stability_score'] = 1 / (stats['volatility_cv'] + 0.1)

    # ML Clustering
    features = stats[['total_vol', 'stability_score', 'avg_mbu_compliance']].fillna(0)
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    stats['cluster'] = kmeans.fit_predict(features_scaled)

    # Rank Clusters
    cluster_rank = stats.groupby('cluster')['total_vol'].mean().sort_values().index
    rank_map = {old: new for new, old in enumerate(cluster_rank)}
    stats['health_grade'] = stats['cluster'].map(rank_map)

    # Labels
    label_map = {0: 'Critical Risk (High Gap)', 1: 'Moderate Risk', 2: 'Healthy Ecosystem'}
    stats['risk_category'] = stats['health_grade'].map(label_map)

    # 0-100 Score Calculation
    norm_vol = scaler.fit_transform(stats[['total_vol']]).flatten()
    stats['health_index'] = (0.4 * norm_vol + 0.4 * stats['stability_score'] + 0.2 * stats['avg_mbu_compliance']) * 100

    # Plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=stats, x='total_vol', y='avg_mbu_compliance', hue='risk_category', palette='RdYlGn')
    plt.xscale('log')
    plt.title('Identity Health: Volume vs MBU Compliance')
    plt.savefig(os.path.join(OUTPUT_DIR, '4_health_clusters.png'))
    plt.close()

    return stats.sort_values('health_index')


def analyze_mbu_gap(df):
    """Visualizes where Children are Failing to Update."""
    print("Analyzing MBU Gaps...")
    if 'enrol_child' not in df.columns or 'bio_child' not in df.columns:
        print("Skipping MBU Gap - Columns missing.")
        return

    df_district = df.groupby('district')[['enrol_child', 'bio_child']].sum().reset_index()
    df_district['gap'] = df_district['enrol_child'] - df_district['bio_child']

    top_risk = df_district.sort_values('gap', ascending=False).head(10)

    plt.figure(figsize=(10, 5))
    # --- FIXED: Added hue and legend=False to silence warning ---
    sns.barplot(data=top_risk, x='gap', y='district', hue='district', palette='Reds_r', legend=False)
    # ------------------------------------------------------------
    plt.title('Top 10 Districts with "Silent Child IDs" (Enrolled but not Updated)')
    plt.xlabel('Count of Children Missing Updates')
    plt.savefig(os.path.join(OUTPUT_DIR, '5_child_risk_gap.png'))
    plt.close()



# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# import glob
# import os
# from src.config import DATA_DIR, OUTPUT_DIR
#
#
# def load_and_clean_data():
#     """Loads all CSVs, cleans data, and standardizes columns."""
#     search_path = os.path.join(DATA_DIR, "*.csv")
#     files = glob.glob(search_path)
#
#     if not files:
#         raise ValueError(f"No CSV files found in {DATA_DIR}. Did you move them?")
#
#     print(f"Loading {len(files)} files...")
#     dfs = []
#     for f in files:
#         try:
#             df = pd.read_csv(f)
#             dfs.append(df)
#         except Exception as e:
#             print(f"Skipping {f}: {e}")
#
#     raw_df = pd.concat(dfs, ignore_index=True)
#
#     # 1. Deduplication
#     clean_df = raw_df.drop_duplicates().copy()
#
#     # 2. Date & Metrics
#     clean_df['date'] = pd.to_datetime(clean_df['date'], format='%d-%m-%Y')
#     clean_df['total_transactions'] = clean_df['demo_age_5_17'] + clean_df['demo_age_17_']
#
#     # 3. State Name Standardization
#     clean_df['state'] = clean_df['state'].str.title().str.strip()
#     state_map = {
#         'Westbengal': 'West Bengal', 'West  Bengal': 'West Bengal',
#         'Orissa': 'Odisha', 'Pondicherry': 'Puducherry',
#         'Uttaranchal': 'Uttarakhand', 'Delhi': 'NCT Of Delhi'
#     }
#     clean_df['state'] = clean_df['state'].replace(state_map)
#
#     # 4. Temporal Features
#     clean_df['day_of_week'] = clean_df['date'].dt.day_name()
#     clean_df['is_weekend'] = clean_df['day_of_week'].isin(['Saturday', 'Sunday'])
#
#     return clean_df
#
#
# def analyze_pareto(df):
#     """Differentiator 1: The Inequality (Lorenz) Analysis"""
#     print("Running Pareto Analysis...")
#     pincode_load = df.groupby('pincode')['total_transactions'].sum().sort_values(ascending=False).reset_index()
#
#     # Calculate Cumulative %
#     pincode_load['cumulative_vol'] = pincode_load['total_transactions'].cumsum()
#     pincode_load['cumulative_perc'] = pincode_load['cumulative_vol'] / pincode_load['total_transactions'].sum()
#     pincode_load['pincode_rank_perc'] = (pincode_load.index + 1) / len(pincode_load)
#
#     # Plot Lorenz Curve
#     plt.figure(figsize=(10, 6))
#     plt.plot(pincode_load['pincode_rank_perc'], pincode_load['cumulative_perc'], color='crimson', linewidth=2)
#     plt.plot([0, 1], [0, 1], color='navy', linestyle='--')
#     plt.title('Operational Inequality (Lorenz Curve)')
#     plt.xlabel('% of Centers (Pincodes)')
#     plt.ylabel('% of Workload')
#     plt.grid(True, alpha=0.3)
#     plt.savefig(os.path.join(OUTPUT_DIR, '1_inequality_curve.png'))
#     plt.close()
#
#     return pincode_load
#
#
# def analyze_reliability(df):
#     """Differentiator 2: The Reliability Matrix (Stability Analysis)"""
#     print("Running Reliability Matrix...")
#     stats = df.groupby(['state', 'district'])['total_transactions'].agg(['mean', 'std', 'count']).reset_index()
#     stats['cv'] = stats['std'] / stats['mean']  # Coefficient of Variation
#
#     # Classify
#     med_cv = stats['cv'].median()
#     med_vol = stats['mean'].median()
#
#     def classify(row):
#         if row['mean'] > med_vol and row['cv'] < med_cv:
#             return 'High Vol / Stable (Backbone)'
#         elif row['mean'] > med_vol and row['cv'] >= med_cv:
#             return 'High Vol / Erratic (Crisis)'
#         elif row['mean'] <= med_vol and row['cv'] < med_cv:
#             return 'Low Vol / Stable'
#         else:
#             return 'Low Vol / Erratic'
#
#     stats['category'] = stats.apply(classify, axis=1)
#
#     # Plot
#     plt.figure(figsize=(10, 8))
#     sns.scatterplot(data=stats, x='mean', y='cv', hue='category', palette='viridis', alpha=0.7)
#     plt.xscale('log')
#     plt.title('Reliability Matrix: Volume vs Stability')
#     plt.savefig(os.path.join(OUTPUT_DIR, '2_reliability_matrix.png'))
#     plt.close()
#
#     return stats
#
#
# def analyze_anomalies(df):
#     """Differentiator 3: Automated Anomaly Detection"""
#     print("Scanning for Anomalies...")
#     # Analyze the top district only for the demo
#     top_dist = df.groupby('district')['total_transactions'].sum().idxmax()
#     dist_data = df[df['district'] == top_dist].copy().sort_values('date')
#     daily = dist_data.groupby('date')['total_transactions'].sum().reset_index()
#
#     # Rolling Statistics
#     daily['rolling_mean'] = daily['total_transactions'].rolling(7).mean()
#     daily['rolling_std'] = daily['total_transactions'].rolling(7).std()
#
#     # Anomaly Rule: > 3 Standard Deviations
#     daily['is_anomaly'] = daily['total_transactions'] > (daily['rolling_mean'] + 3 * daily['rolling_std'])
#
#     # Plot
#     plt.figure(figsize=(12, 6))
#     plt.plot(daily['date'], daily['total_transactions'], label='Daily Load')
#     anomalies = daily[daily['is_anomaly']]
#     plt.scatter(anomalies['date'], anomalies['total_transactions'], color='red', s=100, label='Anomaly Detected',
#                 zorder=5)
#     plt.title(f'Automated Audit Sentinel: {top_dist}')
#     plt.legend()
#     plt.savefig(os.path.join(OUTPUT_DIR, '3_anomaly_audit.png'))
#     plt.close()
#
#
# def analyze_weekend_effect(df):
#     """Differentiator 4: Weekend Efficiency Multiplier"""
#     print("Calculating Weekend Multiplier...")
#     avg_load = df.groupby('is_weekend')['total_transactions'].mean()
#     multiplier = avg_load[True] / avg_load[False] if True in avg_load and False in avg_load else 0
#
#     return multiplier