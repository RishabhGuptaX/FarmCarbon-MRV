from __future__ import annotations
import json
import streamlit as st
import pandas as pd
from farmcarbon.runtime import build_runtime
from farmcarbon.components.maps import show_farm_map

st.set_page_config(page_title="Farm Registry | FarmCarbon MRV", layout="wide")
@st.cache_resource
def runtime(): return build_runtime()
rt=runtime(); repo=rt["repo"]

st.title("Farm Registry")
st.caption("Register farms, validate field boundaries and manage farm records.")

with st.expander("Register a new farm", expanded=not bool(repo.list("farms"))):
    with st.form("farm_registration", clear_on_submit=True):
        c1,c2=st.columns(2)
        name=c1.text_input("Farm name *")
        project_id=c2.text_input("Farmer / project identifier")
        country=c1.text_input("Country", value="India")
        state=c2.text_input("State")
        district=c1.text_input("District")
        village=c2.text_input("Village")
        crop=c1.text_input("Primary crop")
        soil_type=c2.text_input("Soil type (optional)")
        farming_system=c1.selectbox("Farming system", ["Rainfed", "Irrigated", "Mixed cropping", "Agroforestry", "Rice-based", "Other"])
        start=c2.date_input("Project start date")
        baseline=c1.date_input("Baseline date")
        description=c2.text_area("Project description")
        st.markdown("**Farm boundary**")
        boundary_file=st.file_uploader("Upload GeoJSON Polygon or MultiPolygon", type=["geojson", "json"], key="farm_boundary")
        st.caption("A valid boundary calculates area geodesically and derives the centroid. Without a boundary, provide coordinates and area below.")
        c3,c4,c5=st.columns(3)
        lat=c3.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0, format="%.6f")
        lon=c4.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0, format="%.6f")
        area=c5.number_input("Area (ha) without boundary", min_value=0.0, value=0.0, step=0.1)
        submitted=st.form_submit_button("Register farm", type="primary")
    if submitted:
        try:
            payload={"name":name,"project_identifier":project_id,"country":country,"state":state,"district":district,"village":village,
                "crop":crop,"soil_type":soil_type,"farming_system":farming_system,"project_start_date":start.isoformat(),
                "baseline_date":baseline.isoformat(),"description":description,"latitude":lat if not boundary_file else None,
                "longitude":lon if not boundary_file else None,"area_ha":area}
            farm=rt["farm_service"].register(payload, boundary_file.getvalue() if boundary_file else None)
            st.success(f"Registered {farm['name']} successfully.")
            st.rerun()
        except Exception as exc: st.error(str(exc))

st.divider(); farms=repo.list("farms")
if not farms:
    st.info("No farms registered. Add a farm above or reset/load the demonstration dataset from the Dashboard.")
else:
    farm_labels={f"{f['name']} · {f.get('project_identifier') or f['id'][:8]}":f for f in farms}
    selected_label=st.selectbox("Select farm", list(farm_labels))
    farm=farm_labels[selected_label]
    left,right=st.columns([1,1])
    with left:
        st.subheader("Farm details")
        st.write(f"**Location:** {', '.join(filter(None,[farm.get('village'),farm.get('district'),farm.get('state'),farm.get('country')]))}")
        st.write(f"**Area:** {float(farm.get('area_ha') or 0):,.3f} ha")
        st.write(f"**Crop:** {farm.get('crop') or '—'}")
        st.write(f"**Farming system:** {farm.get('farming_system') or '—'}")
        st.write(f"**Coordinates:** {farm.get('latitude')}, {farm.get('longitude')}")
        st.write(f"**Project start / baseline:** {farm.get('project_start_date')} / {farm.get('baseline_date')}")
        if farm.get("source_mode")=="DEMO": st.caption("DEMO FARM — synthetic example record")
        with st.expander("Edit farm details"):
            with st.form("edit_farm"):
                edit_name=st.text_input("Farm name", value=farm.get("name", ""))
                edit_crop=st.text_input("Primary crop", value=farm.get("crop", ""))
                edit_soil=st.text_input("Soil type", value=farm.get("soil_type", ""))
                edit_desc=st.text_area("Description", value=farm.get("description", ""))
                save=st.form_submit_button("Save changes")
            if save:
                rt["farm_service"].update(farm["id"], {"name":edit_name,"crop":edit_crop,"soil_type":edit_soil,"description":edit_desc})
                st.success("Farm updated."); st.rerun()
        if st.button("Prepare farm deletion", key="prepare_delete"):
            st.session_state["confirm_delete_farm"]=farm["id"]
        if st.session_state.get("confirm_delete_farm")==farm["id"]:
            st.warning("This permanently removes the farm and its related samples, observations, interventions, reviews and evidence files.")
            c1,c2=st.columns(2)
            if c1.button("Confirm delete", type="primary"):
                rt["farm_service"].delete(farm["id"]); st.session_state.pop("confirm_delete_farm",None); st.success("Farm and dependent records deleted."); st.rerun()
            if c2.button("Cancel"):
                st.session_state.pop("confirm_delete_farm",None); st.rerun()
    with right:
        st.subheader("Field boundary")
        show_farm_map(farm)
        if farm.get("boundary_geojson"):
            geojson={"type":"FeatureCollection","features":[{"type":"Feature","properties":{"farm":farm["name"]},"geometry":farm["boundary_geojson"]}]}
            st.download_button("Download boundary GeoJSON", json.dumps(geojson,indent=2), file_name=f"{farm['id']}_boundary.geojson", mime="application/geo+json")
        else: st.warning("No polygon boundary recorded.")
        with st.expander("Upload or replace field boundary"):
            replacement=st.file_uploader("New GeoJSON Polygon / MultiPolygon",type=["geojson","json"],key=f"replace_boundary_{farm['id']}")
            if st.button("Validate and save new boundary",disabled=replacement is None,key=f"save_boundary_{farm['id']}"):
                try:
                    updated=rt["farm_service"].replace_boundary(farm["id"],replacement.getvalue())
                    st.success(f"Boundary saved. New geodesic area: {updated['area_ha']:.4f} ha.")
                    st.rerun()
                except Exception as exc: st.error(str(exc))
    st.subheader("Farm monitoring records")
    tabs=st.tabs(["Soil samples","Satellite observations","Interventions","MRV reports"])
    for tab,collection in zip(tabs,["soil_samples","satellite_observations","practices","mrv_reviews"]):
        with tab:
            records=repo.list(collection,farm_id=farm["id"])
            st.dataframe(pd.DataFrame(records) if records else pd.DataFrame(),use_container_width=True,hide_index=True)
