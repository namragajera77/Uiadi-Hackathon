import os
import pandas as pd
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="UIDAI Analytics Dashboard",
    page_icon="🪪",
    layout="wide",
)

# ---------------- FIXED FILE NAMES (ONLY THESE) ----------------
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
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)

# ---------------- NORMALIZATION ----------------
def normalize(df: pd.DataFrame) -> pd.DataFrame:
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

# ---------------- SAFE TOTAL ----------------
def add_total(df: pd.DataFrame, cols, total_name):
    df = df.copy()
    for c in cols:
        if c not in df.columns:
            df[c] = 0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df[total_name] = df[cols].sum(axis=1).astype(int)
    return df

# ---------------- UI ----------------
st.title("🪪 UIDAI Aadhaar Analytics Dashboard")
st.caption("Stable • Cloud-safe • No auto-discovery")

dataset = st.sidebar.radio(
    "Select Dataset",
    ["Enrolment", "Demographic", "Biometric", "Combined"],
)

# ---------------- LOAD DATA ----------------
if dataset == "Enrolment":
    df = normalize(load_files(ENROLMENT_FILES))
    df = add_total(df, ["age_0_5", "age_5_17", "age_18_greater"], "total")

elif dataset == "Demographic":
    df = normalize(load_files(DEMOGRAPHIC_FILES))
    df = add_total(df, ["demo_age_5_17", "demo_age_17_"], "total")

elif dataset == "Biometric":
    df = normalize(load_files(BIOMETRIC_FILES))
    df = add_total(df, ["bio_age_5_17", "bio_age_17_"], "total")

else:
    enr = add_total(
        normalize(load_files(ENROLMENT_FILES)),
        ["age_0_5", "age_5_17", "age_18_greater"],
        "enrolment",
    )
    dem = add_total(
        normalize(load_files(DEMOGRAPHIC_FILES)),
        ["demo_age_5_17", "demo_age_17_"],
        "demographic",
    )
    bio = add_total(
        normalize(load_files(BIOMETRIC_FILES)),
        ["bio_age_5_17", "bio_age_17_"],
        "biometric",
    )

    key = ["date", "state", "district", "pincode", "month"]
    df = (
        enr.groupby(key, as_index=False)["enrolment"].sum()
        .merge(dem.groupby(key, as_index=False)["demographic"].sum(), on=key, how="outer")
        .merge(bio.groupby(key, as_index=False)["biometric"].sum(), on=key, how="outer")
        .fillna(0)
    )
    df["total"] = df[["enrolment", "demographic", "biometric"]].sum(axis=1).astype(int)

# ---------------- SAFETY ----------------
if df.empty:
    st.error("❌ No data loaded. Check CSV file names.")
    st.stop()

# ---------------- FILTER ----------------
min_date, max_date = df["date"].min(), df["date"].max()
start, end = st.sidebar.date_input(
    "Date Range",
    (min_date.date(), max_date.date()),
)

fdf = df[(df["date"].dt.date >= start) & (df["date"].dt.date <= end)]

# ---------------- METRICS ----------------
c1, c2, c3 = st.columns(3)
c1.metric("Records", f"{len(fdf):,}")
c2.metric("Total Count", f"{int(fdf['total'].sum()):,}")
c3.metric("States", fdf["state"].nunique())

# ---------------- TREND ----------------
st.subheader("Trend Over Time")
st.line_chart(fdf.groupby("date")["total"].sum())

# ---------------- DATA ----------------
st.subheader("Data Preview")
st.dataframe(fdf.head(5000), width="stretch")

st.download_button(
    "Download CSV",
    fdf.to_csv(index=False),
    file_name="uidai_filtered.csv",
    mime="text/csv",
)
