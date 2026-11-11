from __future__ import annotations
from datetime import date
import streamlit as st
import pandas as pd
from pathlib import Path
from farmcarbon.runtime import build_runtime
from config.settings import settings
from farmcarbon.utils.file_manager import resolve_upload

st.set_page_config(page_title="Agricultural Practices | FarmCarbon MRV",layout="wide")
@st.cache_resource
def runtime(): return build_runtime()
rt=runtime(); repo=rt["repo"]
st.title("Agricultural Practices")
st.caption("Record implementation activities and attach supporting field evidence.")
farms=repo.list("farms")
if not farms: st.info("Register a farm first."); st.stop()
labels={f"{f['name']} · {f.get('project_identifier') or f['id'][:8]}":f for f in farms}
selected=st.selectbox("Farm",list(labels)); farm=labels[selected]
practice_types=["Reduced Tillage","No-Till Farming","Cover Cropping","Crop Residue Retention","Crop Rotation","Organic Manure Application","Compost Application","Agroforestry","Improved Nutrient Management","Water Management","Biochar Application"]
with st.form("practice_form",clear_on_submit=True):
    c1,c2,c3=st.columns(3)
    practice=c1.selectbox("Practice category",practice_types)
    zone=c2.text_input("Sampling zone / field",value="ZONE-01")
    status=c3.selectbox("Implementation status",["Planned","In Progress","Implemented","Discontinued"])
    start=c1.date_input("Implementation date",value=date.today())
    has_end=c2.checkbox("Completion date available")
    end=c2.date_input("Completion date",value=date.today()) if has_end else None
    area=c3.number_input("Area covered (ha)",min_value=0.0,max_value=max(float(farm.get("area_ha") or 0),0.0) if float(farm.get("area_ha") or 0)>0 else 100000.0,value=0.0,step=0.1)
    crop=c1.text_input("Crop",value=farm.get("crop") or "")
    quantity=c2.number_input("Application quantity (optional)",min_value=0.0,value=0.0,step=1.0)
    unit=c3.text_input("Quantity unit")
    details=st.text_area("Input / material details and field notes")
    attachment=st.file_uploader("Evidence attachment (image, CSV or PDF)",type=["png","jpg","jpeg","webp","csv","pdf"])
    submit=st.form_submit_button("Save intervention",type="primary")
if submit:
    try:
        if area<=0: raise ValueError("Area covered must be greater than zero")
        record=repo.create("practices",{"farm_id":farm["id"],"zone_id":zone,"practice_type":practice,"start_date":start.isoformat(),
            "end_date":end.isoformat() if end else None,"area_ha":area,"crop":crop,"quantity":quantity or None,"unit":unit or None,
            "status":status,"description":details,"source_mode":"USER"})
        if attachment:
            evidence=rt["practice_service"].save_upload(attachment,farm["id"],record["id"])
            st.success(f"Intervention saved with evidence file {evidence['file_name']}.")
        else: st.success("Intervention saved. No evidence file was attached.")
        repo.audit(farm["id"],"practice",record["id"],"CREATE",f"Recorded {practice}")
        st.rerun()
    except Exception as exc: st.error(str(exc))

practices=repo.list("practices",farm_id=farm["id"]); evidence=repo.list("evidence_files",farm_id=farm["id"])
st.subheader("Intervention register")
if practices:
    st.dataframe(pd.DataFrame(practices),use_container_width=True,hide_index=True)
else: st.info("No interventions recorded for this farm.")
st.subheader("Supporting evidence")
if evidence:
    for item in evidence:
        cols=st.columns([3,1,2])
        cols[0].write(item.get("file_name"))
        cols[1].caption(item.get("file_type"))
        path=item.get("stored_path")
        if path:
            try:
                file_path=resolve_upload(path,settings.uploads_dir)
                if file_path.exists(): cols[2].download_button("Download",file_path.read_bytes(),file_name=item.get("file_name") or file_path.name,key=item["id"])
                else: cols[2].caption("File missing on disk")
            except Exception as exc: cols[2].caption(str(exc))
        else: cols[2].caption("Demo metadata only — no actual file")
else: st.info("Evidence files uploaded with interventions or soil samples appear here.")
