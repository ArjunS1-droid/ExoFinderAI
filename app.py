
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
st.markdown(
"""
<style>

/* 🌌 Space background */
.stApp {
    background: radial-gradient(circle at 20% 20%, #0b0f2a, #000000);
    overflow-x: hidden;
}

/* ✨ Animated stars */
.stApp::before {
    content: "";
    position: absolute;
    width: 200%;
    height: 200%;
    background: transparent;
    background-image: radial-gradient(white 1px, transparent 1px);
    background-size: 50px 50px;
    animation: moveStars 60s linear infinite;
    opacity: 0.4;
    z-index: 0;
}

@keyframes moveStars {
    from { transform: translate(0,0); }
    to { transform: translate(-500px,-500px); }
}

/* Ensure content stays above stars */
.main {
    position: relative;
    z-index: 1;
}

/* 🌠 Glow effect for titles */
h1, h2, h3 {
    color: #7dd3fc;
    text-shadow: 0px 0px 10px #38bdf8;
}

/* 📦 Glass card effect */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(125,211,252,0.3);
    border-radius: 15px;
    padding: 10px;
    backdrop-filter: blur(10px);
    transition: 0.3s ease;
}

/* 🖱️ Hover animation */
div[data-testid="stMetric"]:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 20px #38bdf8;
}

/* 🎛 Buttons glow */
button {
    transition: 0.3s ease;
    border-radius: 10px !important;
}

button:hover {
    box-shadow: 0px 0px 15px #60a5fa;
    transform: scale(1.02);
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
