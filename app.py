
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
st.markdown(
"""
<style>

/* Background */
.stApp {
    background: radial-gradient(circle at 20% 20%, #0b1026, #000000);
}

/* SAFE STAR LAYER (no ::before) */
.stApp {
    background-image:
        radial-gradient(white 1px, transparent 1px);
    background-size: 50px 50px;
    animation: starMove 120s linear infinite;
}

/* Slow movement */
@keyframes starMove {
    from { background-position: 0 0; }
    to { background-position: -1000px 1000px; }
}

</style>
""",
unsafe_allow_html=True
)
/* =========================
   🪐 HEADINGS
========================= */

h1, h2, h3 {
    color: #e5e7eb !important;
    font-weight: 600;
    letter-spacing: 0.5px;
}

h1 {
    text-align: center;
}

/* =========================
   📦 GLASS CARDS (METRICS)
========================= */

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 12px;
    backdrop-filter: blur(12px);
    transition: 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border: 1px solid rgba(125,211,252,0.4);
}

/* Metric text */
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] div {
    color: #e5e7eb !important;
}

/* =========================
   📁 FILE UPLOADER FIX
========================= */

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 12px;
    padding: 10px;
}

/* uploader text */
[data-testid="stFileUploader"] * {
    color: #e5e7eb !important;
}

/* browse button */
button[data-testid="baseButton-secondary"] {
    background: #111827 !important;
    color: #e5e7eb !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
}

/* hover button */
button[data-testid="baseButton-secondary"]:hover {
    background: #1f2937 !important;
}

/* =========================
   🎛 BUTTONS (GLOBAL)
========================= */

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 12px;
    padding: 12px;
}

/* ALL text inside uploader */
[data-testid="stFileUploader"] * {
    color: #e5e7eb !important;
}

/* The actual "Browse files" button */
[data-testid="stFileUploader"] button {
    background-color: #111827 !important;
    color: #e5e7eb !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
}

/* Hover state */
[data-testid="stFileUploader"] button:hover {
    background-color: #1f2937 !important;
    border: 1px solid rgba(125,211,252,0.5) !important;
}

/* Fix weird white label area */
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: none !important;
}

/* =========================
   🌠 SIDEBAR
========================= */

section[data-testid="stSidebar"] {
    background: rgba(10, 15, 40, 0.9);
}

/* =========================
   📊 DATAFRAME
========================= */

div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* =========================
   ✨ INFO / SUCCESS BOXES
========================= */

.stAlert {
    border-radius: 12px;
}

/* =========================
   🚀 SPACING CLEANUP
========================= */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

</style>
""",
unsafe_allow_html=True
)
st.set_page_config(page_title="ExoFinder AI", layout="wide")

st.title("🪐 ExoFinder AI")
st.subheader("Exoplanet Transit Detection + NASA-Style Habitability Index")

# =========================
# TRANSIT SECTION
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

            cols = [c.upper() for c in data.names]

            if "TIME" in cols:
                time = data["TIME"]
            else:
                time = np.arange(len(data))

            if "PDCSAP_FLUX" in cols:
                flux = data["PDCSAP_FLUX"]
            elif "SAP_FLUX" in cols:
                flux = data["SAP_FLUX"]
            else:
                st.error("No usable flux column found.")
                st.stop()

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

        c1.metric("Transit Depth (%)", f"{transit_depth:.4f}")
        c2.metric("Duration", f"{transit_duration}")
        c3.metric("Period", f"{orbital_period:.4f}")
        c4.metric("Confidence (%)", f"{confidence:.1f}")

        fig, ax = plt.subplots()
        ax.plot(time, flux)
        ax.set_xlabel("Time")
        ax.set_ylabel("Flux")
        ax.set_title("Light Curve")

        st.pyplot(fig)

    except Exception as e:
        st.error(f"Transit Error: {e}")

# =========================
# HABITABILITY SECTION
# =========================

st.markdown("---")
st.header("🌍 Habitability Index (NASA Style)")

habitability_file = st.file_uploader(
    "Upload Habitability Data (CSV or FITS)",
    type=["csv", "fits", "fit"],
    key="habitability"
)

def gaussian_score(x, ideal, sigma):
    return np.exp(-((x - ideal) ** 2) / (2 * sigma ** 2))

if habitability_file is not None:

    try:

        if habitability_file.name.endswith(".csv"):

            hab_df = pd.read_csv(
                habitability_file,
                comment="#",
                on_bad_lines="skip"
            )

        else:

            hdul = fits.open(habitability_file)
            data = hdul[1].data
            hab_df = pd.DataFrame(np.array(data))

        st.subheader("Data Preview")
        st.dataframe(hab_df.head())

        # Planet selection
        if "kepler_name" in hab_df.columns:
            names = hab_df["kepler_name"].fillna(hab_df["kepoi_name"])
        else:
            names = hab_df["kepoi_name"]

        selected = st.selectbox("Select Planet", names)

        selected_row = hab_df[names == selected].iloc[0]

        st.subheader(f"🪐 Planet: {selected}")

        # Extract values
        radius = selected_row.get("koi_prad", np.nan)
        temp = selected_row.get("koi_teq", np.nan)
        flux_star = selected_row.get("koi_insol", np.nan)

        # NASA-style Gaussian scoring
        radius_score = 0
        temp_score = 0
        flux_score = 0

        if pd.notna(radius):
            radius_score = gaussian_score(radius, 1.0, 0.5)

        if pd.notna(temp):
            temp_score = gaussian_score(temp, 250, 80)
           

        if pd.notna(flux_star):
            flux_score = gaussian_score(flux_star, 1.0, 0.5)

        habitability_index = (
            0.4 * radius_score +
            0.3 * temp_score +
            0.3 * flux_score
        )

        habitability_percent = habitability_index * 100

        st.metric("Habitability Index", f"{habitability_index:.2f} / 1.00")
        st.metric("Habitability Score", f"{habitability_percent:.1f} %")

        # Classification
        if habitability_index >= 0.75:
            status = "🟢 High Potential Habitability"
        elif habitability_index >= 0.5:
            status = "🟡 Moderate Potential Habitability"
        else:
            status = "🔴 Low Habitability"

        st.write(f"### {status}")

        # Display values
        st.write(f"Planet Radius: {radius} Earth radii")
        st.write(f"Temperature: {temp} K")
        st.write(f"Stellar Flux: {flux_star}")

        st.info(
            "This index is a simplified NASA-inspired model based on similarity to Earth. "
            "It does not include atmosphere, water, or biosignatures."
        )

    except Exception as e:
        st.error(f"Habitability Error: {e}")

# =========================
# FOOTER
# =========================

st.markdown("---")
st.write("🚀 ExoFinder AI | ISRO Hackathon Project")
