import streamlit as st

st.set_page_config(page_title="Methodology | FarmCarbon MRV",layout="wide")
from farmcarbon.components.theme import apply_theme
apply_theme()

st.title("Methodology & Data Limitations")
st.caption("Transparent methods for the independent FarmCarbon MRV demonstrator.")

st.subheader("Local data architecture")
st.markdown("""
FarmCarbon MRV does **not** use a SQL database. The MVP stores records in JSON files under `storage/data/`,
farm geometries as GeoJSON objects, and uploaded evidence under `storage/uploads/`. CSV and GeoJSON are
used for portable exports. Writes are atomic at the individual collection-file level. This design is
intended for a local, single-user demonstrator; it is not a multi-user transactional database.
""")

st.subheader("Satellite indicators")
st.markdown(r"""
- **NDVI** = (NIR − Red) / (NIR + Red)
- **NDMI** = (NIR − SWIR) / (NIR + SWIR)
- **EVI** = 2.5 × (NIR − Red) / (NIR + 6 × Red − 7.5 × Blue + 1)

The optional Google Earth Engine provider uses `COPERNICUS/S2_SR_HARMONIZED` and masks Sentinel-2
Scene Classification Layer classes 3, 8, 9, 10 and 11 (cloud shadow, cloud, cirrus and snow/ice classes).
The demo provider emits synthetic index values and labels every record `DEMO`. NDVI, NDMI and EVI are
vegetation/surface indicators; they do not directly measure soil organic carbon or carbon removal.
""")

st.subheader("Soil organic carbon stock")
st.latex(r"SOC\ Stock\ (Mg\ C/ha)=SOC\ (g/kg)\times BD\ (g/cm^3)\times(1-f_{coarse})\times depth\ (cm)\times0.1")
st.write("The implementation uses fixed-depth stock calculation. A baseline/follow-up comparison is only paired when farm, zone, top and bottom sampling depths, and documented measurement method match. Bulk-density changes raise a warning because equivalent soil mass adjustment may be necessary.")
st.info("Example: 10 g/kg × 1.3 g/cm³ × (1 − 0.10) × 30 cm × 0.1 = 35.1 Mg C/ha.")

st.subheader("Carbon stock change and CO₂e")
st.latex(r"Carbon\ stock\ change\ (Mg\ C)=SOC\ stock\ change\ (Mg\ C/ha)\times zone\ area\ (ha)")
st.latex(r"CO_2e\ equivalent\ (Mg)=Carbon\ stock\ change\ (Mg\ C)\times\frac{44}{12}")
st.write("Negative changes are retained. A farm-wide value is not generated when there are no valid comparable measurements. Zone area is required to calculate total carbon mass change.")

st.subheader("MRV review")
st.write("Completeness is a project-management checklist score, not scientific confidence. Review completion is recorded only after an explicit action by a named reviewer. This application does not issue a third-party verification statement, carbon-credit certificate or registry record.")

st.subheader("Important limitations")
st.markdown("""
- Synthetic demo values are examples only and must never be presented as real field measurements.
- Uploaded satellite records are not independently authenticated by this application.
- Laboratory methods, sampling design, bulk density, coarse fragments and depth must be documented and comparable.
- Equivalent soil mass adjustment, uncertainty propagation, leakage, additionality, permanence and carbon-credit protocol validation are outside this MVP.
- This tool is an independent demonstrator, not an official Varaha product and not a certification system.
""")
