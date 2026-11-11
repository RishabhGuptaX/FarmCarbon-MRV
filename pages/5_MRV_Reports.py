from __future__ import annotations
import json
import streamlit as st
import pandas as pd
from farmcarbon.runtime import build_runtime
from farmcarbon.services.report_service import generate_farm_pdf

st.set_page_config(page_title="MRV Reports | FarmCarbon MRV",layout="wide")
@st.cache_resource
def runtime(): return build_runtime()
rt=runtime(); repo=rt["repo"]
st.title("MRV Reports & Review")
st.caption("Assess project completeness, inspect warnings and generate a farm-level monitoring report.")
farms=repo.list("farms")
if not farms: st.info("Register a farm to start an MRV assessment."); st.stop()
labels={f"{f['name']} · {f.get('project_identifier') or f['id'][:8]}":f for f in farms}
selected=st.selectbox("Farm",list(labels)); farm=labels[selected]
assessment=rt["mrv_service"].assess(farm)
col1,col2=st.columns([1,2])
col1.metric("Completeness indicator",f"{assessment['completeness_score']}%",help="Project-management checklist completion only. Not a scientific confidence score.")
col2.metric("Current MRV status",assessment["status"])
st.progress(assessment["completeness_score"]/100)
st.subheader("MRV completeness checklist")
for label,ok,detail in assessment["checks"]:
    (st.success if ok else st.warning)(f"{'Complete' if ok else 'Outstanding'} — **{label}** · {detail}")

st.subheader("Data-quality warnings")
if assessment["warnings"]:
    for warning in assessment["warnings"]: st.warning(warning)
else: st.success("No automated data-quality warnings were raised.")

st.subheader("Reviewer action")
st.caption("A completed review requires a named reviewer and an explicit action. Completing forms or reaching 100% completeness does not automatically verify a project.")
with st.form("review_form"):
    reviewer=st.text_input("Reviewer name")
    notes=st.text_area("Reviewer notes / decision rationale")
    acknowledge=st.checkbox("I have reviewed the available evidence and understand the listed limitations.")
    submit_review=st.form_submit_button("Record review completed",type="primary")
if submit_review:
    try:
        if not acknowledge: raise ValueError("Please confirm that you reviewed the evidence and limitations.")
        review=rt["mrv_service"].record_review(farm["id"],reviewer,notes)
        repo.audit(farm["id"],"mrv_review",review["id"],"REVIEW_COMPLETED",f"Review completed by {reviewer}")
        st.success("Review action recorded with reviewer details. This is not third-party verification or certification.")
        st.rerun()
    except Exception as exc: st.error(str(exc))

reviews=repo.list("mrv_reviews",farm_id=farm["id"])
if reviews:
    st.subheader("Review history")
    st.dataframe(pd.DataFrame(reviews),use_container_width=True,hide_index=True)

st.divider(); st.subheader("Generate report")
soils=repo.list("soil_samples",farm_id=farm["id"])
observations=repo.list("satellite_observations",farm_id=farm["id"])
practices=repo.list("practices",farm_id=farm["id"])
evidence=repo.list("evidence_files",farm_id=farm["id"])
pdf=generate_farm_pdf(farm,soils,observations,practices,evidence,assessment)
st.download_button("Download farm MRV report (PDF)",pdf,file_name=f"FarmCarbon_MRV_{farm.get('project_identifier') or farm['id']}.pdf",mime="application/pdf",type="primary")

c1,c2=st.columns(2)
all_rows=[]
for kind,records in (("soil_samples",soils),("satellite_observations",observations),("practices",practices),("evidence_files",evidence),("mrv_reviews",reviews)):
    for row in records: all_rows.append({"record_type":kind,**row})
c1.download_button("Download farm records (CSV)",pd.DataFrame(all_rows).to_csv(index=False) if all_rows else "record_type\n",file_name=f"{farm['id']}_mrv_data.csv",mime="text/csv")
if farm.get("boundary_geojson"):
    boundary={"type":"FeatureCollection","features":[{"type":"Feature","properties":{"farm_name":farm["name"],"project_identifier":farm.get("project_identifier")},"geometry":farm["boundary_geojson"]}]}
    c2.download_button("Download farm boundary (GeoJSON)",json.dumps(boundary,indent=2),file_name=f"{farm['id']}_boundary.geojson",mime="application/geo+json")
else: c2.caption("No GeoJSON boundary available for export.")
