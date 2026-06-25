import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

st.set_page_config(page_title="ExoFinder AI", layout="wide")

st.title("🪐 ExoFinder AI")
st.subheader("Exoplanet Transit Detection and Habitability Analysis")

# ==========================================
# TRANSIT DETECTION SECTION
# ==========================================

st.header("🔭 Exoplanet Transit Detection")

transit_file = st.file_uploader(
    "Upload Light Curve Data (CSV or FITS)",
    type=["csv", "fits", "fit"],
    key="transit"
)

if transit_file is not None:

    try:

        # CSV FILE
        if transit_file.name.endswith(".csv"):

            df = pd.read_csv(transit_file)

            if len(df.columns) < 2:
                st.error("CSV must contain Time and Flux columns.")
                st.stop()

            time = df.iloc[:, 0]
            flux = df.iloc[:, 1]

        # FITS FILE
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

        transit_depth = (
            (median_flux - min_flux)
            / median_flux
        ) * 100

        dip_threshold = median_flux * 0.99

        dip_indices = np.where(
            flux < dip_threshold
        )[0]

        if len(dip_indices) > 1:

            transit_duration = len(dip_indices)

            dip_times = time[dip_indices]

            if len(dip_times) > 2:
                orbital_period = np.median(
                    np.diff(dip_times)
                )
            else:
                orbital_period = 0

        else:

            transit_duration = 0
            orbital_period = 0

        confidence = min(
            99,
            max(
                50,
                50 + transit_depth * 4
            )
        )

        st.success("Transit Analysis Complete")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Transit Depth (%)",
            f"{transit_depth:.4f}"
        )

        col2.metric(
            "Transit Duration",
            f"{transit_duration}"
        )

        col3.metric(
            "Estimated Period",
            f"{orbital_period:.4f}"
        )

        col4.metric(
            "Confidence (%)",
            f"{confidence:.1f}"
        )

        fig, ax = plt.subplots(
            figsize=(10, 4)
        )

        ax.plot(time, flux)

        ax.set_xlabel("Time")
        ax.set_ylabel("Flux")
        ax.set_title("Light Curve")

        st.pyplot(fig)

    except Exception as e:

        st.error(
            f"Error reading transit file: {e}"
        )

# ==========================================
# HABITABILITY SECTION
# ==========================================

st.markdown("---")

st.header("🌍 Habitability Analysis")

habitability_file = st.file_uploader(
    "Upload Habitability Data (CSV or FITS)",
    type=["csv", "fits", "fit"],
    key="habitability"
)

if habitability_file is not None:

    try:

        if habitability_file.name.endswith(".csv"):

            hab_df = pd.read_csv(
                habitability_file
            )

        else:

            hdul = fits.open(
                habitability_file
            )

            data = hdul[1].data

            hab_df = pd.DataFrame(
                np.array(data)
            )

        st.subheader(
            "Uploaded Habitability Data"
        )

        st.dataframe(hab_df.head())

        columns = [
            str(c).lower()
            for c in hab_df.columns
        ]

        score = 0

        # Planet Radius
        if "planet_radius" in columns:

            radius = float(
                hab_df.iloc[
                    0,
                    columns.index(
                        "planet_radius"
                    )
                ]
            )

            if 0.8 <= radius <= 1.5:
                score += 35

        # Equilibrium Temperature
        if "equilibrium_temp" in columns:

            temp = float(
                hab_df.iloc[
                    0,
                    columns.index(
                        "equilibrium_temp"
                    )
                ]
            )

            if 240 <= temp <= 320:
                score += 35

        # Stellar Flux
        if "stellar_flux" in columns:

            flux_star = float(
                hab_df.iloc[
                    0,
                    columns.index(
                        "stellar_flux"
                    )
                ]
            )

            if 0.75 <= flux_star <= 1.5:
                score += 30

        if score >= 80:

            status = (
                "🟢 Highly Habitable"
            )

        elif score >= 60:

            status = (
                "🟡 Potentially Habitable"
            )

        else:

            status = (
                "🔴 Low Habitability"
            )

        st.metric(
            "Habitability Score",
            f"{score}/100"
        )

        st.write(
            f"### Classification: {status}"
        )

    except Exception as e:

        st.error(
            f"Habitability Error: {e}"
        )

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.write(
    "🚀 ExoFinder AI | ISRO Hackathon Prototype"
)




        
