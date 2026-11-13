from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
from farmcarbon.runtime import build_runtime
from config.settings import settings

st.set_page_config(page_title="FarmCarbon MRV | Dashboard", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")

from farmcarbon.components.theme import apply_theme
apply_theme()

@st.cache_resource
def runtime():
    return build_runtime()

rt = runtime()
repo = rt["repo"]
farms = repo.list("farms")
soils = repo.list("soil_samples")
observations = repo.list("satellite_observations")
practices = repo.list("practices")
farm_name_map = {farm["id"]: farm["name"] for farm in farms}

st.title("FarmCarbon MRV")
st.caption("Agricultural carbon monitoring, reporting and verification workspace")
st.warning("DEMO DATA ACTIVE — seeded farms, satellite observations, soil samples and interventions are synthetic examples, not real field measurements or verified carbon results.", icon="⚠️")
st.info(rt["provider_notice"])

area = sum(float(f.get("area_ha") or 0) for f in farms)
farms_with_soil = len({s.get("farm_id") for s in soils})
latest_obs = len(observations)
soil_compare = []
for farm in farms:
    result = rt["mrv_service"].assess(farm)["comparison"]
    soil_compare.extend(result["comparisons"])
stock_change = sum(x["carbon_stock_change_mg_c"] or 0 for x in soil_compare) if soil_compare else None
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Registered farms", f"{len(farms)}")
c2.metric("Monitored area", f"{area:,.2f} ha")
c3.metric("Farms with soil samples", f"{farms_with_soil}")
c4.metric("Recorded interventions", f"{len(practices)}")
c5.metric("Satellite observations", f"{latest_obs}")
if stock_change is not None:
    st.metric("Comparable-zone carbon stock change", f"{stock_change:,.2f} Mg C", help="Calculated from matching demo sample pairs. Synthetic demonstration output only.")

left,right = st.columns([1.25,1])
with left:
    st.subheader("NDVI monitoring trend")
    if observations:
        df = pd.DataFrame(observations)
        df["observation_date"] = pd.to_datetime(df["observation_date"])
        df["farm_name"] = df["farm_id"].map(farm_name_map).fillna("Unknown farm")
        chart = px.line(df, x="observation_date", y="ndvi", color="farm_name", markers=True, title="NDVI by farm (source mode shown in records)")
        chart.update_layout(height=340, legend_title="Farm ID", margin=dict(l=10,r=10,t=45,b=10))
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("No satellite observations yet. Open Satellite Monitoring to import data.")
with right:
    st.subheader("Monitoring status")
    if farms:
        statuses=[]
        for farm in farms:
            a=rt["mrv_service"].assess(farm)
            statuses.append({"Farm":farm["name"],"Status":a["status"],"Completeness":a["completeness_score"]})
        st.dataframe(pd.DataFrame(statuses), use_container_width=True, hide_index=True)
    else:
        st.info("No farms registered yet.")

# Additional environmental and intervention views.
st.subheader("Monitoring indicators")
if observations:
    df_index = pd.DataFrame(observations)
    df_index["observation_date"] = pd.to_datetime(df_index["observation_date"])
    c_ndmi, c_evi = st.columns(2)
    with c_ndmi:
        df_index["farm_name"] = df_index["farm_id"].map(farm_name_map).fillna("Unknown farm")
        fig_ndmi = px.line(df_index, x="observation_date", y="ndmi", color="farm_name", markers=True, title="NDMI history (surface moisture indicator)")
        fig_ndmi.update_layout(height=300, margin=dict(l=10,r=10,t=45,b=10))
        st.plotly_chart(fig_ndmi, use_container_width=True)
    with c_evi:
        fig_evi = px.line(df_index, x="observation_date", y="evi", color="farm_name", markers=True, title="EVI history")
        fig_evi.update_layout(height=300, margin=dict(l=10,r=10,t=45,b=10))
        st.plotly_chart(fig_evi, use_container_width=True)
else:
    st.info("NDMI and EVI charts will appear when observations are available.")

c_soc, c_practice = st.columns(2)
with c_soc:
    st.subheader("Comparable-zone SOC stock")
    if soil_compare:
        soc_rows=[]
        for item in soil_compare:
            soc_rows.extend([
                {"Zone":item["zone_id"],"Period":"Baseline","SOC stock (Mg C/ha)":item["baseline_stock_mg_c_ha"]},
                {"Zone":item["zone_id"],"Period":"Follow-up","SOC stock (Mg C/ha)":item["followup_stock_mg_c_ha"]},
            ])
        fig_soc=px.bar(pd.DataFrame(soc_rows),x="Zone",y="SOC stock (Mg C/ha)",color="Period",barmode="group")
        fig_soc.update_layout(height=300,margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig_soc,use_container_width=True)
    else:
        st.info("No comparable baseline/follow-up SOC measurements yet.")
with c_practice:
    st.subheader("Agricultural intervention distribution")
    if practices:
        practice_df=pd.DataFrame(practices)
        fig_practice=px.bar(practice_df.groupby("practice_type",dropna=False).size().reset_index(name="Records"),x="practice_type",y="Records",title="Recorded practices")
        fig_practice.update_layout(height=300,margin=dict(l=10,r=10,t=45,b=10),xaxis_title="Practice",yaxis_title="Records")
        st.plotly_chart(fig_practice,use_container_width=True)
    else:
        st.info("No interventions recorded yet.")

st.subheader("Recent soil samples")
recent_soils=sorted(soils,key=lambda x:x.get("sample_date",""),reverse=True)[:6]
if recent_soils:
    farm_names={f["id"]:f["name"] for f in farms}
    st.dataframe(pd.DataFrame([{"Farm":farm_names.get(s.get("farm_id"),"Unknown"),"Sample":s.get("sample_identifier"),"Date":s.get("sample_date"),"Period":s.get("measurement_period"),"SOC stock (Mg C/ha)":s.get("calculated_soc_stock_mg_c_ha"),"Source":s.get("source_mode")} for s in recent_soils]),use_container_width=True,hide_index=True)
else:
    st.info("Soil samples will appear here as they are recorded.")

st.subheader("Recent activity")
activity = sorted(repo.list("audit_events"), key=lambda x:x.get("created_at",""), reverse=True)[:8]
if activity:
    st.dataframe(pd.DataFrame([{"When":x.get("created_at"),"Entity":x.get("entity_type"),"Action":x.get("action"),"Details":x.get("description"),"Source":x.get("source_mode")} for x in activity]), use_container_width=True, hide_index=True)
else:
    st.info("Activity will appear here as you add farms, samples and observations.")

with st.sidebar:
    st.markdown("### FarmCarbon MRV")
    st.caption("Local-first climate-tech demonstrator")
    st.markdown("**Data storage:** JSON files + GeoJSON + local uploads")
    st.markdown("**No SQL database is used.**")
    if st.button("Reset demonstration data", use_container_width=True):
        from farmcarbon.demo_data import seed_demo_data
        repo.store.clear()
        for upload in settings.uploads_dir.iterdir():
            if upload.is_file() and upload.name != ".gitkeep":
                upload.unlink(missing_ok=True)
        seed_demo_data(repo, force=False)
        st.success("Synthetic demonstration data reset. Local evidence uploads were cleared.")
        st.cache_resource.clear()
        st.rerun()
