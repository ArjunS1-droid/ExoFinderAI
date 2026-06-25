import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

st.markdown(
"""
<style>
.stApp h1 {
    color: #ffffff !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* =========================
   🌌 BASE BACKGROUND
========================= */

.stApp {
    background: radial-gradient(circle at 20% 20%, #0b1026, #000000);
    color: #e5e7eb;
    font-family: 'Segoe UI', sans-serif;
}

/* =========================
   🪐 TYPOGRAPHY (FIXED HIERARCHY)
========================= */

h1 {
    color: #f8fafc !important;
    font-size: 2.6rem !important;
    font-weight: 800 !important;
    text-align: center;
    margin-bottom: 1rem;
}

h2 {
    color: #e5e7eb !important;
    font-size: 1.7rem !important;
    font-weight: 650 !important;
    margin-top: 1.2rem;
}

h3 {
    color: #cbd5e1 !important;
    font-size: 1.3rem !important;
    font-weight: 500 !important;
}

/* =========================
   📦 METRIC CARDS (NASA STYLE)
========================= */

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 12px;
    transition: 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border: 1px solid rgba(125,211,252,0.4);
}

/* Metric text fix */
div[data-testid="stMetric"] * {
    color: #e5e7eb !important;
}

/* =========================
   📁 FILE UPLOADER (FIXED)
========================= */

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 12px;
    padding: 12px;
}

/* uploader text */
[data-testid="stFileUploader"] * {
    color: #e5e7eb !important;
}

/* browse button */
[data-testid="stFileUploader"] button {
    background: #111827 !important;
    color: #e5e7eb !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
}

/* hover button */
[data-testid="stFileUploader"] button:hover {
    background: #1f2937 !important;
    border: 1px solid rgba(125,211,252,0.4) !important;
}

/* =========================
   🎛 BUTTONS
========================= */

button {
    border-radius: 10px !important;
    transition: 0.2s ease;
}

button:hover {
    transform: scale(1.02);
}

/* =========================
   📊 DATA TABLE
========================= */

div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* =========================
   🌠 SIDEBAR
========================= */

section[data-testid="stSidebar"] {
    background: rgba(10, 15, 40, 0.9);
}

/* =========================
   ✨ INFO BOXES
========================= */

.stAlert {
    border-radius: 12px;
}

/* =========================
   🚀 SAFE SPACING
========================= */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}


</style>
""",
unsafe_allow_html=True
)

# =========================
# TRANSIT DETECTION
# =========================

st.header("🔭 Transit Detection")

transit_file = st.file_uploader(
    "Upload Light Curve Data (CSV or FITS)",
    type=["csv", "fits", "fit"],
    key="transit"
)

if transit_file is not None:

    try:

        if transit_file.name.endswith(".csv"):

            df = pd.read_csv(transit_file)

            time = df.iloc[:, 0].values
            flux = df.iloc[:, 1].values

        else:

            hdul = fits.open(transit_file)
            data = hdul[1].data

            if "PDCSAP_FLUX" in data.names:
                flux = data["PDCSAP_FLUX"]
            elif "SAP_FLUX" in data.names:
                flux = data["SAP_FLUX"]
            else:
                st.error("No usable flux column found.")
                st.stop()

            if "TIME" in data.names:
                time = data["TIME"]
            else:
                time = np.arange(len(flux))

        mask = np.isfinite(time) & np.isfinite(flux)
        time = np.array(time)[mask]
        flux = np.array(flux)[mask]

        median_flux = np.median(flux)
        min_flux = np.min(flux)

        transit_depth = ((median_flux - min_flux) / median_flux) * 100

        dip_threshold = median_flux * 0.99
        dip_indices = np.where(flux < dip_threshold)[0]

        if len(dip_indices) > 1:
            transit_duration = len(dip_indices)
            dip_times = time[dip_indices]

            if len(dip_times) > 2:
                orbital_period = np.median(np.diff(dip_times))
            else:
                orbital_period = 0
        else:
            transit_duration = 0
            orbital_period = 0

        confidence = min(99, max(50, 50 + transit_depth * 4))

        st.success("Transit Analysis Complete")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Depth (%)", f"{transit_depth:.2f}")
        c2.metric("Duration", f"{transit_duration}")
        c3.metric("Period", f"{orbital_period:.2f}")
        c4.metric("Confidence", f"{confidence:.1f}%")

        fig, ax = plt.subplots()
        ax.plot(time, flux)
        ax.set_title("Light Curve")
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Transit Error: {e}")

# =========================
# HABITABILITY SECTION
# =========================

st.markdown("---")
st.header("🌍 Habitability Index")

habitability_file = st.file_uploader(
    "Upload Kepler Habitability Data (CSV/FITS)",
    type=["csv", "fits", "fit"],
    key="habitability"
)

def gaussian(x, mu, sigma):
    return np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

if habitability_file is not None:

    try:

        if habitability_file.name.endswith(".csv"):
            hab_df = pd.read_csv(habitability_file, on_bad_lines="skip")
        else:
            hdul = fits.open(habitability_file)
            hab_df = pd.DataFrame(np.array(hdul[1].data))

        st.subheader("Dataset Preview")
        st.dataframe(hab_df.head())

        if "kepler_name" in hab_df.columns:
            names = hab_df["kepler_name"].fillna(hab_df["kepoi_name"])
        else:
            names = hab_df["kepoi_name"]

        selected = st.selectbox("Select Planet", names)
        row = hab_df[names == selected].iloc[0]

        radius = row.get("koi_prad", np.nan)
        temp = row.get("koi_teq", np.nan)
        flux = row.get("koi_insol", np.nan)

        r_score = gaussian(radius, 1.0, 0.5) if pd.notna(radius) else 0
        t_score = gaussian(temp, 250, 80) if pd.notna(temp) else 0
        f_score = gaussian(flux, 1.0, 0.5) if pd.notna(flux) else 0

        habitability_index = 0.4*r_score + 0.3*t_score + 0.3*f_score
        habitability_percent = habitability_index * 100

        st.metric("Index", f"{habitability_index:.2f}/1.00")
        st.metric("Score", f"{habitability_percent:.1f}%")

        if habitability_index >= 0.75:
            st.success("High Habitability Potential 🟢")
        elif habitability_index >= 0.5:
            st.warning("Moderate Habitability 🟡")
        else:
            st.error("Low Habitability 🔴")

        st.write(f"Radius: {radius} R⊕")
        st.write(f"Temperature: {temp} K")
        st.write(f"Flux: {flux} S⊕")

        st.info(
            "This is a simplified Earth-similarity model based on KOI parameters. "
            "Real habitability depends on atmosphere, water, and climate."
        )

    except Exception as e:
        st.error(f"Habitability Error: {e}")

# =========================
# FOOTER
# =========================

st.markdown("---")
st.write("🚀 ExoFinder AI | ISRO Hackathon Project")
