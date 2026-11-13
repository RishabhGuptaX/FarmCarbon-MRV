from __future__ import annotations
from datetime import date, timedelta
import streamlit as st
import pandas as pd
from farmcarbon.runtime import build_runtime
from farmcarbon.components.charts import render_index_chart

st.set_page_config(page_title="Satellite Monitoring | FarmCarbon MRV", layout="wide")
from farmcarbon.components.theme import apply_theme
apply_theme()

@st.cache_resource
def runtime(): return build_runtime()
rt=runtime(); repo=rt["repo"]
st.title("Satellite Monitoring")
st.caption("Monitor vegetation and surface-moisture indicators. NDVI, NDMI and EVI are not direct soil-carbon measurements.")
st.info(rt["provider_notice"])
farms=repo.list("farms")
if not farms:
    st.info("Register a farm before collecting observations."); st.stop()
labels={f"{f['name']} · {f.get('project_identifier') or f['id'][:8]}":f for f in farms}
selected=st.selectbox("Farm",list(labels)); farm=labels[selected]
with st.form("satellite_request"):
    c1,c2,c3=st.columns(3)
    start=c1.date_input("Start date",value=date.today()-timedelta(days=365))
    end=c2.date_input("End date",value=date.today())
    cloud=c3.slider("Maximum scene cloud cover (%)",0,100,40)
    collect=st.form_submit_button("Collect satellite observations",type="primary")
if collect:
    try:
        if end<start: raise ValueError("End date must be on or after start date")
        with st.spinner("Collecting observations…"):
            saved=rt["satellite_service"].collect(farm,start,end,cloud)
        if saved: st.success(f"Saved {len(saved)} observations. Source mode: {rt['satellite_provider'].mode.upper()}.")
        else: st.warning("No new observations were returned. Try a wider date range or check the cloud threshold; duplicate observations are skipped.")
    except Exception as exc: st.error(f"Could not collect observations: {exc}")

with st.expander("Upload a satellite-observation CSV"):
    st.caption("Required columns: observation_date, ndvi, ndmi, evi, cloud_percentage. Every imported row is marked UPLOAD and must be independently checked.")
    csv_file=st.file_uploader("Observation CSV",type=["csv"],key="satellite_csv")
    if st.button("Import CSV",disabled=csv_file is None):
        try:
            df=pd.read_csv(csv_file)
            required={"observation_date","ndvi","ndmi","evi","cloud_percentage"}
            missing=required-set(df.columns)
            if missing: raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
            imported=0
            for row in df.to_dict(orient="records"):
                vals=[float(row[k]) for k in ("ndvi","ndmi","evi","cloud_percentage")]
                if not all(pd.notna(v) for v in vals): raise ValueError("CSV contains empty indicator values")
                if not -1 <= vals[0] <= 1: raise ValueError("NDVI must be between -1 and 1")
                if not -1 <= vals[1] <= 1: raise ValueError("NDMI must be between -1 and 1")
                if not 0 <= vals[3] <= 100: raise ValueError("Cloud percentage must be between 0 and 100")
                record={"farm_id":farm["id"],"observation_date":pd.to_datetime(row["observation_date"]).date().isoformat(),
                    "ndvi":vals[0],"ndmi":vals[1],"evi":vals[2],"cloud_percentage":vals[3],
                    "source":"User uploaded CSV","source_collection":"USER_CSV","source_mode":"UPLOAD",
                    "algorithm_version":"user-supplied","metadata_json":{"filename":csv_file.name}}
                repo.create("satellite_observations",record); imported+=1
            repo.audit(farm["id"],"satellite_observation",farm["id"],"UPLOAD",f"Imported {imported} observations from CSV","UPLOAD")
            st.success(f"Imported {imported} observation rows."); st.rerun()
        except Exception as exc: st.error(f"CSV import failed: {exc}")

observations=sorted(repo.list("satellite_observations",farm_id=farm["id"]),key=lambda x:x.get("observation_date",""))
st.subheader("Observation history")
if observations:
    for index in ("ndvi","ndmi","evi"):
        render_index_chart(observations,index,title=f"{index.upper()} trend — {farm['name']}")
    df=pd.DataFrame(observations)
    st.dataframe(df[[c for c in ["observation_date","ndvi","ndmi","evi","cloud_percentage","source","source_mode"] if c in df.columns]],use_container_width=True,hide_index=True)
    col1,col2=st.columns(2)
    col1.metric("Observations",len(observations))
    col2.metric("Mean cloud cover",f"{pd.to_numeric(df['cloud_percentage'],errors='coerce').mean():.1f}%")
    st.download_button("Download observations CSV",df.to_csv(index=False),file_name=f"{farm['id']}_satellite_observations.csv",mime="text/csv")
else: st.info("No monitoring observations yet. Collect using the selected provider or upload a CSV.")
