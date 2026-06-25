import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

st.set_page_config(page_title="ExoFinder AI", layout="wide")

st.title("🪐 ExoFinder AI")
st.subheader("Exoplanet Transit Detection and Habitability Analysis")

# ==================================================
# TRANSIT DETECTION SECTION
# ==================================================

st.header("🔭 Exoplanet Transit Detection")

transit_file = st.file_uploader(
    "Upload Light Curve Data (CSV or FITS)",
    type=["csv", "fits", "fit"],
    key="transit"
)

if transit_file is not None:

    try:

        if transit_file.name.endswith(".csv"):

            df = pd.read_csv(transit_file)

            if len(df.columns) < 2:
                st.error("CSV must contain Time and Flux columns.")
                st.stop()

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

        transit_depth = (
            (median_flux - min_flux) / median_flux
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

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Transit Depth (%)",
            f"{transit_depth:.4f}"
        )

        c2.metric(
            "Transit Duration",
            f"{transit_duration}"
        )

        c3.metric(
            "Estimated Period",
            f"{orbital_period:.4f}"
        )

        c4.metric(
            "Confidence (%)",
            f"{confidence:.1f}"
        )

        fig, ax = plt.subplots(figsize=(10, 4))

        ax.plot(time, flux)

        ax.set_xlabel("Time")
        ax.set_ylabel("Flux")
        ax.set_title("Light Curve")

        st.pyplot(fig)

    except Exception as e:

        st.error(f"Transit File Error: {e}")

# ==================================================
# HABITABILITY SECTION
# ==================================================

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
                habitability_file,
                comment="#",
                on_bad_lines="skip"
            )

        else:

            hdul = fits.open(habitability_file)

            data = hdul[1].data

            hab_df = pd.DataFrame(
                np.array(data)
            )

        st.subheader("Uploaded Habitability Data")

        st.dataframe(hab_df.head())

        # Planet selector
        if "kepler_name" in hab_df.columns:

            planet_names = hab_df["kepler_name"].fillna(
                hab_df["kepoi_name"]
            )

        else:

            planet_names = hab_df["kepoi_name"]

        selected_planet = st.selectbox(
            "Select Planet",
            planet_names
        )

        selected_row = hab_df[
            planet_names == selected_planet
        ].iloc[0]

        st.subheader(
            f"🪐 Planet: {selected_planet}"
        )

        score = 0

        radius = selected_row.get("koi_prad", np.nan)
        temp = selected_row.get("koi_teq", np.nan)
        insol = selected_row.get("koi_insol", np.nan)

        if pd.notna(radius):

            if 0.8 <= radius <= 1.8:
                score += 35

        if pd.notna(temp):
            if 150 <= temp <= 200:
                  score += 20
  
            elif 200 <= temp <= 350:
                 score += 35
   

 

        if pd.notna(insol):
            if 0.20 <= insol < 0.25:
                score += 15
    
            elif 0.25 <= insol <= 2.0:
                   score += 30
   

           

        st.write(f"**Planet Radius:** {radius}")
        st.write(f"**Equilibrium Temperature:** {temp} K")
        st.write(f"**Stellar Flux:** {insol}")

        if score >= 80:

            status = "🟢 Highly Habitable"

        elif score >= 60:

            status = "🟡 Potentially Habitable"

        else:

            status = "🔴 Low Habitability"

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

# ==================================================
# FOOTER
# ==================================================

st.markdown("---")

st.write(
    "🚀 ExoFinder AI | ISRO Hackathon Prototype"
)
