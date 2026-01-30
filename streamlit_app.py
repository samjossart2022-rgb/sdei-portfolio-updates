import os
import sys
import subprocess
import pandas as pd
import streamlit as st

DATA_PATH = os.path.join("data", "data.csv")

st.set_page_config(page_title="SD Funding & Ecosystem Tracker", layout="wide")
st.title("South Dakota Funding & Ecosystem Tracker")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        df = pd.read_csv(path)
    else:
        df = pd.DataFrame(columns=[
            "date","type","company","headline","round","amount","investors",
            "sector","county","source_url"
        ])
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df

def run_ingest():
    # Runs src.ingest using the same Python interpreter Streamlit is using
    cmd = [sys.executable, "-m", "src.ingest"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        st.error("Refresh failed. See details below.")
        st.code(result.stderr or result.stdout)
        return False
    return True

if st.button("🔄 Refresh Data"):
    with st.spinner("Fetching latest startup data..."):
        ok = run_ingest()
    if ok:
        st.cache_data.clear()
        st.success("Data refreshed. Reloading...")
        st.rerun()

df = load_data(DATA_PATH)

# Sidebar filters
st.sidebar.header("Filters")

sector_opts = sorted([s for s in df.get("sector", pd.Series()).dropna().unique() if str(s).strip()])
round_opts  = sorted([s for s in df.get("round", pd.Series()).dropna().unique() if str(s).strip()])
county_opts = sorted([s for s in df.get("county", pd.Series()).dropna().unique() if str(s).strip()])

sector = st.sidebar.multiselect("Sector", sector_opts, [])
stage  = st.sidebar.multiselect("Stage/Round", round_opts, [])
county = st.sidebar.multiselect("County", county_opts, [])

month_opts = ["All"]
if "date" in df.columns and df["date"].notna().any():
    month_opts += sorted(df["date"].dropna().dt.to_period("M").astype(str).unique().tolist())
month = st.sidebar.selectbox("Month", month_opts)

filtered = df.copy()
if sector and "sector" in filtered.columns:
    filtered = filtered[filtered["sector"].isin(sector)]
if stage and "round" in filtered.columns:
    filtered = filtered[filtered["round"].isin(stage)]
if county and "county" in filtered.columns:
    filtered = filtered[filtered["county"].isin(county)]
if month and month != "All" and "date" in filtered.columns:
    pm = pd.Period(month)
    filtered = filtered[filtered["date"].dt.to_period("M") == pm]

st.subheader("Overview")
st.metric("Total Records", len(df))
st.metric("Unique Sources", df["source_url"].nunique() if "source_url" in df.columns else 0)

if "sector" in df.columns:
    st.bar_chart(df["sector"].value_counts())

st.write(f"Total records: **{len(df)}** | Showing: **{len(filtered)}**")

cols = ["date","type","company","headline","round","amount","investors","sector","county","source_url"]
for c in cols:
    if c not in filtered.columns:
        filtered[c] = None

st.dataframe(
    filtered.sort_values(by=["date"], ascending=False).assign(
        date=lambda x: x["date"].dt.date.astype("string") if "date" in x.columns else ""
    )[cols],
    use_container_width=True,
)

st.caption("Tip: Edit `src/sources.yaml` to add more feeds. Use Refresh Data to run `python -m src.ingest`.")