```python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="ExoFinder AI", layout="wide")

st.title("🪐 ExoFinder AI")
st.subheader("Exoplanet Detection & Habitability Assessment")

tab1, tab2 = st.tabs(["Transit Detection", "Habitability Analysis"])

# --------------------------
# TAB 1 : TRANSIT DETECTION
# --------------------------

with tab1:

    st.header("Upload Light Curve Data")

    lightcurve_file = st.file_uploader(
        "Upload Light Curve CSV",
        type=["csv"],
        key="lc"
    )

    if lightcurve_file:

        df = pd.read_csv(lightcurve_file)

        if "time" not in df.columns or "flux" not in df.columns:
            st.error("CSV must contain 'time' and 'flux' columns")
        else:

            st.subheader("Preview")
            st.write(df.head())

            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(df["time"], df["flux"])
            ax.set_xlabel("Time")
            ax.set_ylabel("Flux")
            ax.set_title("Light Curve")

            st.pyplot(fig)

            median_flux = df["flux"].median()
            min_flux = df["flux"].min()

            transit_depth = (
                (median_flux - min_flux)
                / median_flux
            ) * 100

            threshold = median_flux * 0.99

            transit_points = df[
                df["flux"] < threshold
            ]

            if len(transit_points) > 1:
                transit_duration = (
                    transit_points["time"].max()
                    - transit_points["time"].min()
                )
            else:
                transit_duration = 0

            st.subheader("Transit Results")

            st.metric(
                "Transit Depth",
                f"{transit_depth:.3f}%"
            )

            st.metric(
                "Transit Duration",
                f"{transit_duration:.3f}"
            )

            if transit_depth > 1:

                confidence = min(
                    99,
                    50 +
                    transit_depth * 10 +
                    min(len(transit_points), 20)
                )

                st.success(
                    "Possible Exoplanet Transit Detected"
                )

                st.metric(
                    "Detection Confidence",
                    f"{confidence:.1f}%"
                )

            else:
                st.warning(
                    "No Significant Transit Found"
                )

# --------------------------
# TAB 2 : HABITABILITY
# --------------------------

with tab2:

    st.header("Upload Planet Parameters")

    planet_file = st.file_uploader(
        "Upload Planet Data CSV",
        type=["csv"],
        key="planet"
    )

    if planet_file:

        planet_df = pd.read_csv(planet_file)

        st.write(planet_df)

        row = planet_df.iloc[0]

        radius = row["radius"]
        mass = row["mass"]
        star_temp = row["star_temperature"]
        distance = row["distance_from_star"]

        score = 0

        # Radius
        if 0.8 <= radius <= 1.5:
            score += 25

        # Mass
        if 0.5 <= mass <= 5:
            score += 25

        # Habitable Zone
        if 0.8 <= distance <= 1.5:
            score += 25

        # Star Temperature
        if 4500 <= star_temp <= 6500:
            score += 25

        score = min(score, 100)

        st.subheader("Habitability Results")

        st.metric(
            "Habitability Score",
            f"{score}/100"
        )

        if score >= 75:
            status = "Potentially Habitable"
        elif score >= 50:
            status = "Moderately Habitable"
        else:
            status = "Low Habitability"

        st.write("### Status")
        st.success(status)

        confidence = min(
            99,
            score * 0.95
        )

        st.metric(
            "AI Confidence Rate",
            f"{confidence:.1f}%"
        )
```


        
