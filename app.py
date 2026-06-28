import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import base64
import time
# =========================
# PAGE SETUP
# =========================

st.set_page_config(
    page_title="EXOPLANET DETECTOR",
    layout="wide"
)

# =========================
# SESSION STATE
# =========================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "started" not in st.session_state:
    st.session_state.started = False

# =========================
# BACKGROUND
# =========================

def get_base64(image_file):
    with open(image_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

home_bg = get_base64("space_background.jpg")
analysis_bg = get_base64("analysis_background.jpg")

# =========================
# CSS
# =========================



if st.session_state.page == "home":
    current_bg = home_bg
else:
    current_bg = analysis_bg

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;800&family=Audiowide&display=swap');
.stApp {{
background-image:url("data:image/jpg;base64,{current_bg}");
background-size:120% 120%;
background-position:center;
background-attachment:fixed;
color:white;
animation:spaceMove 25s infinite alternate ease-in-out;
}}

@keyframes spaceMove {{
0% {{ background-position:0% 0%; }}
100% {{ background-position:100% 100%; }}
}}
@keyframes starMove {{
    from {{
        transform: translateY(0px);
    }}
    to {{
        transform: translateY(-800px);
    }}
}}

[data-testid="stMetricValue"] {{
    font-family: 'Exo 2', sans-serif !important;
    font-size: 30px !important;
    font-weight: 630 !important;
    color: #F8FAFF !important;
    padding-bottom: 3px;
}}

[data-testid="stMetricLabel"] p {{
    font-family: 'Orbitron', sans-serif !important;
    font-size: 17px !important;
    font-weight: 580 !important;
    color: #F8FAFF !important;
    border-bottom: 2px solid rgba(125,249,255,0.9);
    box-shadow: 0 3px 10px rgba(125,249,255,0.5);
    padding-bottom: 3px;
}}
h1 {{
font-family:'Orbitron', sans-serif !important;
font-size:42px !important;
font-weight:800 !important;
text-align:center !important;
color:#F8FAFF !important;
margin-top:-40px !important;
margin-bottom:50px !important;
letter-spacing:3px;
}}
.hero {{
    position: absolute;
    top: 110px;
    left: 40px;
    max-width: 650px;

    background: rgba(0,0,0,0.55);
    backdrop-filter: blur(10px);
    padding: 35px;
    border-radius: 25px;
    border: 1px solid rgba(255,255,255,0.12);
}}
div[data-testid="stHeading"]
 h2 {{
    font-family: 'Exo 2', sans-serif !important;
    font-size: 34px !important;
    font-weight: 700 !important;

    background: linear-gradient(
        90deg,
        #7DF9FF,
        #B388FF,
        #FFFFFF
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;

    text-shadow: 0 0 15px rgba(125,249,255,0.3);
}}
.planet-name {{
    font-family: 'Orbitron', sans-serif;
    font-size: 40px;
    font-weight: 700;
    color: #F8FAFF;
    margin-top: 9px;
    margin-bottom: 25px;
    text-shadow:
        0 0 8px rgba(0,0,0,0.9),
        0 0 20px rgba(10,20,40,0.8);
}}
div[data-testid="stMetric"] {{
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);

    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px;

    padding: 20px;
    margin: 10px;

    box-shadow:
        0 8px 32px rgba(0,0,0,0.35);

    transition: all 0.3s ease;
}}
div[data-testid="stMetric"] > div {{

    display: flex !important;

    flex-direction: column !important;

    align-items: center !important;

    justify-content: center !important;

    text-align: center !important;

}}


div[data-testid="stMetricLabel"] {{

    width: 100% !important;

    display: flex !important;

    justify-content: center !important;

    align-items: center !important;

    text-align: center !important;

}}


div[data-testid="stMetricLabel"] p {{

    text-align: center !important;

    width: 100% !important;

}}


div[data-testid="stMetricValue"] {{

    width: 100% !important;

    text-align: center !important;

}}
.stButton button {{
    background: linear-gradient(90deg, #0F2027, #203A43);
    color: white;
    border: none;
    border-radius: 50px;
    padding: 18px 60px;
    font-size: 24px;
    font-weight: 700;
    box-shadow:
        0 0 6px rgba(0,255,255,0.25);
    transition: all 0.3s ease;
}}

.stButton button:hover {{
    transform: scale(1.04);
    box-shadow:
        0 0 10px rgba(0,255,255,0.5),
        0 0 20px rgba(0,255,255,0.3);
}}
div.stButton {{
    margin-top: 350px;
    text-align: center;
    
}}
/* FILE UPLOADER CSS */
[data-testid="stFileUploaderDropzone"] {{
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
}}

[data-testid="stFileUploader"] {{
    width: fit-content !important;
}}
.stApp::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.30);
    z-index: -2;
    pointer-events: none;
}}
.stApp::after {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;

    background:
        radial-gradient(2px 2px at 20% 30%, white, transparent),
        radial-gradient(2px 2px at 70% 50%, #7DF9FF, transparent),
        radial-gradient(1px 1px at 40% 80%, white, transparent),
        radial-gradient(2px 2px at 90% 20%, #B388FF, transparent),
        radial-gradient(2px 2px at 10% 70%, white, transparent),
        radial-gradient(1px 1px at 80% 90%, #7DF9FF, transparent);

    background-size: 400px 400px;

    animation: starMove 80s linear infinite;

    z-index: -1;
    pointer-events: none;
}}
/* =========================
   MOBILE RESPONSIVE DESIGN
========================= */

@media (max-width: 768px) {{

h1 {{

    font-size: 38px !important;

    line-height: 1.1;

    margin-top: 20px !important;

    margin-bottom: 30px !important;

}}


.hero {{

    position: relative;

    top: 40px;

    left: 15px;

    right:15px;

    max-width:90%;

    padding:25px;

}}


div[data-testid="stHeading"] h2 {{

    font-size:28px !important;

}}


.hero p {{

    font-size:18px;

}}


.stButton button {{

    padding:15px 40px;

    font-size:18px;

}}


div.stButton {{

    margin-top:120px;

}}

}}
</style>
""", unsafe_allow_html=True)

# =========================
# UNIVERSAL COLUMN DETECTION
# =========================

def detect_time_flux(df):
    df.columns = [str(c).strip().lower() for c in df.columns]

    time_col = None
    flux_col = None

    for col in df.columns:
        if "time" in col:
            time_col = col
        if "flux" in col or "pdcsap" in col or "sap" in col:
            flux_col = col

    if time_col is None:
        time_col = df.columns[0]
    if flux_col is None:
        flux_col = df.columns[1]

    return time_col, flux_col


def find_column(df, options):
    for col in df.columns:
        if col in options:
            return col
    return None

# =========================
# HOME PAGE
# =========================

if st.session_state.page == "home":

    st.title("🪐 EXOPLANET DETECTOR")

    st.markdown("""
    <div class="hero">
    <h2>Universal NASA Exoplanet Analyzer</h2>
    <p>Supports Kepler, TESS and general NASA datasets</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 START MISSION"):

        st.session_state.started = True

        time.sleep(0.5)

        st.session_state.page = "analysis"

        st.rerun()
# =========================
# ANALYSIS PAGE
# =========================

if st.session_state.page == "analysis" and st.session_state.started:

    # =========================
    # TRANSIT DETECTION
    # =========================

    st.header("🛰️ Transit Detection")
    st.markdown("""
    <div style="
        font-size: 20px;
        font-weight: 600;
        text-align: left;
        color: #cfe8ff;
        margin-bottom: 10px;
">
Upload Kepler or TESS light curve to detect planetary transits
</div>
""", unsafe_allow_html=True)

    transit_file = st.file_uploader(
        "Upload Light Curve (CSV/FITS)",
        type=["csv", "fits", "fit"],
        key="transit"
    )

    if transit_file is not None:
        
        try:
            
            if transit_file.name.endswith(".csv"):
                df = pd.read_csv(transit_file)

                time_col, flux_col = detect_time_flux(df)

                time_data = df[time_col].values
                flux = df[flux_col].values

            else:
                hdul = fits.open(transit_file)
                data = hdul[1].data

                flux = data["PDCSAP_FLUX"] if "PDCSAP_FLUX" in data.names else data["SAP_FLUX"]
                time_data = data["TIME"] if "TIME" in data.names else np.arange(len(flux))

            mask = np.isfinite(time_data) & np.isfinite(flux)
            time_data = np.array(time_data)[mask]
            flux = np.array(flux)[mask]
            # Normalize flux
            flux = flux / np.median(flux)

            # Moving average smoothing
            window = 7
            flux_smooth = np.convolve(
                flux,
                np.ones(window) / window,
                mode="same"
            )
            noise= np.std(flux_smooth)

# TRANSIT SHAPE ANALYSIS (STEP 1)
# =========================

            dip_index = int(np.argmin(flux_smooth))
            dip_index = max(0, min(dip_index, len(flux_smooth)-1))

            window = 20
            n = len(flux_smooth)

            start = int(max(0, dip_index - window))
            end = int(min(n, dip_index + window))

            dip_region = flux_smooth[start:end]

            baseline = np.median(flux_smooth)
            minimum = np.min(dip_region)
            depth = ((baseline - minimum) / baseline) * 100
            local = flux_smooth[start:end]
            local = local / np.median(local)
            mid = len(local) // 2
            left = local[:mid]
            right = local[mid:]
            shape_score = abs(np.mean(left) - np.mean(right))

# -------------------------
# SHAPE FEATURES
# -------------------------

            left = flux_smooth[start:dip_index]
            right = flux_smooth[dip_index:end]
 
            if len(left) > 0 and len(right) > 0:
             asymmetry = abs(np.mean(left) - np.mean(right))/ (np.mean(flux_smooth)+ 1e-6)
            else:
             asymmetry = 0

            sharpness = baseline - minimum

            shape_score = asymmetry + sharpness

            st.markdown("""
            <div style="
                font-size: 26px;
                font-weight: 900;
                text-align: center;
                padding: 14px;
                border-radius: 15px;
                background: rgba(0,255,200,0.08);
                color: #00ffd5;
                text-shadow: 0 0 12px #00ffd5;
                margin-top: 10px;
            ">
            🛰️ TRANSIT ANALYSIS COMPLETE
            </div>
            """, unsafe_allow_html=True)

            # =========================
            # 2 × 2 METRIC GRID
            # =========================

            snr = depth / (noise * 100)

            confidence = min(
                99,
                max(50, snr * 10)
            )


            row1 = st.columns(2)
            row2 = st.columns(2)


            row1[0].metric(
                "Transit Depth",
                f"{depth:.2f}%"
            )

            row1[1].metric(
                "Data Points",
                len(flux)
            )

            row2[0].metric(
                "Noise",
                f"{noise:.5f}"
            )

            row2[1].metric(
                "Confidence",
                f"{confidence:.1f}%"
            )
            # -------------------------
            # SAFE ARRAY ALIGNMENT FIX
            # -------------------------

            n = min(len(time_data), len(flux), len(flux_smooth))

            time_data = time_data[:n]
            flux = flux[:n]
            flux_smooth = flux_smooth[:n]

            safe_index = min(dip_index, len(time_data)-1)
            fig, ax = plt.subplots(figsize=(10,4))

            # Light curve line
            ax.plot(
                time_data,
                flux,
                linewidth=1.8,
                label="Stellar Brightness"
            )

            # Transit detection marker
            ax.scatter(
                time_data[safe_index],
                flux[safe_index],
                color="red",
                s=120,
                marker="o",
                label="Transit Detected"
            )


            # Highlight transit area
            ax.axvspan(
                time_data[max(0,safe_index-20)],
                time_data[min(len(time_data)-1,safe_index+20)],
                alpha=0.2,
                label="Transit Window"
            )


            ax.set_title(
                "🛰️ AI Detected Exoplanet Transit",
                fontsize=14
            )

            ax.set_xlabel("Time (Days)")
            ax.set_ylabel("Normalized Flux")


            # Grid
            ax.grid(True, alpha=0.3)


            ax.legend()


            # cleaner layout
            plt.tight_layout()


            st.pyplot(fig)
            uncertainty = np.std(flux_smooth)

            st.write(
                f"Estimated Measurement Uncertainty: ±{uncertainty:.5f}"
            )

            # =========================
            # 🌌 AI SIGNAL CLASSIFICATION
            # =========================

            st.markdown("---")

            st.subheader("🪐 AI Detection Result")

            def show_result_box(text, color, icon):
                st.markdown(f"""
                <div style="
                    font-size: 28px;
                    font-weight: 950;
                    text-align: center;
                    padding: 16px;
                    border-radius: 16px;
                    background: rgba(255,255,255,0.08);
                    color: {color};
                    text-shadow: 0 0 14px {color};
                    box-shadow: 0 0 25px rgba(0,0,0,0.3);
                    margin-top: 10px;
                ">
                {icon} {text}
                </div>
                """, unsafe_allow_html=True)

            if depth > 0.5 and confidence >= 80:
                show_result_box(
                    "EXOPLANET CANDIDATE DETECTED",
                    "#00ff88",
                    "🪐"
                )
                result = "High Probability Transit"


            elif depth > 0.2 and shape_score < 0.03:
                show_result_box(
                    "EXOPLANET CANDIDATE DETECTED",
                    "#00ff88",
                    "🪐"
                )
                result = "Planet-like Signal"


            elif shape_score >= 0.03:

                show_result_box(
                    "SIGNAL UNCERTAIN",
                    "#ffcc00",
                    "⚠️"
                )

                result = "Possible False Positive"


            else:
                show_result_box(
                    "NO STRONG PLANET SIGNAL",
                    "#ff4d4d",
                    "⭐"
                )
                result = "Low Confidence"


            r1, r2 = st.columns(2)

            r1.metric(
                "Detection Status",
                result
            )

            r2.metric(
                "AI Confidence",
                f"{confidence:.1f}%"
            )
            st.write("DEBUG confidence:", confidence)
            st.write("DEBUG shape_score:", shape_score)   
            
        except Exception as e:
            st.error(e)
# =========================
# HABITABILITY INDEX (FULL NASA UPGRADE)
# =========================

if st.session_state.page == "analysis" and st.session_state.started:

    st.markdown("---")
    st.header("🌍 Habitability Index")
    st.markdown("""
    <div style="
        font-size: 20px;
        font-weight: 600;
        text-align: left;
        color: #cfe8ff;
        margin-bottom: 10px;
    ">
    Analyze planetary conditions and estimate habitability
    </div>
    """, unsafe_allow_html=True)

    habitability_file = st.file_uploader(
        "Upload Exoplanet Data (CSV/FITS)",
        type=["csv", "fits", "fit"],
        key="habitability"
    )

    def safe_get(df, col_list, i):
        for c in col_list:
            if c in df.columns:
                try:
                    return float(df[c].iloc[i])
                except:
                    return None
        return None

    if habitability_file is not None:

        try:

            if habitability_file.name.endswith(".csv"):
                hab_df = pd.read_csv(
                    habitability_file,
                    engine="python",
                    on_bad_lines="skip",
                    comment="#"
                )
            else:
                hdul = fits.open(habitability_file)
                hab_df = pd.DataFrame(np.array(hdul[1].data))

            hab_df.columns = [str(c).strip().lower() for c in hab_df.columns]

            st.subheader("Dataset Preview")
            st.dataframe(hab_df.head())

            # Column groups
            radius_cols = ["koi_prad", "pl_rade", "radius"]
            temp_cols = ["koi_teq", "pl_eqt", "temp", "equilibrium_temp"]
            flux_cols = ["koi_insol", "pl_insol", "flux"]

            period_cols = ["koi_period", "pl_orbper"]
            duration_cols = ["koi_duration"]
            depth_cols = ["koi_depth"]

            star_temp_cols = ["koi_steff", "st_teff"]
            star_logg_cols = ["koi_slogg", "st_logg"]
            star_rad_cols = ["koi_srad", "st_rad"]

            r_col = next((c for c in hab_df.columns if c in radius_cols), None)
            t_col = next((c for c in hab_df.columns if c in temp_cols), None)
            f_col = next((c for c in hab_df.columns if c in flux_cols), None)

            if r_col and t_col and f_col:

                clean = hab_df.dropna(subset=[r_col, t_col, f_col])

                st.subheader("🌌 Full Planet Profile")

                name_cols = [
                "kepler_name",
                "kepoi_name",
                "pl_name",
                "planet_name",
                "name"
            ]

                name_col = next(
                (c for c in hab_df.columns if c in name_cols),
                None
            )

                

                for i in range(min(5, len(clean))):

                    radius = safe_get(clean, radius_cols, i)
                    temp = safe_get(clean, temp_cols, i)
                    flux = safe_get(clean, flux_cols, i)

                    period = safe_get(clean, period_cols, i)
                    duration = safe_get(clean, duration_cols, i)
                    depth = safe_get(clean, depth_cols, i)

                    star_temp = safe_get(clean, star_temp_cols, i)
                    star_logg = safe_get(clean, star_logg_cols, i)
                    star_radius = safe_get(clean, star_rad_cols, i)

                    # =========================
                    # 🛰 ORBITAL DISTANCE (AU) FIXED
                    # =========================
                    flux_val = float(flux) if flux not in [None, "", 0] else None
                    distance_au = np.sqrt(1 / flux_val) if (flux_val and flux_val > 0) else None

                    # =========================
                    # Habitability score
                    # =========================
                    radius_score = np.exp(-((radius - 1)**2) / (2 * 0.5**2)) if radius else 0
                    temp_score = np.exp(-((temp - 288)**2) / (2 * 80**2)) if temp else 0
                    flux_score = np.exp(-((flux_val - 1)**2) / (2 * 0.5**2)) if flux_val else 0

                    score = 0.4 * radius_score + 0.3 * temp_score + 0.3 * flux_score
                    # Get the best available planet name
                    if "kepler_name" in clean.columns and pd.notna(clean.iloc[i]["kepler_name"]):
                        planet_name = clean.iloc[i]["kepler_name"]

                    elif "pl_name" in clean.columns and pd.notna(clean.iloc[i]["pl_name"]):
                        planet_name = clean.iloc[i]["pl_name"]

                    elif "toi" in clean.columns and pd.notna(clean.iloc[i]["toi"]):
                        planet_name = f"TOI-{clean.iloc[i]['toi']}"

                    elif "tic_id" in clean.columns and pd.notna(clean.iloc[i]["tic_id"]):
                        planet_name = f"TIC {clean.iloc[i]['tic_id']}"

                    elif "kepoi_name" in clean.columns and pd.notna(clean.iloc[i]["kepoi_name"]):
                        planet_name = clean.iloc[i]["kepoi_name"]

                    else:
                        planet_name = f"Exoplanet {i+1}"

                    st.markdown(
                        f'<div class="planet-name">🌍 {planet_name}</div>',
                        unsafe_allow_html=True
                    )
                    
                   
                    # =========================
                    # 🌍 PARAMETERS (4 × 3 GRID)
                    # =========================

                    row1 = st.columns(4)
                    row2 = st.columns(4)
                    row3 = st.columns(4)

                    # ---------- Row 1 ----------
                    row1[0].metric(
                        "🌍 Radius (R⊕)",
                        f"{radius:.2f}" if radius is not None else "N/A"
                    )

                    row1[1].metric(
                        "🌡 Temp (K)",
                        f"{temp:.2f}" if temp is not None else "N/A"
                    )

                    row1[2].metric(
                        "☀ Stellar Flux",
                        f"{flux_val:.2f}" if flux_val is not None else "N/A"
                    )

                    row1[3].metric(
                        "🛰 Distance (AU)",
                        f"{distance_au:.2f}" if distance_au is not None else "N/A"
                    )

                    # ---------- Row 2 ----------
                    row2[0].metric(
                        "🛰 Period (days)",
                        f"{period:.2f}" if period is not None else "N/A"
                    )

                    row2[1].metric(
                        "⏱ Duration (hrs)",
                        f"{duration:.2f}" if duration is not None else "N/A"
                    )

                    row2[2].metric(
                        "📉 Transit Depth",
                        f"{depth:.2f}" if depth is not None else "N/A"
                    )

                    row2[3].metric(
                        "🌍 Habitability",
                        f"{score:.2f}/1.00"
                    )

                    # ---------- Row 3 ----------
                    row3[0].metric(
                        "⭐ Star Temp (K)",
                        f"{star_temp:.2f}" if star_temp is not None else "N/A"
                    )

                    row3[1].metric(
                        "⭐ Surface Gravity",
                        f"{star_logg:.2f}" if star_logg is not None else "N/A"
                    )

                    row3[2].metric(
                        "⭐ Star Radius (R☉)",
                        f"{star_radius:.2f}" if star_radius is not None else "N/A"
                    )

                    row3[3].empty()

                    if score >= 0.75:
                        label = "🟢 HIGH HABITABILITY POTENTIAL"
                        color = "#00ff9d"
                    elif score >= 0.5:
                        label = "🟡 MODERATE HABITABILITY"
                        color = "#ffd166"
                    else:
                        label = "🔴 LOW HABITABILITY"
                        color = "#ff4d4d"

                    st.markdown(f"""
                    <div style="
                        font-size: 28px;
                        font-weight: 900;
                        text-align: center;
                        padding: 15px;
                        border-radius: 15px;
                        margin-top: 30px;        
                        background: rgba(255,255,255,0.08);
                        color: {color};
                        text-shadow: 0 0 10px {color};
                    ">
                    {label}
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("---")

                   

            else:
                st.error("Required columns not found in dataset")

        except Exception as e:
            st.error(e)
            

# =========================
# FOOTER
# =========================

st.markdown("---")
st.write("🚀 Universal Exoplanet Detector")
