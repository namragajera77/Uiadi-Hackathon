import os
import pandas as pd
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="UIDAI Analytics Dashboard",
    page_icon="🪪",
    layout="wide",
)

# ---------------- CUSTOM UI STYLE ----------------
st.markdown("""
<style>
.main {
    background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}
.kpi {
    background: white;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    text-align: center;
}
.kpi h2 {margin:0; font-size:28px;}
.kpi p {margin:0; color:#64748b;}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #020617);
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FIXED FILE NAMES ----------------
ENROLMENT_FILES = [
    "enrollment_all (1).csv",
    "enrollment_all (1)_2.csv",
    "enrollment_all (1)_3.csv",
]

DEMOGRAPHIC_FILES = [
    "demo_all (1).csv",
    "demo_all (1)_2.csv",
]

BIOMETRIC_FILES = [
    "mightymerge.io__xzzeu4zp.csv",
    "mightymerge.io__xzzeu4zp (1)_2.csv",
]

# ---------------- DATA LOADER ----------------
@st.cache_data(show_spinner=False)
def load_files(files):
    dfs = []
    for f in files:
        if os.path.exists(f):
            dfs.append(pd.read_csv(f))
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

# ---------------- NORMALIZATION ----------------
def normalize(df):
    if df.empty:
        return df
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
        df["month"] = df["date"].dt.to_period("M").astype(str)
    for c in ["state", "district"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    if "pincode" in df.columns:
        df["pincode"] = df["pincode"].astype(str).str.replace(".0","",regex=False)
    return df

# ---------------- SAFE TOTAL ----------------
def add_total(df, cols, name):
    df = df.copy()
    for c in cols:
        if c not in df.columns:
            df[c] = 0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df[name] = df[cols].sum(axis=1).astype(int)
    return df

# ---------------- HEADER ----------------
st.title("🪪 UIDAI Aadhaar Analytics Dashboard")
st.caption("Enrolment • Demographic • Biometric | Stable & Hackathon-Ready")

# ---------------- SIDEBAR ----------------
dataset = st.sidebar.radio(
    "Select Dataset",
    ["Enrolment", "Demographic", "Biometric", "Combined"],
)

# ---------------- LOAD DATA ----------------
if dataset == "Enrolment":
    df = add_total(
        normalize(load_files(ENROLMENT_FILES)),
        ["age_0_5", "age_5_17", "age_18_greater"],
        "total"
    )

elif dataset == "Demographic":
    df = add_total(
        normalize(load_files(DEMOGRAPHIC_FILES)),
        ["demo_age_5_17", "demo_age_17_"],
        "total"
    )

elif dataset == "Biometric":
    df = add_total(
        normalize(load_files(BIOMETRIC_FILES)),
        ["bio_age_5_17", "bio_age_17_"],
        "total"
    )

else:
    enr = add_total(normalize(load_files(ENROLMENT_FILES)),
                    ["age_0_5","age_5_17","age_18_greater"], "enrol")
    dem = add_total(normalize(load_files(DEMOGRAPHIC_FILES)),
                    ["demo_age_5_17","demo_age_17_"], "demo")
    bio = add_total(normalize(load_files(BIOMETRIC_FILES)),
                    ["bio_age_5_17","bio_age_17_"], "bio")

    key = ["date","state","district","pincode","month"]
    df = (
        enr.groupby(key, as_index=False)["enrol"].sum()
        .merge(dem.groupby(key, as_index=False)["demo"].sum(), on=key, how="outer")
        .merge(bio.groupby(key, as_index=False)["bio"].sum(), on=key, how="outer")
        .fillna(0)
    )
    df["total"] = df[["enrol","demo","bio"]].sum(axis=1).astype(int)

if df.empty:
    st.error("No data loaded. Check CSV files.")
    st.stop()

# ---------------- FILTER ----------------
min_d, max_d = df["date"].min(), df["date"].max()
start, end = st.sidebar.date_input("Date Range",
                                  (min_d.date(), max_d.date()))
df = df[(df["date"].dt.date >= start) & (df["date"].dt.date <= end)]

# ---------------- KPI CARDS ----------------
c1, c2, c3 = st.columns(3)
c1.markdown(f"<div class='kpi'><p>Records</p><h2>{len(df):,}</h2></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='kpi'><p>Total Count</p><h2>{df['total'].sum():,}</h2></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='kpi'><p>States</p><h2>{df['state'].nunique()}</h2></div>", unsafe_allow_html=True)

# ---------------- TABS ----------------
tab1, tab2 = st.tabs(["📈 Trend", "🧾 Data"])

with tab1:
    st.line_chart(df.groupby("date")["total"].sum())

with tab2:
    st.dataframe(df.head(5000), width="stretch")
    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "uidai_filtered.csv",
        "text/csv",
    )
