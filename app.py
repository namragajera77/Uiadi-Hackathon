import os
import glob
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

# Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False


# ------------------------------ Page Config ------------------------------
st.set_page_config(
    page_title="UIDAI Analytics Dashboard",
    page_icon="🪪",
    layout="wide",
)


# ------------------------------ Styling ------------------------------
CUSTOM_CSS = """
<style>
.main {background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);}

.kpi {
    border: 1px solid rgba(2,6,23,0.12);
    background: white;
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 6px 20px rgba(2,6,23,0.05);
}
.kpi .label {font-size: 12px; color:#334155;}
.kpi .value {font-size: 30px; font-weight: 900;}
.kpi .help  {font-size: 12px; color:#64748b;}

.section {
    border: 1px solid rgba(2,6,23,0.08);
    background: white;
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 6px 20px rgba(2,6,23,0.05);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #020617 100%);
}
section[data-testid="stSidebar"] * {color:#e5e7eb;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ------------------------------ File Discovery ------------------------------
BASE_DIR = os.environ.get("UIDAI_DATA_DIR", "")

# ------------------------------ Fixed File Names ------------------------------

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




ENROLMENT_FILES = _auto_discover("api_data_aadhar_enrolment_*.csv") or DEFAULT_ENROLMENT
BIOMETRIC_FILES = _auto_discover("api_data_aadhar_biometric_*.csv") or DEFAULT_BIOMETRIC
DEMOGRAPHIC_FILES = _auto_discover("api_data_aadhar_demographic_*.csv") or DEFAULT_DEMOGRAPHIC


# ------------------------------ Data Utils ------------------------------
@st.cache_data(show_spinner=False)
def load_concat(paths):
    dfs = []
    for p in paths:
        if p and os.path.exists(p):
            dfs.append(pd.read_csv(p))
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def normalize_common(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()

    # 🔑 CRITICAL FIX: normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)

    for col in ["state", "district"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "pincode" in df.columns:
        df["pincode"] = (
            df["pincode"]
            .astype(str)
            .str.replace(".0", "", regex=False)
            .str.zfill(6)
        )

    if "date" in df.columns:
        df["month"] = df["date"].dt.to_period("M").astype(str)

    return df


def add_total_column(df: pd.DataFrame, value_cols, total_name):
    df = df.copy()

    # 🔒 SAFE: ensure columns exist
    for col in value_cols:
        if col not in df.columns:
            df[col] = 0

    df[value_cols] = (
        df[value_cols]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
        .astype(int)
    )

    df[total_name] = df[value_cols].sum(axis=1)
    return df


def kpi(label, value, help_text=""):
    st.markdown(
        f"""
        <div class="kpi">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            {f"<div class='help'>{help_text}</div>" if help_text else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------ Sidebar ------------------------------
st.title("🪪 UIDAI Aadhaar Analytics Dashboard")
st.caption("Enrolment • Demographic • Biometric Analytics")

with st.sidebar:
    dataset = st.radio(
        "Choose Dataset",
        ["Enrolment", "Demographic", "Biometric", "Combined View"],
    )

    st.markdown("---")
    load_mode = st.selectbox(
        "Data Source",
        ["Use predefined files", "Upload single CSV"],
    )

    uploaded_path = None
    if load_mode == "Upload single CSV":
        up = st.file_uploader("Upload CSV", type="csv")
        if up:
            uploaded_path = "/tmp/upload.csv"
            pd.read_csv(up).to_csv(uploaded_path, index=False)


# ------------------------------ Load Data ------------------------------
if dataset == "Enrolment":
    df = normalize_common(load_concat([uploaded_path] if uploaded_path else ENROLMENT_FILES))
    df = add_total_column(df, ["age_0_5", "age_5_17", "age_18_greater"], "total_enrolments")
    metric_col = "total_enrolments"

elif dataset == "Demographic":
    df = normalize_common(load_concat([uploaded_path] if uploaded_path else DEMOGRAPHIC_FILES))
    df = add_total_column(df, ["demo_age_5_17", "demo_age_17_"], "total_demographic")
    metric_col = "total_demographic"

elif dataset == "Biometric":
    df = normalize_common(load_concat([uploaded_path] if uploaded_path else BIOMETRIC_FILES))
    df = add_total_column(df, ["bio_age_5_17", "bio_age_17_"], "total_biometric")
    metric_col = "total_biometric"

else:
    enr = add_total_column(
        normalize_common(load_concat(ENROLMENT_FILES)),
        ["age_0_5", "age_5_17", "age_18_greater"],
        "total_enrolments",
    )
    dem = add_total_column(
        normalize_common(load_concat(DEMOGRAPHIC_FILES)),
        ["demo_age_5_17", "demo_age_17_"],
        "total_demographic",
    )
    bio = add_total_column(
        normalize_common(load_concat(BIOMETRIC_FILES)),
        ["bio_age_5_17", "bio_age_17_"],
        "total_biometric",
    )

    key = ["date", "state", "district", "pincode", "month"]
    df = (
        enr.groupby(key, as_index=False)["total_enrolments"].sum()
        .merge(dem.groupby(key, as_index=False)["total_demographic"].sum(), on=key, how="outer")
        .merge(bio.groupby(key, as_index=False)["total_biometric"].sum(), on=key, how="outer")
        .fillna(0)
    )
    metric_col = "total_enrolments"


if df.empty:
    st.error("No data loaded.")
    st.stop()


# ------------------------------ Filters ------------------------------
min_date, max_date = df["date"].min(), df["date"].max()

with st.sidebar:
    date_range = st.date_input(
        "Date Range",
        (min_date.date(), max_date.date()),
    )

    states = st.multiselect("State", sorted(df["state"].dropna().unique()))
    districts = st.multiselect("District", sorted(df["district"].dropna().unique()))
    pin = st.text_input("Pincode")


fdf = df.copy()
start, end = date_range
fdf = fdf[(fdf["date"].dt.date >= start) & (fdf["date"].dt.date <= end)]

if states:
    fdf = fdf[fdf["state"].isin(states)]
if districts:
    fdf = fdf[fdf["district"].isin(districts)]
if pin:
    fdf = fdf[fdf["pincode"].str.contains(pin)]


# ------------------------------ Tabs ------------------------------
tab1, tab2, tab3 = st.tabs(["📌 Overview", "📈 Trends", "🧾 Data"])


with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Records", f"{len(fdf):,}")
    c2.metric("Total", f"{int(fdf[metric_col].sum()):,}")
    c3.metric("States", fdf["state"].nunique())
    c4.metric("Districts", fdf["district"].nunique())
    st.markdown("</div>", unsafe_allow_html=True)


with tab2:
    trend = fdf.groupby("date", as_index=False)[metric_col].sum()
    if PLOTLY_AVAILABLE:
        fig = px.line(trend, x="date", y=metric_col)
        st.plotly_chart(fig, width="stretch")
    else:
        st.line_chart(trend.set_index("date"))


with tab3:
    st.dataframe(fdf.head(5000), width="stretch")
    st.download_button(
        "Download CSV",
        fdf.to_csv(index=False),
        file_name="uidai_filtered.csv",
        mime="text/csv",
    )
