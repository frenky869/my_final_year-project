"""
app.py — Kenya Maize Price Predictor
─────────────────────────────────────
ALL values (prices, predictions, model metrics, feature importances,
forecasts, historical trends) come STRICTLY from the Colab notebook
artifacts saved to:
    /content/drive/MyDrive/MaizePrediction/dashboard/

No data is generated inside this file.
Files read:
    panel_clean.csv   — every cleaned weekly price + weather observation
    test_results.csv  — actuals vs predictions on the held-out test set
    forecast.csv      — week-by-week future predictions to 2026-06-16
    model.pkl         — trained best model (for on-demand prediction)
    label_encoder.pkl — LabelEncoder fitted on counties in Colab
    feature_cols.pkl  — exact feature list used during training
    metadata.json     — MAE, RMSE, MAPE, R², model name, date range
    model_name.txt    — name of the best model chosen by Colab
"""

import os, json, warnings
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import joblib

warnings.filterwarnings("ignore")

# ── optional folium ───────────────────────────────────────────────────────────
try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

# ─────────────────────────────────────────────────────────────────────────────
# PATHS — where the Colab notebook saves its artifacts
# ─────────────────────────────────────────────────────────────────────────────
DRIVE_DIR = "/content/drive/MyDrive/MaizePrediction/dashboard"
LOCAL_DIR = os.path.join(os.path.dirname(__file__), "dashboard")

NEEDED = [
    "panel_clean.csv", "test_results.csv", "forecast.csv",
    "model.pkl", "label_encoder.pkl", "feature_cols.pkl",
    "metadata.json", "model_name.txt",
]

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kenya Maize Price Predictor",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}

