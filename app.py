"""EV Charging Station Demand – interactive Streamlit dashboard.
Cleaning steps mirror the EDA notebook (Final_EDA_EV_Project_updated).
Run:  streamlit run app.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="EV Charging Demand Dashboard", page_icon="⚡", layout="wide")

DEFAULT_CSV = Path(__file__).parent / "EV_Charging_Station_Demand_104500_with_NaN.csv"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
NUM_COLS = ["battery_capacity_kWh", "charging_power_kW", "energy_consumed_kWh", "charging_duration_min",
            "station_load_percent", "available_chargers", "occupied_chargers",
            "utilization_rate_percent", "charging_demand", "electricity_price_per_kWh"]
TRAFFIC_ORDER = ["Low", "Medium", "High", "Very_High"]
COLORS = ["#00B386", "#6C5CE7", "#FF7A59", "#0984E3", "#FDCB6E", "#E84393", "#00CEC9", "#636E72"]
SEQ = [[0, "#E8FFF6"], [0.5, "#00B386"], [1, "#0B3D5C"]]
DIV = [[0, "#E84393"], [0.5, "#FFFFFF"], [1, "#0984E3"]]
HEAT = [[0, "#FFF8E1"], [0.5, "#FF7A59"], [1, "#6C1D45"]]

import plotly.io as pio
import plotly.graph_objects as go
pio.templates["ev"] = go.layout.Template(layout=dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#1F2D3D", family="Inter, Helvetica, Arial, sans-serif"),
    colorway=COLORS, title=dict(font=dict(size=16, color="#0B3D5C")),
    xaxis=dict(gridcolor="#E3EAF2", linecolor="#C5D0DC", zerolinecolor="#C5D0DC"),
    yaxis=dict(gridcolor="#E3EAF2", linecolor="#C5D0DC", zerolinecolor="#C5D0DC"),
    colorscale=dict(sequential=SEQ, sequentialminus=SEQ, diverging=DIV),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    margin=dict(t=55, l=10, r=10, b=10)))
pio.templates.default = "ev"
px.defaults.template = "ev"

CSS = """
<style>
.stApp { background:linear-gradient(180deg,#F3FBF8 0%,#F5F7FF 55%,#FFF7F2 100%); color:#1F2D3D; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0B3D5C 0%,#14597E 100%); }
[data-testid="stSidebar"] * { color:#F2FAFF !important; }
[data-testid="stSidebar"] [data-baseweb="select"] * { color:#1F2D3D !important; }
h1,h2,h3 { letter-spacing:-0.02em; color:#0B3D5C; }
.hero { background:linear-gradient(120deg,#00B386 0%,#0984E3 55%,#6C5CE7 100%); color:#fff;
        padding:26px 32px; margin-bottom:18px; border-radius:18px; box-shadow:0 10px 30px rgba(9,132,227,.25); }
.hero h1 { margin:0; font-weight:800; font-size:2.2rem; color:#fff; }
.hero p { margin:6px 0 0; color:rgba(255,255,255,.88); }
[data-testid="stMetric"] { background:#fff; border:1px solid #E3EAF2; border-top:4px solid #00B386;
        padding:14px 16px; border-radius:14px; box-shadow:0 4px 14px rgba(11,61,92,.07); }
div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stMetric"] { border-top-color:#6C5CE7; }
div[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetric"] { border-top-color:#FF7A59; }
div[data-testid="stHorizontalBlock"] > div:nth-child(4) [data-testid="stMetric"] { border-top-color:#0984E3; }
div[data-testid="stHorizontalBlock"] > div:nth-child(5) [data-testid="stMetric"] { border-top-color:#E84393; }
[data-testid="stMetricValue"] { font-weight:800; color:#0B3D5C; }
[data-testid="stMetricLabel"] { color:#6B7C8F; text-transform:uppercase; font-size:.72rem; letter-spacing:.08em; }
button[data-baseweb="tab"] { font-weight:700; font-size:.9rem; border-radius:10px 10px 0 0; }
button[data-baseweb="tab"][aria-selected="true"] { color:#00B386 !important; }
div[data-baseweb="tab-highlight"] { background:#00B386 !important; height:3px; }
.objective { background:#fff; border:1px solid #E3EAF2; border-left:5px solid #6C5CE7; border-radius:14px;
       padding:14px 20px; margin:0 0 18px; box-shadow:0 4px 14px rgba(11,61,92,.07); color:#1F2D3D; }
.objective h4 { margin:0 0 6px; color:#0B3D5C; font-size:1.02rem; letter-spacing:-0.01em; }
.objective p { margin:0; font-size:.95rem; line-height:1.55; }
.sec { background:linear-gradient(90deg,#E6FAF3,transparent); border-left:5px solid #00B386;
       padding:8px 14px; margin:26px 0 10px; font-size:1.15rem; font-weight:700; color:#0B3D5C; border-radius:4px; }
[data-testid="stPlotlyChart"] { background:#fff; border:1px solid #E3EAF2; border-radius:14px;
       padding:6px; box-shadow:0 4px 14px rgba(11,61,92,.06); }
.stDownloadButton button { background:linear-gradient(90deg,#00B386,#0984E3); color:#fff; border:0; font-weight:700; border-radius:10px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---- optional images: drop files named background.* and banner.* next to app.py ----
import base64, mimetypes


def find_image(stem):
    for ext in ("jpg", "jpeg", "png", "webp", "gif"):
        p = Path(__file__).parent / f"{stem}.{ext}"
        if p.exists():
            mime = mimetypes.guess_type(p.name)[0] or "image/jpeg"
            return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()
    return None


BG_IMG, BANNER_IMG = find_image("background"), find_image("banner")
if BG_IMG:
    st.markdown(f"""<style>.stApp {{ background-image:linear-gradient(rgba(245,249,255,.86),rgba(245,249,255,.86)),
    url("{BG_IMG}"); background-size:cover; background-attachment:fixed; background-position:center; }}</style>""",
                unsafe_allow_html=True)
HERO_STYLE = ""
if BANNER_IMG:
    HERO_STYLE = (' style="background-image:linear-gradient(120deg,rgba(0,179,134,.72),rgba(9,132,227,.62),'
                  f'rgba(108,92,231,.72)),url({BANNER_IMG});background-size:cover;background-position:center;"')


def sec(t):
    st.markdown(f'<div class="sec">{t}</div>', unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading data…")
def load_raw(src):
    return pd.read_csv(src)


@st.cache_data(show_spinner="Cleaning data…")
def clean(raw: pd.DataFrame):
    """Same pipeline as the notebook. Returns (clean_df, quality_stats)."""
    stats = {"raw_rows": len(raw), "missing": raw.isna().sum()}
    df = raw.drop_duplicates()
    stats["dupes"] = len(raw) - len(df)
    n = len(df)
    df = df.dropna(subset=["charging_demand"]).copy()
    stats["no_target"] = n - len(df)

    for c in ["location_type", "vehicle_type", "charger_type", "traffic_density"]:
        df[c] = df[c].fillna(df[c].mode()[0])
    for c in ["battery_capacity_kWh", "energy_consumed_kWh", "charging_duration_min"]:
        df[c] = df[c].fillna(df.groupby("vehicle_type")[c].transform("median"))
    df["charging_power_kW"] = df["charging_power_kW"].fillna(
        df.groupby("charger_type")["charging_power_kW"].transform("median"))

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["month"] = df["timestamp"].dt.month
    df["day_of_week"] = df["timestamp"].dt.day_name()
    df["is_weekend"] = df["timestamp"].dt.dayofweek >= 5
    df["peak_hour"] = df["peak_hour"].map({"TRUE": True, "FALSE": False, True: True, False: False})
    df["peak_hour"] = df["peak_hour"].fillna(df["hour"].isin([8, 9, 10, 17, 18, 19, 20])).astype(bool)
    df = df.fillna(df.median(numeric_only=True))

    cap = ["station_load_percent", "occupied_chargers"]
    q1, q3 = df[cap].quantile(0.25), df[cap].quantile(0.75)
    iqr = q3 - q1
    df[cap] = df[cap].clip(lower=q1 - 1.5 * iqr, upper=q3 + 1.5 * iqr, axis=1)
    df["demand_level"] = pd.qcut(df["charging_demand"], q=3, labels=["Low", "Medium", "High"])
    stats["clean_rows"] = len(df)
    return df, stats


# ---------------------------------------------------------------- data
if not DEFAULT_CSV.exists():
    st.error(f"Put **{DEFAULT_CSV.name}** in the same folder as app.py.")
    st.stop()
raw = load_raw(DEFAULT_CSV)
df_all, qs = clean(raw)

# ---------------------------------------------------------------- sidebar
st.sidebar.markdown("## ⚡ EV Charging")
st.sidebar.caption("Filters apply to every tab except Data quality.")
states = st.sidebar.multiselect("State", sorted(df_all["state"].unique()))
locs = st.sidebar.multiselect("Location type", sorted(df_all["location_type"].unique()))
vehs = st.sidebar.multiselect("Vehicle type", sorted(df_all["vehicle_type"].unique()))
chs = st.sidebar.multiselect("Charger type", sorted(df_all["charger_type"].unique()))
traf = st.sidebar.multiselect("Traffic density", TRAFFIC_ORDER)
peak = st.sidebar.radio("Peak hour", ["All", "Peak only", "Non-peak only"], horizontal=True)
wk = st.sidebar.radio("Day type", ["All", "Weekend", "Weekday"], horizontal=True)
hr = st.sidebar.slider("Hour of day", 0, 23, (0, 23))
months = st.sidebar.multiselect("Month", list(range(1, 13)))

df = df_all
for col, sel in [("state", states), ("location_type", locs), ("vehicle_type", vehs),
                 ("charger_type", chs), ("traffic_density", traf), ("month", months)]:
    if sel:
        df = df[df[col].isin(sel)]
if peak != "All":
    df = df[df["peak_hour"] == (peak == "Peak only")]
if wk != "All":
    df = df[df["is_weekend"] == (wk == "Weekend")]
df = df[df["hour"].between(*hr)]
st.sidebar.caption(f"**{len(df):,}** of {len(df_all):,} sessions selected")

st.markdown(f'<div class="hero"{HERO_STYLE}><h1>EV CHARGING STATION DEMAND</h1>'
            '<p>⚡ Exploratory data analysis dashboard · India · 2024</p></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="objective"><h4>🎯 Project objective</h4>'
    '<p>To explore EV charging station data from across India and understand <b>when, where and why '
    'charging demand rises</b>. The dashboard cleans the raw data, then uses univariate, bivariate and '
    'multivariate analysis to show how time of day, location, vehicle type, charger type and traffic '
    'density affect demand. These insights can help operators plan stations and manage load.</p></div>',
    unsafe_allow_html=True)
if df.empty:
    st.warning("No sessions match the current filters.")
    st.stop()

CAT_COLS = ["state", "location_type", "vehicle_type", "charger_type", "traffic_density", "day_of_week"]
tabs = st.tabs(["Overview", "Data", "Data quality", "Univariate", "Bivariate",
                "Multivariate", "Pivot tables", "Key findings"])

# ================================================================ 1 OVERVIEW
with tabs[0]:
    c = st.columns(5)
    c[0].metric("Sessions", f"{len(df):,}")
    c[1].metric("Avg charging demand", f"{df.charging_demand.mean():.1f}")
    c[2].metric("Avg station load %", f"{df.station_load_percent.mean():.1f}")
    c[3].metric("Avg price / kWh", f"{df.electricity_price_per_kWh.mean():.2f}")
    c[4].metric("Stations", f"{df.station_id.nunique():,}")

    a, b = st.columns(2)
    m = df.groupby("month").size().reset_index(name="sessions")
    a.plotly_chart(px.line(m, x="month", y="sessions", markers=True, title="Sessions per month")
                   .update_xaxes(dtick=1), use_container_width=True)
    h = df.groupby("hour").size().reset_index(name="sessions")
    b.plotly_chart(px.line(h, x="hour", y="sessions", markers=True, title="Sessions per hour of day"),
                   use_container_width=True)
    a, b = st.columns(2)
    sd = df.groupby("state")["charging_demand"].mean().sort_values().reset_index()
    a.plotly_chart(px.bar(sd, x="charging_demand", y="state", orientation="h",
                          title="Average charging demand by state",
                          labels={"charging_demand": "Avg demand"}), use_container_width=True)
    hw = df.groupby(["hour", "is_weekend"])["charging_demand"].mean().reset_index()
    hw["Day type"] = hw["is_weekend"].map({True: "Weekend", False: "Weekday"})
    b.plotly_chart(px.line(hw, x="hour", y="charging_demand", color="Day type", markers=True,
                           line_dash="Day type", title="Average demand by hour"), use_container_width=True)

    sec("Location-wise demand")
    a, b = st.columns(2)
    ld = df.groupby("location_type")["charging_demand"].agg(["mean", "count"]).reset_index().sort_values("mean")
    a.plotly_chart(px.bar(ld, x="mean", y="location_type", orientation="h", color="location_type",
                          text=ld["mean"].round(1), title="Average charging demand by location type",
                          labels={"mean": "Avg demand", "location_type": "Location"})
                   .update_layout(showlegend=False), use_container_width=True)
    b.plotly_chart(px.pie(ld, names="location_type", values="count", hole=0.55,
                          title="Share of sessions by location type"), use_container_width=True)
    lh = df.groupby(["hour", "location_type"])["charging_demand"].mean().reset_index()
    st.plotly_chart(px.line(lh, x="hour", y="charging_demand", color="location_type",
                            title="Average demand by hour – per location type"), use_container_width=True)

    sec("Vehicle type")
    a, b = st.columns(2)
    vd = df.groupby("vehicle_type")["charging_demand"].agg(["mean", "count"]).reset_index().sort_values("mean")
    a.plotly_chart(px.bar(vd, x="mean", y="vehicle_type", orientation="h", color="vehicle_type",
                          text=vd["mean"].round(1), title="Average charging demand by vehicle type",
                          labels={"mean": "Avg demand", "vehicle_type": "Vehicle"})
                   .update_layout(showlegend=False), use_container_width=True)
    b.plotly_chart(px.bar(vd.sort_values("count"), x="count", y="vehicle_type", orientation="h",
                          color="vehicle_type", text="count", title="Sessions by vehicle type",
                          labels={"count": "Sessions", "vehicle_type": "Vehicle"})
                   .update_layout(showlegend=False), use_container_width=True)
    lv = df.groupby(["location_type", "vehicle_type"])["charging_demand"].mean().reset_index()
    st.plotly_chart(px.bar(lv, x="location_type", y="charging_demand", color="vehicle_type", barmode="group",
                           title="Average demand – location type × vehicle type",
                           labels={"charging_demand": "Avg demand"}), use_container_width=True)

# ================================================================ 2 DATA
with tabs[1]:
    c = st.columns(4)
    c[0].metric("Rows (selection)", f"{len(df):,}")
    c[1].metric("Columns", f"{df.shape[1]}")
    c[2].metric("Numeric columns", f"{df.select_dtypes('number').shape[1]}")
    c[3].metric("Missing values", f"{int(df.isna().sum().sum())}")

    sec("Data preview")
    n = st.slider("Rows to show", 5, 200, 20, 5)
    view = st.radio("View", ["Head", "Tail", "Random sample"], horizontal=True)
    show = df.drop(columns=["demand_level"])
    st.dataframe(show.head(n) if view == "Head" else show.tail(n) if view == "Tail"
                 else show.sample(min(n, len(show)), random_state=1), use_container_width=True)

    sec("Describe – numeric columns")
    st.dataframe(df.select_dtypes("number").describe().T.round(2), use_container_width=True)

    sec("Describe – categorical columns")
    st.dataframe(df[["state", "location_type", "vehicle_type", "charger_type", "traffic_density",
                     "day_of_week", "peak_hour", "is_weekend", "demand_level"]]
                 .astype(str).describe().T, use_container_width=True)

    sec("Column info")
    info = pd.DataFrame({"dtype": df.dtypes.astype(str), "non-null": df.notna().sum(),
                         "unique": df.nunique()})
    st.dataframe(info, use_container_width=True)
    st.download_button("Download filtered data (CSV)", df.to_csv(index=False).encode(),
                       "ev_filtered.csv", "text/csv")

# ================================================================ 3 DATA QUALITY
with tabs[2]:
    sec("Cleaning summary (full dataset, unaffected by filters)")
    c = st.columns(4)
    c[0].metric("Raw rows", f"{qs['raw_rows']:,}")
    c[1].metric("Duplicates removed", f"{qs['dupes']:,}")
    c[2].metric("Rows w/o target dropped", f"{qs['no_target']:,}")
    c[3].metric("Clean rows", f"{qs['clean_rows']:,}")
    ms = qs["missing"][qs["missing"] > 0].sort_values().reset_index()
    ms.columns = ["column", "missing"]
    ms["% of raw rows"] = (ms["missing"] / qs["raw_rows"] * 100).round(2)
    a, b = st.columns([3, 2])
    a.plotly_chart(px.bar(ms, x="missing", y="column", orientation="h",
                          title="Missing values per column (raw)"), use_container_width=True)
    b.dataframe(ms.sort_values("missing", ascending=False), hide_index=True, use_container_width=True)
    st.markdown("""
**Treatment** – target rows dropped; categoricals → mode; battery / energy / duration → median per vehicle type;
power → median per charger type; date fields rebuilt from `timestamp`; `peak_hour` from hour rule (08–10, 17–20);
remaining numerics → median; `station_load_percent` and `occupied_chargers` capped with the IQR rule.""")
    sec("Outliers (IQR rule, on current selection)")
    q1, q3 = df[NUM_COLS].quantile(0.25), df[NUM_COLS].quantile(0.75)
    iqr = q3 - q1
    lo, up_ = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    oc = ((df[NUM_COLS] < lo) | (df[NUM_COLS] > up_)).sum()
    st.dataframe(pd.DataFrame({"lower": lo.round(2), "upper": up_.round(2), "outliers": oc,
                               "percent": (oc / len(df) * 100).round(2)}), use_container_width=True)
    sec("Box plots – outlier detection")
    bcol = st.selectbox("Column", NUM_COLS, index=NUM_COLS.index("charging_demand"), key="dq_box")
    st.plotly_chart(px.box(df, x=bcol, points="outliers", title=f"Box plot – {bcol}"), use_container_width=True)

# ================================================================ 4 UNIVARIATE
with tabs[3]:
    sec("Numeric columns – distribution")
    col = st.selectbox("Numeric column", NUM_COLS, index=NUM_COLS.index("charging_demand"), key="uni_num")
    a, b = st.columns(2)
    a.plotly_chart(px.histogram(df, x=col, nbins=40, marginal="box", title=f"Histogram – {col}"),
                   use_container_width=True)
    dens = df[col].dropna()
    kde = px.histogram(df, x=col, nbins=60, histnorm="probability density",
                       title=f"Density – {col}")
    kde.update_traces(opacity=0.35)
    b.plotly_chart(kde, use_container_width=True)

    sec("Categorical columns – counts")
    cat = st.selectbox("Categorical column", CAT_COLS, key="uni_cat")
    vc = df[cat].value_counts().reset_index()
    if cat == "day_of_week":
        vc[cat] = pd.Categorical(vc[cat], DAYS, ordered=True); vc = vc.sort_values(cat)
    elif cat == "traffic_density":
        vc[cat] = pd.Categorical(vc[cat], TRAFFIC_ORDER, ordered=True); vc = vc.sort_values(cat)
    a, b = st.columns(2)
    a.plotly_chart(px.bar(vc, x=cat, y="count", title=f"Sessions by {cat}"), use_container_width=True)
    b.plotly_chart(px.pie(vc, names=cat, values="count", hole=0.55, title=f"Share of sessions – {cat}"),
                   use_container_width=True)

    sec("Balance checks")
    cc = st.columns(3)
    d = df["demand_level"].value_counts().reset_index()
    cc[0].plotly_chart(px.bar(d, x="demand_level", y="count", title="Demand level"), use_container_width=True)
    p = df["peak_hour"].astype(str).value_counts().reset_index()
    cc[1].plotly_chart(px.bar(p, x="peak_hour", y="count", title="Peak hour"), use_container_width=True)
    w = df["is_weekend"].astype(str).value_counts().reset_index()
    cc[2].plotly_chart(px.bar(w, x="is_weekend", y="count", title="Weekend"), use_container_width=True)

    sec("Sessions over time")
    a, b = st.columns(2)
    dd = df["day_of_week"].value_counts().reindex(DAYS).reset_index()
    dd.columns = ["day_of_week", "sessions"]
    a.plotly_chart(px.bar(dd, x="day_of_week", y="sessions", title="Sessions by day of week"), use_container_width=True)
    ts = df.set_index("timestamp").resample("W").size().reset_index(name="sessions")
    b.plotly_chart(px.line(ts, x="timestamp", y="sessions", title="Weekly sessions"), use_container_width=True)

# ================================================================ 5 BIVARIATE
with tabs[4]:
    sec("Average charging demand by category")
    cat = st.selectbox("Group by",
                       ["peak_hour", "is_weekend", "traffic_density", "location_type", "charger_type",
                        "vehicle_type", "state", "day_of_week", "month", "hour"], key="bi_cat")
    g = df.groupby(cat)["charging_demand"].mean().reset_index()
    if cat == "day_of_week":
        g[cat] = pd.Categorical(g[cat], DAYS, ordered=True); g = g.sort_values(cat)
    elif cat == "traffic_density":
        g[cat] = pd.Categorical(g[cat], TRAFFIC_ORDER, ordered=True); g = g.sort_values(cat)
    elif cat in ("month", "hour"):
        g = g.sort_values(cat)
    else:
        g = g.sort_values("charging_demand")
    g[cat] = g[cat].astype(str)
    fig = (px.line(g, x=cat, y="charging_demand", markers=True) if cat in ("month", "hour", "day_of_week")
           else px.bar(g, x=cat, y="charging_demand"))
    a, b = st.columns(2)
    a.plotly_chart(fig.update_layout(title=f"Average demand by {cat}"), use_container_width=True)
    b.plotly_chart(px.box(df, x=cat if cat not in ("month", "hour") else df[cat].astype(str),
                          y="charging_demand", points=False, title=f"Demand spread by {cat}"),
                   use_container_width=True)

    sec("Demand vs numeric driver")
    a, b = st.columns([1, 3])
    xcol = a.selectbox("X axis", [c for c in NUM_COLS if c != "charging_demand"],
                       index=NUM_COLS.index("station_load_percent"))
    colorby = a.selectbox("Colour by", ["None", "peak_hour", "traffic_density", "location_type"])
    ns = a.slider("Sample size", 500, min(20000, len(df)), min(5000, len(df)), 500) if len(df) > 500 else len(df)
    smp = df.sample(min(ns, len(df)), random_state=1)
    try:
        sc = px.scatter(smp, x=xcol, y="charging_demand", opacity=0.4,
                        color=None if colorby == "None" else colorby,
                        trendline="ols" if colorby == "None" else None)
    except Exception:
        sc = px.scatter(smp, x=xcol, y="charging_demand", opacity=0.4,
                        color=None if colorby == "None" else colorby)
    b.plotly_chart(sc.update_layout(title=f"Charging demand vs {xcol} ({len(smp):,} sampled sessions)"),
                   use_container_width=True)

    sec("Top vs bottom states – demand by hour")
    k = st.slider("Number of states", 1, 5, 3)
    sm = df.groupby("state")["charging_demand"].mean().sort_values()
    sel = list(sm.index[-k:]) + list(sm.index[:k])
    hh = df[df["state"].isin(sel)].groupby(["hour", "state"])["charging_demand"].mean().reset_index()
    st.plotly_chart(px.line(hh, x="hour", y="charging_demand", color="state", line_dash="state",
                            markers=True, title=f"Top {k} and bottom {k} states by average demand"),
                    use_container_width=True)

# ================================================================ 6 MULTIVARIATE
with tabs[5]:
    key = ["station_load_percent", "occupied_chargers", "utilization_rate_percent",
           "available_chargers", "charging_demand"]
    allnum = st.checkbox("Correlation of all numeric columns", value=False)
    cols = NUM_COLS if allnum else key
    a, b = st.columns(2)
    a.plotly_chart(px.imshow(df[cols].corr(), text_auto=".2f", color_continuous_scale=DIV,
                             zmin=-1, zmax=1, title="Correlation heatmap"), use_container_width=True)
    pv = pd.pivot_table(df, values="energy_consumed_kWh", index="vehicle_type", columns="charger_type", aggfunc="mean")
    b.plotly_chart(px.imshow(pv, text_auto=".1f", color_continuous_scale=SEQ,
                             title="Avg energy consumed (kWh) – vehicle × charger"), use_container_width=True)
    h3 = pd.pivot_table(df, values="charging_demand", index="state", columns="hour", aggfunc="mean")
    h3 = h3.loc[df.groupby("state")["charging_demand"].mean().sort_values(ascending=False).index]
    st.plotly_chart(px.imshow(h3, color_continuous_scale=HEAT, aspect="auto",
                              labels=dict(color="Avg demand"), title="Average demand – state × hour of day"),
                    use_container_width=True)
    sec("Three-variable view")
    c = st.columns(3)
    xx = c[0].selectbox("X", [x for x in NUM_COLS if x != "charging_demand"], index=4, key="m_x")
    yy = c[1].selectbox("Y", NUM_COLS, index=NUM_COLS.index("charging_demand"), key="m_y")
    cc = c[2].selectbox("Colour / group", ["peak_hour", "traffic_density", "location_type", "charger_type",
                                          "vehicle_type", "is_weekend"], key="m_c")
    s3 = df.sample(min(5000, len(df)), random_state=2).copy()
    s3[cc] = s3[cc].astype(str)
    st.plotly_chart(px.scatter(s3, x=xx, y=yy, color=cc, symbol=cc, opacity=0.5,
                               title=f"{yy} vs {xx} by {cc}"), use_container_width=True)

# ================================================================ 7 PIVOT TABLES
def style_pt(pt):
    return pt.style.background_gradient(cmap="YlGnBu", axis=None).format("{:.1f}")


with tabs[6]:
    sec("Average demand: state × location type")
    pt1 = pd.pivot_table(df, values="charging_demand", index="state", columns="location_type",
                         aggfunc="mean", margins=True, margins_name="Overall").round(1)
    st.dataframe(style_pt(pt1), use_container_width=True)

    sec("Build your own pivot table")
    c = st.columns(4)
    idx = c[0].selectbox("Rows", ["state", "location_type", "vehicle_type", "charger_type", "traffic_density",
                                  "day_of_week", "month", "hour"], index=0)
    colx = c[1].selectbox("Columns", ["location_type", "vehicle_type", "charger_type", "traffic_density",
                                      "peak_hour", "is_weekend", "state", "day_of_week"], index=0)
    val = c[2].selectbox("Value", NUM_COLS, index=NUM_COLS.index("charging_demand"))
    agg = c[3].selectbox("Aggregation", ["mean", "median", "sum", "count", "max", "min"])
    if idx == colx:
        st.info("Choose different row and column fields.")
    else:
        pt = pd.pivot_table(df, values=val, index=idx, columns=colx, aggfunc=agg,
                            margins=True, margins_name="Overall").round(1)
        st.dataframe(style_pt(pt), use_container_width=True)
        st.download_button("Download pivot as CSV", pt.to_csv().encode(), "pivot.csv", "text/csv")

# ================================================================ 8 KEY FINDINGS
with tabs[7]:
    sec("Key findings (computed from the full cleaned data)")
    A = df_all
    pk = A.groupby("peak_hour")["charging_demand"].mean()
    wkm = A.groupby("is_weekend")["charging_demand"].mean()
    tr = A.groupby("traffic_density")["charging_demand"].mean()
    lc = A.groupby("location_type")["charging_demand"].mean().sort_values()
    stt = A.groupby("state")["charging_demand"].mean().sort_values()
    corr = A.select_dtypes("number").corr()["charging_demand"].drop("charging_demand").drop(
        ["hour", "month"], errors="ignore").sort_values(key=abs, ascending=False)
    weak = corr[corr.abs() < 0.05].index.tolist()
    mx = A["charging_demand"].max()
    st.markdown(f"""
- **Data quality:** {qs['raw_rows']:,} raw rows → {qs['dupes']:,} duplicates removed → {qs['no_target']:,} rows without a target dropped → **{qs['clean_rows']:,} clean rows**, 0 missing values.
- **Peak hour:** average demand {pk[True]:.1f} vs {pk[False]:.1f} off-peak ({(pk[True]/pk[False]-1)*100:+.0f}%).
- **Strongest correlations with demand:** {", ".join(f"`{k}` ({v:.2f})" for k, v in corr.head(4).items())}.
- **Traffic density:** {" → ".join(f"{k} {tr[k]:.0f}" for k in TRAFFIC_ORDER if k in tr.index)}.
- **Weekend vs weekday:** {wkm.get(True, float('nan')):.1f} vs {wkm.get(False, float('nan')):.1f}.
- **Location type:** highest {lc.index[-1]} ({lc.iloc[-1]:.1f}), lowest {lc.index[0]} ({lc.iloc[0]:.1f}).
- **State:** highest {stt.index[-1]} ({stt.iloc[-1]:.1f}), lowest {stt.index[0]} ({stt.iloc[0]:.1f}).
- **Little/no linear relationship (|r|<0.05):** {", ".join(f"`{w}`" for w in weak) or "none"}.
- **Target range:** {A['charging_demand'].min():.0f} – {mx:.0f}; {(A['charging_demand'] >= mx).mean()*100:.1f}% of rows sit at the maximum.
""")
    st.caption("The written findings in the notebook cite different row counts (e.g. 98,440 clean rows); "
               "the numbers here are recomputed from the supplied CSV.")
    sec("Live check on your current filter selection")
    pk2 = df.groupby("peak_hour")["charging_demand"].mean()
    c = st.columns(3)
    if len(pk2) == 2:
        c[0].metric("Peak vs non-peak demand", f"{pk2[True]:.1f} vs {pk2[False]:.1f}",
                    f"{(pk2[True] / pk2[False] - 1) * 100:+.0f}%")
    c[1].metric("Corr(demand, station load)", f"{df.charging_demand.corr(df.station_load_percent):.2f}")
    c[2].metric("Share at max demand", f"{(df.charging_demand >= mx).mean() * 100:.1f}%")
