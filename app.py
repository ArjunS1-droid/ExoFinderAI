import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

st.set_page_config(page_title="ExoFinder AI", layout="wide")

st.title("🪐 ExoFinder AI")
st.subheader("Exoplanet Transit Detection and Habitability Analysis")

uploaded_file = st.file_uploader(
    "Upload Light Curve Data (CSV or FITS)",
    type=["csv", "fits", "fit"]
)

if uploaded_file is not None:

    try:
        # CSV FILE
        if uploaded_file.name.endswith(".csv"):

            df = pd.read_csv(uploaded_file)

            if len(df.columns) < 2:
                st.error("CSV must contain Time and Flux columns.")
                st.stop()

            time = df.iloc[:, 0]
            flux = df.iloc[:, 1]

        # FITS FILE
        else:

            hdul = fits.open(uploaded_file)
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

        confidence = min(
            99,
            max(
                50,
                50 + transit_depth * 4
            )
        )

        st.success("Analysis Complete")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Transit Depth (%)", f"{transit_depth:.4f}")
        col2.metric("Transit Duration", f"{transit_duration}")
        col3.metric("Estimated Period", f"{orbital_period:.4f}")
        col4.metric("Confidence (%)", f"{confidence:.1f}")

        st.subheader("Habitability Assessment")

        if transit_depth < 1:
            habitability = "Potentially Habitable"
            score = 80
        elif transit_depth < 3:
            habitability = "Possibly Habitable"
            score = 60
        else:
            habitability = "Low Habitability"
            score = 30

        st.write(f"**Classification:** {habitability}")
        st.write(f"**Habitability Score:** {score}/100")

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(time, flux)
        ax.set_xlabel("Time")
        ax.set_ylabel("Flux")
        ax.set_title("Light Curve")
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error reading file: {e}")


        
