import os
import pandas as pd
import streamlit as st
import os
import pandas as pd
import streamlit as st

DATA_PATH = os.path.join("data", "data.csv")

DATA_PATH = os.path.join("data", "data.csv")

st.set_page_config(page_title="SD Funding & Ecosystem Tracker", layout="wide")
st.title("South Dakota Funding & Ecosystem Tracker")
if st.button("🔄 Refresh Data"):
    with st.spinner("Fetching latest startup data..."):
        os.system("python -m src.ingest")
        st.success("Data refreshed successfully! Please reload the dashboard.")
@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
    else:
        df = pd.DataFrame(columns=[
            "date","type","company","headline","round","amount","investors","sector","county","source_url"
        ])
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
sector = st.sidebar.multiselect("Sector", sorted([s for s in df["sector"].dropna().unique() if str(s).strip()]), [])
stage = st.sidebar.multiselect("Stage/Round", sorted([s for s in df["round"].dropna().unique() if str(s).strip()]), [])
county = st.sidebar.multiselect("County", sorted([s for s in df["county"].dropna().unique() if str(s).strip()]), [])
month = st.sidebar.selectbox("Month", ["All"] + sorted(df["date"].dropna().dt.to_period("M").astype(str).unique().tolist()))

filtered = df.copy()
if sector:
    filtered = filtered[filtered["sector"].isin(sector)]
if stage:
    filtered = filtered[filtered["round"].isin(stage)]
if county:
    filtered = filtered[filtered["county"].isin(county)]
if month and month != "All":
    pm = pd.Period(month)
    filtered = filtered[filtered["date"].dt.to_period("M") == pm]

st.subheader("Overview")
import pandas as pd

df = pd.read_csv("data/data.csv")

st.metric("Total Records", len(df))
st.metric("Unique Sources", df['source_url'].nunique())

st.bar_chart(df['sector'].value_counts())
st.write(f"Total records: **{len(df)}** | Showing: **{len(filtered)}**")

st.dataframe(
    filtered.sort_values(by=["date"], ascending=False).assign(
        date=lambda x: x["date"].dt.date.astype("string")
    )[["date","type","company","headline","round","amount","investors","sector","county","source_url"]],
    use_container_width=True,
)

st.caption("Tip: Edit `src/sources.yaml` to add more feeds. Run `python -m src.ingest` to refresh.")