.main-header{
  background:linear-gradient(135deg,#14532d 0%,#166534 45%,#ca8a04 100%);
  padding:2rem 2.5rem;border-radius:16px;margin-bottom:2rem;color:white;
}
.main-header h1{font-family:'Playfair Display',serif;font-size:2.4rem;
  font-weight:700;margin:0 0 0.4rem 0;}
.main-header p{font-size:.95rem;opacity:.88;margin:0;font-weight:300;}
.county-pill{display:inline-block;background:rgba(255,255,255,.18);
  border-radius:20px;padding:.2rem .8rem;font-size:.78rem;font-weight:600;
  margin:.4rem .2rem 0 0;}

.kpi-card{background:white;border:1px solid #dcfce7;border-radius:14px;
  padding:1.1rem 1.4rem;text-align:center;
  box-shadow:0 2px 10px rgba(20,83,45,.07);}
.kpi-card .kpi-label{font-size:.7rem;text-transform:uppercase;
  letter-spacing:1.2px;color:#6b7280;font-weight:600;}
.kpi-card .kpi-value{font-size:1.75rem;font-weight:700;color:#14532d;line-height:1.2;}
.kpi-card .kpi-sub{font-size:.75rem;color:#9ca3af;margin-top:.2rem;}

.predict-box{background:linear-gradient(135deg,#14532d,#166534);
  color:white;border-radius:16px;padding:1.8rem 2rem;
  text-align:center;margin:1rem 0;}
.predict-box .big-price{font-family:'Playfair Display',serif;
  font-size:3.2rem;font-weight:700;line-height:1;}
.predict-box .per-kg{font-size:.95rem;opacity:.82;margin-top:.35rem;}

.range-box{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;
  padding:.9rem 1.2rem;margin-top:.6rem;}

.county-rank-card{background:white;border-radius:10px;padding:.85rem 1rem;
  border-left:4px solid #16a34a;margin-bottom:.6rem;
  display:flex;justify-content:space-between;align-items:center;
  box-shadow:0 1px 4px rgba(0,0,0,.05);}

.insight-box{background:#f0fdf4;border-left:4px solid #16a34a;
  border-radius:0 10px 10px 0;padding:1rem 1.3rem;
  font-size:.85rem;color:#374151;line-height:1.75;}

.section-head{font-size:1.1rem;font-weight:600;color:#14532d;
  margin:1.4rem 0 .7rem 0;}

.stButton>button{
  background:linear-gradient(135deg,#14532d,#166534);
  color:white;border:none;border-radius:10px;padding:.7rem 1rem;
  font-weight:600;font-size:1rem;width:100%;}
.stButton>button:hover{box-shadow:0 4px 14px rgba(20,83,45,.35);}

div[data-testid="stSidebar"]{background:#0C3B2E;}
div[data-testid="stSidebar"] *{color:#E8F5E9 !important;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# COUNTY GEO INFO  (lat/lon/role only — NO prices generated here)
# ─────────────────────────────────────────────────────────────────────────────
COUNTY_GEO = {
    "Nairobi":     {"lat":-1.2921, "lon":36.8219, "role":"Urban Consumer",   "color":"#dc2626"},
    "Mombasa":     {"lat":-4.0435, "lon":39.6682, "role":"Coastal Consumer", "color":"#ea580c"},
    "Kiambu":      {"lat":-1.0312, "lon":36.8474, "role":"Peri-Urban",       "color":"#ca8a04"},
    "Kirinyaga":   {"lat":-0.5577, "lon":37.3479, "role":"Producer",         "color":"#16a34a"},
    "Uasin-Gishu": {"lat": 0.5203, "lon":35.2699, "role":"Grain Basket",     "color":"#15803d"},
}

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]

# ─────────────────────────────────────────────────────────────────────────────
# LOAD ARTIFACTS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_artifacts():
    """
    Load every file written by the Colab notebook's export cell.
    Checks Drive path first, then a local ./dashboard/ folder.
    Returns None if files are missing.
    """
    chosen = None
    for d in [DRIVE_DIR, LOCAL_DIR]:
        if all(os.path.exists(os.path.join(d, f)) for f in NEEDED):
            chosen = d
            break
    if chosen is None:
        return None

    p = lambda f: os.path.join(chosen, f)

    panel_clean  = pd.read_csv(p("panel_clean.csv"),  parse_dates=["week_start"])
    test_results = pd.read_csv(p("test_results.csv"), parse_dates=["week_start"])
    forecast_df  = pd.read_csv(p("forecast.csv"),     parse_dates=["week_start"])
    model        = joblib.load(p("model.pkl"))
    le           = joblib.load(p("label_encoder.pkl"))
    feat_cols    = joblib.load(p("feature_cols.pkl"))
    with open(p("metadata.json"))  as f: meta       = json.load(f)
    with open(p("model_name.txt")) as f: model_name = f.read().strip()

    return dict(
        panel_clean  = panel_clean,
        test_results = test_results,
        forecast_df  = forecast_df,
        model        = model,
        le           = le,
        feat_cols    = feat_cols,
        meta         = meta,
        model_name   = model_name,
        source_dir   = chosen,
    )

# ─────────────────────────────────────────────────────────────────────────────
# ON-DEMAND PREDICTION using the Colab-trained model
# ─────────────────────────────────────────────────────────────────────────────
def predict_one(model, le, feat_cols, panel_clean,
                county, year, month, rain_mm):
    """
    Build one feature row using the SAME feature names/order as Colab training.
    Uses panel_clean to derive rolling/lag values from real historical data.
    Falls back gracefully if a feature is not constructible.
    """
    # Build a row with all features the model expects, defaulting to 0
    row = {col: 0.0 for col in feat_cols}

    # --- time features (same as notebook) ---
    row["month"]     = month
    row["year"]      = year
    row["month_sin"] = np.sin(2 * np.pi * month / 12)
    row["month_cos"] = np.cos(2 * np.pi * month / 12)
    iso_week         = pd.Timestamp(year=year, month=month, day=14).isocalendar().week
    row["week"]      = iso_week
    row["week_sin"]  = np.sin(2 * np.pi * iso_week / 52)
    row["week_cos"]  = np.cos(2 * np.pi * iso_week / 52)

    # --- county encoded (same LabelEncoder fitted in Colab) ---
    if "county_encoded" in row:
        try:
            row["county_encoded"] = int(le.transform([county])[0])
        except Exception:
            row["county_encoded"] = 0

    # --- weather features: use county historical mean from panel_clean ---
    county_hist = panel_clean[panel_clean["county"] == county]
    for wcol in ["temp_avg_c","temp_max_c","temp_min_c","rain_mm",
                 "temp_range","heavy_rain","heat_stress","strong_wind"]:
        if wcol in row and wcol in county_hist.columns:
            row[wcol] = float(county_hist[wcol].mean())

    # Override rain_mm with user slider value
    if "rain_mm" in row:
        row["rain_mm"] = float(rain_mm)

    # --- lag & rolling: use last known values from panel_clean for this county ---
    last_prices = (
        county_hist.sort_values("week_start")["agri_price"].dropna().values
    )
    if len(last_prices) > 0:
        for lag, col in [(1,"price_lag_1"),(2,"price_lag_2"),
                         (3,"price_lag_3"),(4,"price_lag_4"),(8,"price_lag_8")]:
            if col in row:
                idx = -lag if lag <= len(last_prices) else -len(last_prices)
                row[col] = float(last_prices[idx])

        for w, col in [(4,"price_rolling_mean_4"),(8,"price_rolling_mean_8"),
                       (12,"price_rolling_mean_12")]:
            if col in row:
                row[col] = float(np.mean(last_prices[-w:]))
        for w, col in [(4,"price_rolling_std_4"),(8,"price_rolling_std_8"),
                       (12,"price_rolling_std_12")]:
            if col in row:
                row[col] = float(np.std(last_prices[-w:])) if len(last_prices) >= 2 else 0.0

    X = pd.DataFrame([row])[feat_cols]
    return float(model.predict(X)[0])

# ─────────────────────────────────────────────────────────────────────────────
# MAP BUILDER  (uses only notebook-derived prices)
# ─────────────────────────────────────────────────────────────────────────────
def build_map(county_prices, selected=None):
    center_lat = np.mean([COUNTY_GEO[c]["lat"] for c in county_prices if c in COUNTY_GEO])
    center_lon = np.mean([COUNTY_GEO[c]["lon"] for c in county_prices if c in COUNTY_GEO])
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6,
                   tiles="CartoDB positron")

    prices = list(county_prices.values())
    mn, mx = min(prices), max(prices)

    for county, price in county_prices.items():
        if county not in COUNTY_GEO:
            continue
        info = COUNTY_GEO[county]
        norm = (price - mn) / (mx - mn + 1)
        r    = int(20  + norm * 200)
        g    = int(120 - norm * 80)
        b    = int(50  - norm * 40)
        fill   = f"#{r:02x}{g:02x}{b:02x}"
        border = "#fbbf24" if county == selected else info["color"]
        bw     = 4 if county == selected else 2
        radius = 22 + norm * 22

        popup_html = f"""
        <div style="font-family:Inter,sans-serif;min-width:200px;padding:4px">
          <div style="font-size:15px;font-weight:700;color:#14532d">🌽 {county}</div>
          <div style="color:#6b7280;font-size:11px;margin-bottom:6px">{info['role']}</div>
          <hr style="margin:4px 0;border-color:#dcfce7">
          <div style="font-size:22px;font-weight:700;color:#14532d">
            KES {price:,.1f}/kg
          </div>
          <div style="color:#9ca3af;font-size:12px">wholesale (agri_price)</div>
        </div>"""

        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=radius, color=border, weight=bw,
            fill=True, fill_color=fill, fill_opacity=0.72,
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=folium.Tooltip(f"<b>{county}</b><br>KES {price:,.1f}/kg")
        ).add_to(m)

        folium.Marker(
            location=[info["lat"], info["lon"]],
            icon=folium.DivIcon(
                html=f"""<div style="
                    font-family:Inter,sans-serif;background:white;
                    border:2px solid {border};border-radius:8px;
                    padding:3px 8px;font-size:10px;font-weight:700;
                    color:#14532d;white-space:nowrap;
                    transform:translate(-50%,-120%);
                    box-shadow:0 2px 6px rgba(0,0,0,.12);">
                  {county.split()[0]}<br>KES {price:,.1f}
                </div>""",
                icon_size=(130, 42), icon_anchor=(65, 42)
            )
        ).add_to(m)

    legend = """
    <div style="position:fixed;bottom:28px;left:28px;z-index:999;
         background:white;padding:14px 18px;border-radius:12px;
         box-shadow:0 2px 12px rgba(0,0,0,.12);font-family:Inter,sans-serif;">
      <b style="color:#14532d;font-size:12px">Price per kg (KES)</b><br>
      <div style="display:flex;align-items:center;gap:8px;margin-top:7px;">
        <div style="width:70px;height:10px;border-radius:5px;
             background:linear-gradient(to right,#148032,#c47a00,#c81414);">
        </div>
      </div>
      <div style="display:flex;justify-content:space-between;
           font-size:10px;color:#9ca3af;width:70px;margin-top:2px;">
        <span>Cheaper</span><span>Pricier</span>
      </div>
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))
    return m

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌽 Maize Price\nPredictor")
    st.markdown("---")
    st.markdown(
        "All data loaded from the **Colab notebook** export.\n\n"
        "**Drive path:**\n`MaizePrediction/dashboard/`"
    )
    st.markdown("---")
    st.caption(
        "Run the notebook → execute the **export cell** "
        "at the bottom → reload this page."
    )

# ── Load ──────────────────────────────────────────────────────────────────────
art = load_artifacts()

if art is None:
    st.error(
        "❌ **Notebook artifacts not found.**\n\n"
        "Expected path: `" + DRIVE_DIR + "`\n\n"
        "**Steps to fix:**\n"
        "1. Open the Colab notebook\n"
        "2. Run **all cells** (Runtime → Run all)\n"
        "3. Run the **export cell** at the bottom — it saves 8 files to Drive\n"
        "4. Sync Google Drive and reload this page"
    )
    st.info(
        "Files needed: `model.pkl · label_encoder.pkl · feature_cols.pkl · "
        "model_name.txt · panel_clean.csv · test_results.csv · "
        "forecast.csv · metadata.json`"
    )
    st.stop()

# Unpack artifacts
panel_clean  = art["panel_clean"]
test_results = art["test_results"]
forecast_df  = art["forecast_df"]
model        = art["model"]
le           = art["le"]
feat_cols    = art["feat_cols"]
meta         = art["meta"]
model_name   = art["model_name"]

TARGET_COUNTIES = sorted(panel_clean["county"].unique().tolist())

st.sidebar.success(f"✅ Artifacts loaded from:\n`{art['source_dir']}`")
st.sidebar.markdown(f"**Model:** {model_name}")
st.sidebar.markdown(f"**Trained:** {meta['trained_on']}")

# ── Header ────────────────────────────────────────────────────────────────────
pills = "".join(
    f'<span class="county-pill">📍 {c}</span>' for c in TARGET_COUNTIES
)
st.markdown(f"""
<div class="main-header">
  <h1>🌽 Kenya Maize Price Predictor</h1>
  <p>Predictions powered by your Colab-trained {model_name} model · {meta['date_range']}</p>
  <div style="margin-top:.8rem">{pills}</div>
</div>
""", unsafe_allow_html=True)

# ── KPI Strip — from metadata.json written by Colab ──────────────────────────
k1, k2, k3, k4 = st.columns(4)
mae_raw  = meta["metrics"]["MAE"].replace("KES ","").replace("KSh ","").strip()
rmse_raw = meta["metrics"]["RMSE"].replace("KES ","").replace("KSh ","").strip()

with k1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Best Model</div>
        <div class="kpi-value" style="font-size:1rem;padding-top:4px">{model_name}</div>
        <div class="kpi-sub">Selected by lowest Test MAE</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">R² Score</div>
        <div class="kpi-value">{meta['metrics']['R2']}</div>
        <div class="kpi-sub">Test set (held-out)</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">MAE</div>
        <div class="kpi-value">KES {mae_raw}</div>
        <div class="kpi-sub">Mean Absolute Error</div>
    </div>""", unsafe_allow_html=True)
with k4:
    avg_p = panel_clean["agri_price"].mean()
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Historical Avg Price</div>
        <div class="kpi-value">KES {avg_p:.2f}</div>
        <div class="kpi-sub">{meta['date_range']}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Main layout ───────────────────────────────────────────────────────────────
left, right = st.columns([1, 1.85], gap="large")

# ══════════════════════════════════════
#  LEFT — Prediction Form
#  Uses: model.pkl + label_encoder.pkl
#        + feature_cols.pkl from Colab
# ══════════════════════════════════════
with left:
    st.markdown('<div class="section-head">🎯 Predict Price (Colab model)</div>',
                unsafe_allow_html=True)

    county = st.selectbox("County", TARGET_COUNTIES)
    cy, cm = st.columns(2)
    with cy:
        year  = st.selectbox("Year",  [2025, 2026, 2027])
    with cm:
        month = st.selectbox("Month", range(1, 13),
                             format_func=lambda x: MONTH_NAMES[x-1])

    # Rainfall slider — range derived from actual panel data
    rain_min = float(panel_clean["rain_mm"].min()) if "rain_mm" in panel_clean.columns else 0.0
    rain_max = float(panel_clean["rain_mm"].max()) if "rain_mm" in panel_clean.columns else 200.0
    rain_med = float(panel_clean["rain_mm"].median()) if "rain_mm" in panel_clean.columns else 20.0
    rainfall = st.slider(
        "Rainfall (mm) — from notebook weather data",
        float(rain_min), float(rain_max), float(rain_med), 1.0
    )

    # MAE as float for confidence interval
    try:
        mae_f = float(mae_raw.replace(",",""))
    except Exception:
        mae_f = float(test_results["abs_error"].mean()) if "abs_error" in test_results.columns else 0.0

    if st.button("🌽  Predict with Colab Model"):
        price = predict_one(model, le, feat_cols, panel_clean,
                            county, year, month, rainfall)

        st.markdown(f"""
        <div class="predict-box">
          <div style="font-size:.85rem;opacity:.78;margin-bottom:.5rem">
            {county} &nbsp;·&nbsp; {MONTH_NAMES[month-1]} {year}
          </div>
          <div class="big-price">KES {price:,.2f}</div>
          <div class="per-kg">wholesale price per kg (agri_price target)</div>
        </div>
        <div class="range-box">
          <div style="font-size:.72rem;color:#6b7280;font-weight:600;
               text-transform:uppercase;letter-spacing:1px;margin-bottom:.4rem">
            Confidence Range (±MAE from Colab test set)
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
              <div style="font-weight:700;color:#14532d;font-size:1.05rem">
                KES {price - mae_f:,.2f}
              </div>
              <div style="font-size:.72rem;color:#9ca3af">Lower bound</div>
            </div>
            <div style="color:#d1d5db;font-size:1.3rem">↔</div>
            <div style="text-align:right">
              <div style="font-weight:700;color:#14532d;font-size:1.05rem">
                KES {price + mae_f:,.2f}
              </div>
              <div style="font-size:.72rem;color:#9ca3af">Upper bound</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Show the last known actual price for context
        last_actual = (
            panel_clean[panel_clean["county"]==county]
            .sort_values("week_start")["agri_price"]
            .dropna().iloc[-1]
            if len(panel_clean[panel_clean["county"]==county]) > 0
            else None
        )
        if last_actual:
            last_date = (
                panel_clean[panel_clean["county"]==county]
                .sort_values("week_start")["week_start"]
                .iloc[-1].strftime("%Y-%m-%d")
            )
            delta = price - last_actual
            direction = "▲" if delta > 0 else "▼"
            st.markdown(
                f"Last known actual price ({last_date}): **KES {last_actual:.2f}**  \n"
                f"Predicted change: {direction} KES {abs(delta):.2f}"
            )

    # ── Model metrics from metadata.json ──────────────────────────────────────
    st.markdown('<div class="section-head">📊 Colab Model Metrics</div>',
                unsafe_allow_html=True)
    metrics_df = pd.DataFrame([{
        "Metric": "MAE",  "Value": meta["metrics"]["MAE"]
    },{
        "Metric": "RMSE", "Value": meta["metrics"]["RMSE"]
    },{
        "Metric": "MAPE", "Value": meta["metrics"]["MAPE"]
    },{
        "Metric": "R²",   "Value": meta["metrics"]["R2"]
    }])
    st.dataframe(metrics_df.set_index("Metric"), use_container_width=True)

    # ── County avg prices from panel_clean.csv ────────────────────────────────
    st.markdown('<div class="section-head">🏘️ County Average Prices (Actual Data)</div>',
                unsafe_allow_html=True)
    county_avgs = (
        panel_clean.groupby("county")["agri_price"]
        .mean().round(2).sort_values(ascending=False)
    )
    for c, avg in county_avgs.items():
        color = COUNTY_GEO.get(c, {}).get("color", "#16a34a")
        role  = COUNTY_GEO.get(c, {}).get("role",  "")
        st.markdown(f"""
        <div style="background:white;border-radius:10px;padding:.7rem 1rem;
             border-left:4px solid {color};margin-bottom:.5rem;
             box-shadow:0 1px 4px rgba(0,0,0,.05);font-size:.85rem;">
          <b style="color:#14532d">{c}</b>
          <span style="color:#6b7280;margin-left:6px">{role}</span>
          <span style="float:right;font-weight:700;color:#14532d">
            KES {avg:.2f}/kg
          </span>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════
#  RIGHT — Tabs
# ══════════════════════════════════════
with right:
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Price Map",
        "📈 Historical Trends",
        "🔮 Forecast",
        "📉 Model Analysis",
    ])

    # ── Tab 1: Map — prices from forecast.csv or panel_clean.csv ─────────────
    with tab1:
        st.markdown('<div class="section-head">County Price Map — Notebook Data</div>',
                    unsafe_allow_html=True)

        if not HAS_FOLIUM:
            st.warning(
                "Install folium: `pip install folium streamlit-folium`  \n"
                "Showing price table instead."
            )

        mc1, mc2 = st.columns(2)
        with mc1:
            map_source = st.radio(
                "Price source",
                ["Latest actual (panel_clean.csv)",
                 "Forecast (forecast.csv)"],
                horizontal=False, key="mapsrc"
            )
        with mc2:
            if "Forecast" in map_source and not forecast_df.empty:
                avail_dates = sorted(forecast_df["week_start"].dt.date.unique())
                chosen_date = st.selectbox(
                    "Forecast week", avail_dates,
                    index=min(4, len(avail_dates)-1), key="fdate"
                )
            else:
                chosen_date = None

        # Build county → price dict STRICTLY from notebook files
        county_prices = {}
        if "Forecast" in map_source and not forecast_df.empty and chosen_date:
            sub = forecast_df[forecast_df["week_start"].dt.date == chosen_date]
            for _, row in sub.iterrows():
                if row["county"] in TARGET_COUNTIES:
                    county_prices[row["county"]] = row["predicted_price"]
        else:
            # Latest actual agri_price per county from panel_clean
            latest = (
                panel_clean.sort_values("week_start")
                .groupby("county")["agri_price"].last()
            )
            for c, p in latest.items():
                if c in TARGET_COUNTIES:
                    county_prices[c] = p

        if county_prices:
            if HAS_FOLIUM:
                folium_map = build_map(county_prices)
                st_folium(folium_map, height=430, use_container_width=True)
            else:
                # Fallback bar chart
                fig_map = px.bar(
                    x=list(county_prices.keys()),
                    y=list(county_prices.values()),
                    labels={"x":"County","y":"Price (KES/kg)"},
                    color=list(county_prices.values()),
                    color_continuous_scale=["#148032","#c47a00","#c81414"],
                    title="Price by County"
                )
                fig_map.update_layout(coloraxis_showscale=False,
                                      plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig_map, use_container_width=True)

            # Price ranking
            st.markdown('<div class="section-head">Price Ranking</div>',
                        unsafe_allow_html=True)
            sorted_c = sorted(county_prices.items(), key=lambda x: x[1])
            rank_emoji = ["🥇","🥈","🥉","4️⃣","5️⃣"]
            cheapest   = sorted_c[0][1]
            for i, (c, p) in enumerate(sorted_c):
                diff     = p - cheapest
                diff_str = f"+KES {diff:,.2f}" if diff > 0 else "Cheapest"
                color    = COUNTY_GEO.get(c, {}).get("color","#16a34a")
                role     = COUNTY_GEO.get(c, {}).get("role","")
                st.markdown(f"""
                <div class="county-rank-card"
                     style="border-left-color:{color}">
                  <div>
                    <span style="font-size:1.1rem">{rank_emoji[i]}</span>
                    <b style="color:#14532d;margin-left:6px">{c}</b>
                    <span style="color:#9ca3af;font-size:.75rem;
                         margin-left:6px">{role}</span>
                  </div>
                  <div style="text-align:right">
                    <div style="font-weight:700;color:#14532d;font-size:1.1rem">
                      KES {p:,.2f}
                    </div>
                    <div style="font-size:.72rem;color:#9ca3af">{diff_str}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No price data for the selected combination.")

    # ── Tab 2: Historical Trends — from panel_clean.csv ───────────────────────
    with tab2:
        st.markdown(
            '<div class="section-head">Historical Prices — panel_clean.csv</div>',
            unsafe_allow_html=True
        )

        view_mode = st.radio("View", ["All Counties","Single County"],
                             horizontal=True, key="vmode")

        if view_mode == "Single County":
            sel_c = st.selectbox("County", TARGET_COUNTIES, key="sc")
            hist  = panel_clean[panel_clean["county"]==sel_c].sort_values("week_start")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist["week_start"], y=hist["agri_price"],
                mode="lines", name="AgriBORA (actual)",
                line=dict(color=COUNTY_GEO.get(sel_c,{}).get("color","#16a34a"),
                          width=2),
                fill="tozeroy", fillcolor="rgba(20,83,45,0.07)"
            ))
            # Overlay KAMIS if present
            if "kamis_price" in hist.columns:
                fig.add_trace(go.Scatter(
                    x=hist["week_start"], y=hist["kamis_price"],
                    mode="lines", name="KAMIS",
                    line=dict(color="#ca8a04", width=1.5, dash="dot")
                ))
        else:
            fig = go.Figure()
            for c in TARGET_COUNTIES:
                h = panel_clean[panel_clean["county"]==c].sort_values("week_start")
                fig.add_trace(go.Scatter(
                    x=h["week_start"], y=h["agri_price"],
                    mode="lines", name=c,
                    line=dict(
                        color=COUNTY_GEO.get(c,{}).get("color","#888"),
                        width=1.8
                    )
                ))

        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", size=12),
            xaxis=dict(showgrid=True, gridcolor="#f3f4f6", title="Week"),
            yaxis=dict(showgrid=True, gridcolor="#f3f4f6",
                       title="Price (KES/kg) — agri_price"),
            legend=dict(orientation="h", yanchor="bottom", y=1.01),
            margin=dict(l=10,r=10,t=30,b=10), height=370
        )
        st.plotly_chart(fig, use_container_width=True)

        # Monthly seasonal pattern from real data
        st.markdown(
            '<div class="section-head">Seasonal Pattern (actual data)</div>',
            unsafe_allow_html=True
        )
        panel_clean["_month"] = panel_clean["week_start"].dt.month
        seasonal = (
            panel_clean.groupby(["county","_month"])["agri_price"]
            .mean().reset_index()
        )
        seasonal["Month"] = seasonal["_month"].apply(lambda x: MONTH_NAMES[x-1])

        fig2 = px.line(
            seasonal, x="Month", y="agri_price",
            color="county",
            color_discrete_map={
                c: COUNTY_GEO.get(c,{}).get("color","#888")
                for c in TARGET_COUNTIES
            },
            markers=True,
            labels={"agri_price":"Avg Price (KES/kg)","county":"County"}
        )
        fig2.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter"),
            margin=dict(l=10,r=10,t=10,b=10), height=300
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 3: Forecast — strictly from forecast.csv ──────────────────────────
    with tab3:
        st.markdown(
            '<div class="section-head">Price Forecast — forecast.csv from Colab</div>',
            unsafe_allow_html=True
        )

        if forecast_df.empty:
            st.warning(
                "forecast.csv is empty. Re-run the notebook's forecasting "
                "section and the export cell."
            )
        else:
            fc_counties = st.multiselect(
                "Counties", TARGET_COUNTIES, default=TARGET_COUNTIES, key="fcc"
            )

            fig3 = go.Figure()
            for c in fc_counties:
                # Historical tail (last 26 weeks) from panel_clean
                hist_tail = (
                    panel_clean[panel_clean["county"]==c]
                    .sort_values("week_start").tail(26)
                )
                fig3.add_trace(go.Scatter(
                    x=hist_tail["week_start"],
                    y=hist_tail["agri_price"],
                    mode="lines", name=f"{c} (actual)",
                    line=dict(
                        color=COUNTY_GEO.get(c,{}).get("color","#888"),
                        width=2
                    )
                ))
                # Forecast line
                fc_c = forecast_df[forecast_df["county"]==c].sort_values("week_start")
                fig3.add_trace(go.Scatter(
                    x=fc_c["week_start"],
                    y=fc_c["predicted_price"],
                    mode="lines+markers", name=f"{c} (forecast)",
                    line=dict(
                        color=COUNTY_GEO.get(c,{}).get("color","#888"),
                        width=2, dash="dash"
                    ),
                    marker=dict(size=4)
                ))

            fig3.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Inter"),
                xaxis=dict(showgrid=True, gridcolor="#f3f4f6", title="Week"),
                yaxis=dict(showgrid=True, gridcolor="#f3f4f6",
                           title="Price (KES/kg) — predicted_price"),
                legend=dict(orientation="h", yanchor="bottom", y=1.01),
                margin=dict(l=10,r=10,t=30,b=10), height=380
            )
            st.plotly_chart(fig3, use_container_width=True)

            # Latest forecast per county
            st.markdown(
                '<div class="section-head">Latest Forecast Price per County</div>',
                unsafe_allow_html=True
            )
            latest_fc = (
                forecast_df.sort_values("week_start")
                .groupby("county")["predicted_price"].last()
                .reset_index()
                .sort_values("predicted_price", ascending=False)
            )
            st.dataframe(
                latest_fc.rename(columns={
                    "county":"County",
                    "predicted_price":"Predicted Price (KES/kg)"
                }).set_index("County").round(2),
                use_container_width=True
            )

            csv = forecast_df.to_csv(index=False).encode()
            st.download_button(
                "⬇️ Download full forecast CSV",
                csv, "maize_forecast.csv", "text/csv"
            )

    # ── Tab 4: Model Analysis — from test_results.csv + model.pkl ────────────
    with tab4:
        st.markdown(
            '<div class="section-head">Actual vs Predicted — test_results.csv</div>',
            unsafe_allow_html=True
        )

        if test_results.empty:
            st.warning("test_results.csv is empty.")
        else:
            # Scatter: actual vs predicted
            ap = test_results.dropna(subset=["agri_price","prediction"])
            fig4 = px.scatter(
                ap, x="agri_price", y="prediction",
                color="county",
                color_discrete_map={
                    c: COUNTY_GEO.get(c,{}).get("color","#888")
                    for c in TARGET_COUNTIES
                },
                trendline="ols",
                labels={
                    "agri_price":"Actual Price (KES/kg)",
                    "prediction":"Predicted Price (KES/kg)",
                    "county":"County"
                },
                title=f"Actual vs Predicted — {model_name}"
            )
            fig4.update_traces(
                marker=dict(size=6, opacity=0.55),
                selector=dict(mode="markers")
            )
            fig4.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Inter"),
                margin=dict(l=10,r=10,t=40,b=10), height=360
            )
            st.plotly_chart(fig4, use_container_width=True)

            # Per-county error stats from test_results
            st.markdown(
                '<div class="section-head">Per-County Error (test set)</div>',
                unsafe_allow_html=True
            )
            if "abs_error" in test_results.columns:
                err = test_results.groupby("county").agg(
                    MAE=("abs_error","mean"),
                    Max_Error=("abs_error","max"),
                    N_Weeks=("abs_error","count")
                ).round(3)
                if "pct_error" in test_results.columns:
                    err["MAPE_%"] = (
                        test_results.groupby("county")["pct_error"].mean().round(2)
                    )
                st.dataframe(err, use_container_width=True)

        # Feature importance from model.pkl
        st.markdown(
            '<div class="section-head">Feature Importance — model.pkl</div>',
            unsafe_allow_html=True
        )
        if model is not None and hasattr(model, "feature_importances_") and feat_cols:
            fi_df = (
                pd.DataFrame({
                    "Feature":    feat_cols,
                    "Importance": model.feature_importances_
                })
                .sort_values("Importance", ascending=True)
            )
            fig5 = px.bar(
                fi_df, x="Importance", y="Feature",
                orientation="h",
                color="Importance",
                color_continuous_scale=["#dcfce7","#14532d"],
                title=f"Feature Importance — {model_name}"
            )
            fig5.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                coloraxis_showscale=False,
                margin=dict(l=10,r=10,t=40,b=10), height=350,
                font=dict(family="Inter")
            )
            st.plotly_chart(fig5, use_container_width=True)

            # Insight box — top 3 features from real importances
            top3 = fi_df.sort_values("Importance",ascending=False).head(3)
            top3_lines = "  \n".join(
                f"🔹 **{row['Feature']}** — importance {row['Importance']:.4f}"
                for _, row in top3.iterrows()
            )
            st.markdown(
                f"""<div class="insight-box">
                <b>Top 3 price drivers (from Colab model)</b><br>
                {top3_lines.replace(chr(10),"<br>")}
                </div>""",
                unsafe_allow_html=True
            )
        elif model is not None and hasattr(model, "coef_") and feat_cols:
            coef_df = (
                pd.DataFrame({
                    "Feature":     feat_cols,
                    "Coefficient": np.abs(model.coef_)
                })
                .sort_values("Coefficient", ascending=True)
            )
            fig5 = px.bar(
                coef_df, x="Coefficient", y="Feature",
                orientation="h", color="Coefficient",
                color_continuous_scale=["#dcfce7","#14532d"],
                title=f"Coefficient Magnitudes — {model_name}"
            )
            fig5.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                coloraxis_showscale=False,
                margin=dict(l=10,r=10,t=40,b=10), height=350,
                font=dict(family="Inter")
            )
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info(
                "Feature importance is available for tree-based models "
                "(Random Forest, XGBoost, LightGBM, Gradient Boosting)."
            )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="text-align:center;color:#9ca3af;font-size:.78rem;padding:.8rem 0">
  🌽 Kenya Maize Price Predictor &nbsp;·&nbsp;
  Model: <b>{model_name}</b> &nbsp;·&nbsp;
  Data: {meta['date_range']} &nbsp;·&nbsp;
  All values from Colab notebook artifacts<br>
  <span style="color:#14532d;font-weight:600">
    {" &nbsp;·&nbsp; ".join(TARGET_COUNTIES)}
  </span>
</div>
""", unsafe_allow_html=True)
