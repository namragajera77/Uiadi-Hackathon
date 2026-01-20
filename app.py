import os
import glob
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

# Plotly for interactive charts
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
/* Main background */
.main {
    background: linear-gradient(180deg, rgba(248,250,252,1) 0%, rgba(255,255,255,1) 100%);
}

/* Metric cards */

.kpi {min-height: 120px; display:flex; flex-direction:column; justify-content:center;}

.kpi {
    border: 1px solid rgba(2,6,23,0.12);
    background: rgba(255,255,255,0.95);
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 6px 20px rgba(2,6,23,0.05);
}

.kpi .label {font-size: 12px; opacity: 0.9; color: #0f172a;}
.kpi .value {font-size: 30px; font-weight: 900; margin-top: 4px; color: #0f172a;}
.kpi .help  {font-size: 12px; opacity: 0.8; margin-top: 6px; color: #334155;}

/* Improve readability in dark mode */
@media (prefers-color-scheme: dark) {
  .main {background: linear-gradient(180deg, #0b1220 0%, #020617 100%);}
  .section {background: rgba(15,23,42,0.75); border: 1px solid rgba(148,163,184,0.25);}
  .kpi {background: rgba(15,23,42,0.85); border: 1px solid rgba(148,163,184,0.25);}
  .kpi .label, .kpi .value {color: #f8fafc;}
  .kpi .help {color: #cbd5e1;}
  div[data-testid="stMetric"] {background: rgba(15,23,42,0.85) !important; border-radius: 18px; padding: 10px 14px; border: 1px solid rgba(148,163,184,0.25);} 
}

/* Section headers */
.section {
    border: 1px solid rgba(2,6,23,0.08);
    background: rgba(255,255,255,0.9);
    border-radius: 22px;
    padding: 18px 18px 4px 18px;
    box-shadow: 0 6px 20px rgba(2,6,23,0.05);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,23,42,1) 0%, rgba(2,6,23,1) 100%);
}
section[data-testid="stSidebar"] * {color: #e5e7eb;}
section[data-testid="stSidebar"] .stMarkdown p {color: #e5e7eb;}

/* Buttons */
.stDownloadButton button {
    border-radius: 999px !important;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ------------------------------ File discovery ------------------------------
# In your PC, you can set UIDAI_DATA_DIR env var to your folder e.g.
# setx UIDAI_DATA_DIR "D:\\Garv Pendrive\\UIDAI"
BASE_DIR = os.environ.get("UIDAI_DATA_DIR", "")

DEFAULT_ENROLMENT = [
    r"enrollment_all (1).csv"
]
DEFAULT_BIOMETRIC = [
    r"mightymerge.io__xzzeu4zp.csv"
]
DEFAULT_DEMOGRAPHIC = [
    r"demo_all (1).csv"
]


def _auto_discover(pattern: str) -> list[str]:
    if not BASE_DIR:
        return []
    paths = sorted(glob.glob(os.path.join(BASE_DIR, pattern)))
    return paths


ENROLMENT_FILES = _auto_discover("api_data_aadhar_enrolment_*.csv") or DEFAULT_ENROLMENT
BIOMETRIC_FILES = _auto_discover("api_data_aadhar_biometric_*.csv") or DEFAULT_BIOMETRIC
DEMOGRAPHIC_FILES = _auto_discover("api_data_aadhar_demographic_*.csv") or DEFAULT_DEMOGRAPHIC


# ------------------------------ Data loaders ------------------------------
@st.cache_data(show_spinner=False)
def load_concat(paths: list[str]) -> pd.DataFrame:
    dfs = []
    for p in paths:
        if os.path.exists(p):
            dfs.append(pd.read_csv(p))
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


def normalize_common(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    # Normalize columns
    df.columns = [c.strip() for c in df.columns]

    # Parse date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")

    # Normalize location fields
    for col in ["state", "district"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "pincode" in df.columns:
        df["pincode"] = df["pincode"].astype(str).str.replace(".0", "", regex=False).str.zfill(6)

    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


def add_total_column(df: pd.DataFrame, value_cols: list[str], total_name: str = "total") -> pd.DataFrame:
    df = df.copy()
    for col in value_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df[total_name] = df[value_cols].sum(axis=1)
    return df


# ------------------------------ KPI Card ------------------------------
def kpi(label: str, value: str, help_text: str = ""):
    st.markdown(
        f"""
        <div class="kpi">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            {f'<div class="help">{help_text}</div>' if help_text else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------ Sidebar ------------------------------
st.title("🪪 UIDAI Aadhaar Analytics Dashboard")
st.caption("User-friendly Streamlit dashboard for **Enrolment + Demographic + Biometric** Aadhaar datasets.")

with st.sidebar:
    st.markdown("## ⚙️ Controls")
    dataset = st.radio(
        "Choose dataset",
        ["Enrolment", "Demographic", "Biometric", "Combined View"],
        index=0,
    )

    st.markdown("---")
    st.markdown("### 📦 Data Source")
    load_mode = st.selectbox(
        "Load mode",
        [
            "Use predefined files (recommended)",
            "Upload a single CSV (for testing)",
        ],
        index=0,
    )

    uploaded_path = None
    if load_mode == "Upload a single CSV (for testing)":
        up = st.file_uploader("Upload CSV file", type=["csv"])
        if up is not None:
            uploaded_path = "/tmp/uploaded.csv"
            pd.read_csv(up).to_csv(uploaded_path, index=False)

    st.markdown("---")
    st.markdown("### 🎛️ Filters")


# ------------------------------ Load selected dataset ------------------------------
if dataset == "Enrolment":
    paths = [uploaded_path] if uploaded_path else ENROLMENT_FILES
    df = normalize_common(load_concat(paths))
    value_cols = ["age_0_5", "age_5_17", "age_18_greater"]
    df = add_total_column(df, value_cols, "total_enrolments")
    metric_col = "total_enrolments"

elif dataset == "Demographic":
    paths = [uploaded_path] if uploaded_path else DEMOGRAPHIC_FILES
    df = normalize_common(load_concat(paths))
    value_cols = ["demo_age_5_17", "demo_age_17_"]
    df = add_total_column(df, value_cols, "total_demographic")
    metric_col = "total_demographic"

elif dataset == "Biometric":
    paths = [uploaded_path] if uploaded_path else BIOMETRIC_FILES
    df = normalize_common(load_concat(paths))
    value_cols = ["bio_age_5_17", "bio_age_17_"]
    df = add_total_column(df, value_cols, "total_biometric")
    metric_col = "total_biometric"

else:
    # Combined view
    # Aggregate each dataset to common key and merge
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
    enr_agg = enr.groupby(key, as_index=False)["total_enrolments"].sum()
    dem_agg = dem.groupby(key, as_index=False)["total_demographic"].sum()
    bio_agg = bio.groupby(key, as_index=False)["total_biometric"].sum()

    df = enr_agg.merge(dem_agg, on=key, how="outer").merge(bio_agg, on=key, how="outer")
    df[["total_enrolments", "total_demographic", "total_biometric"]] = df[[
        "total_enrolments",
        "total_demographic",
        "total_biometric",
    ]].fillna(0).astype(int)

    df = df.sort_values("date")
    metric_col = "total_enrolments"  # default for charts


if df.empty:
    st.error("No data found. Please check your file paths or upload a CSV.")
    st.stop()


# ------------------------------ Filters (depend on data) ------------------------------
min_date = df["date"].min()
max_date = df["date"].max()

with st.sidebar:
    date_range = st.date_input(
        "📅 Date range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )

    state_opts = sorted(df["state"].dropna().unique().tolist())
    states = st.multiselect("🏙️ State", options=state_opts, default=[])

    if states:
        district_opts = sorted(df.loc[df["state"].isin(states), "district"].dropna().unique().tolist())
    else:
        district_opts = sorted(df["district"].dropna().unique().tolist())
    districts = st.multiselect("🏘️ District", options=district_opts, default=[])

    pin = st.text_input("📮 Pincode (optional)", value="", placeholder="e.g. 560043")

    st.markdown("---")
    st.markdown("### 📊 Chart Settings")
    top_n = st.slider("Top N", 5, 30, 10)
    group_view = st.selectbox("Group by", ["State", "District", "Pincode"], index=0)

    if dataset == "Combined View":
        metric_choice = st.selectbox(
            "Metric",
            ["total_enrolments", "total_demographic", "total_biometric"],
            index=0,
        )
        metric_col = metric_choice


# Apply filters
fdf = df.copy()
start, end = date_range
fdf = fdf[(fdf["date"].dt.date >= start) & (fdf["date"].dt.date <= end)]

if states:
    fdf = fdf[fdf["state"].isin(states)]
if districts:
    fdf = fdf[fdf["district"].isin(districts)]
if pin.strip():
    fdf = fdf[fdf["pincode"].astype(str).str.contains(pin.strip())]


# ------------------------------ Tabs Layout ------------------------------
TAB1, TAB2, TAB3 = st.tabs(["📌 Overview", "📈 Trends", "🧾 Data"])


# ------------------------------ Overview ------------------------------
with TAB1:
    st.markdown('<div class="section">', unsafe_allow_html=True)

    # KPIs row
    c1, c2, c3, c4, c5 = st.columns([1.1, 1.3, 1.1, 1.1, 1.1])

    with c1:
        kpi("Records", f"{len(fdf):,}")

    with c2:
        kpi("Total", f"{int(fdf[metric_col].sum()):,}", help_text=f"Metric: {metric_col}")

    with c3:
        kpi("States", f"{fdf['state'].nunique():,}")

    with c4:
        kpi("Districts", f"{fdf['district'].nunique():,}")

    with c5:
        kpi("Pincodes", f"{fdf['pincode'].nunique():,}")

    st.markdown("---")

    left, right = st.columns([1.3, 1])

    with left:
        st.subheader("🏆 Top contributors")
        group_col = {"State": "state", "District": "district", "Pincode": "pincode"}[group_view]
        rank = (
            fdf.groupby(group_col, as_index=False)[metric_col]
            .sum()
            .sort_values(metric_col, ascending=False)
            .head(top_n)
        )

        if PLOTLY_AVAILABLE:
            fig = px.bar(rank, x=metric_col, y=group_col, orientation="h")
            fig.update_layout(height=420, yaxis_title="", xaxis_title=metric_col)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.dataframe(rank, use_container_width=True)

    with right:
        st.subheader("🧩 Distribution")
        if dataset == "Enrolment":
            dist = fdf[["age_0_5", "age_5_17", "age_18_greater"]].sum().rename(
                {"age_0_5": "0-5", "age_5_17": "5-17", "age_18_greater": "18+"}
            )
        elif dataset == "Demographic":
            dist = fdf[["demo_age_5_17", "demo_age_17_"]].sum().rename(
                {"demo_age_5_17": "5-17", "demo_age_17_": "17+"}
            )
        elif dataset == "Biometric":
            dist = fdf[["bio_age_5_17", "bio_age_17_"]].sum().rename(
                {"bio_age_5_17": "5-17", "bio_age_17_": "17+"}
            )
        else:
            dist = pd.Series(
                {
                    "Enrolment": int(fdf["total_enrolments"].sum()),
                    "Demographic": int(fdf["total_demographic"].sum()),
                    "Biometric": int(fdf["total_biometric"].sum()),
                }
            )

        if PLOTLY_AVAILABLE:
            dist_df = dist.reset_index()
            dist_df.columns = ["group", "count"]
            pie = px.pie(dist_df, names="group", values="count", hole=0.55)
            pie.update_layout(height=420)
            st.plotly_chart(pie, use_container_width=True)
        else:
            st.bar_chart(dist)

    st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------ Trends ------------------------------
with TAB2:
    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.subheader("📈 Trend over time")
    trend = fdf.groupby("date", as_index=False)[metric_col].sum().sort_values("date")

    if PLOTLY_AVAILABLE:
        line = px.line(trend, x="date", y=metric_col)
        line.update_layout(height=420)
        st.plotly_chart(line, use_container_width=True)
    else:
        st.line_chart(trend.set_index("date")[metric_col])

    st.markdown("---")

    st.subheader("🗓️ Month-wise heatmap (Top 15 states)")
    heat = fdf.groupby(["state", "month"], as_index=False)[metric_col].sum()
    active_states = (
        fdf.groupby("state")[metric_col].sum().sort_values(ascending=False).head(15).index.tolist()
    )
    heat = heat[heat["state"].isin(active_states)]
    pivot = heat.pivot_table(index="state", columns="month", values=metric_col, aggfunc="sum").fillna(0)

    if PLOTLY_AVAILABLE:
        hm = px.imshow(pivot, aspect="auto")
        hm.update_layout(height=480, xaxis_title="Month", yaxis_title="State")
        st.plotly_chart(hm, use_container_width=True)
    else:
        st.dataframe(pivot, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------ Data ------------------------------
with TAB3:
    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.subheader("🧾 Preview")
    st.dataframe(fdf.head(5000), use_container_width=True)

    st.markdown("---")
    st.subheader("⬇️ Download")

    csv = fdf.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered dataset as CSV",
        data=csv,
        file_name=f"uidai_{dataset.lower().replace(' ','_')}_filtered.csv",
        mime="text/csv",
    )

    st.caption(
        "Run with: `python -m streamlit run app_v2.py`  |  Set your folder using UIDAI_DATA_DIR env variable."
    )

    st.markdown('</div>', unsafe_allow_html=True)