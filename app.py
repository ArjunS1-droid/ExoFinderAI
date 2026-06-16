import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits

st.title("🌍 ExoFinderAI")
st.write("Upload a FITS light curve file to detect possible exoplanets.")

uploaded_file = st.file_uploader(
    "Upload FITS File",
    type=["fits"]
)

if uploaded_file is not None:
        with fits.open(uploaded_file) as hdul:

            data = hdul[1].data
            df = pd.DataFrame(data)

            st.subheader("Light Curve Data")
            st.write(df.head())

            if "TIME" in df.columns and "SAP_FLUX" in df.columns:

                fig, ax = plt.subplots(figsize=(10, 5))

                ax.plot(df["TIME"], df["SAP_FLUX"])

                transit_idx = df["SAP_FLUX"].idxmin()

                ax.scatter(
                    df["TIME"][transit_idx],
                    df["SAP_FLUX"][transit_idx]
                )

                ax.set_xlabel("Time")
                ax.set_ylabel("SAP Flux")
                ax.set_title("Light Curve")

                st.pyplot(fig)

                min_flux = df["SAP_FLUX"].min()
                avg_flux = df["SAP_FLUX"].mean()

                dip_percent = (
                    (avg_flux - min_flux)
                    / avg_flux
                ) * 100

                confidence = min(
                    99,
                    round(dip_percent * 20)
                )

                st.subheader("Analysis")

                st.metric(
                    "Minimum Flux",
                    round(min_flux, 2)
                )

                st.metric(
                    "Average Flux",
                    round(avg_flux, 2)
                )

                st.metric(
                    "Brightness Dip %",
                    round(dip_percent, 2)
                )

                if min_flux < 0.99 * avg_flux:

                    st.success(
                        "Possible Exoplanet Candidate Detected"
                    )

        
