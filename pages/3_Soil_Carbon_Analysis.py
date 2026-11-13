from __future__ import annotations
from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px
from farmcarbon.runtime import build_runtime
from farmcarbon.services.soil_carbon_service import calculate_soc_stock, compare_samples

st.set_page_config(page_title="Soil Carbon Analysis | FarmCarbon MRV",layout="wide")
from farmcarbon.components.theme import apply_theme
apply_theme()

@st.cache_resource
def runtime(): return build_runtime()
rt=runtime(); repo=rt["repo"]
st.title("Soil Organic Carbon Analysis")
st.caption("Measurement-led SOC stock calculations and comparable baseline/follow-up analysis.")
st.warning("Fixed-depth SOC stock estimates are not certified carbon-credit quantities. Equivalent soil mass adjustment is not implemented.")
farms=repo.list("farms")
if not farms: st.info("Register a farm first."); st.stop()
labels={f"{f['name']} · {f.get('project_identifier') or f['id'][:8]}":f for f in farms}
selected=st.selectbox("Farm",list(labels)); farm=labels[selected]

with st.expander("Add soil sample",expanded=not bool(repo.list("soil_samples",farm_id=farm["id"]))):
    with st.form("soil_sample_form",clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        zone=c1.text_input("Sampling zone ID *",value="ZONE-01")
        sample_id=c2.text_input("Sample ID *")
        period=c3.selectbox("Measurement period",["Baseline","Monitoring"])
        sample_date=c1.date_input("Sampling date",value=date.today())
        method=c2.selectbox("Laboratory / measurement method",["Walkley-Black","Dry combustion","Loss on ignition","Other / documented method"])
        lab_ref=c3.text_input("Laboratory reference")
        depth_top=c1.number_input("Sampling depth start (cm)",min_value=0.0,value=0.0,step=1.0)
        depth_bottom=c2.number_input("Sampling depth end (cm)",min_value=0.1,value=30.0,step=1.0)
        zone_area=c3.number_input("Sampling zone area (ha)",min_value=0.0,value=min(float(farm.get("area_ha") or 0),4.0) if farm.get("area_ha") else 0.0,step=0.1)
        soc=c1.number_input("SOC concentration (g/kg)",min_value=0.0,value=10.0,step=0.1)
        bd=c2.number_input("Bulk density (g/cm³)",min_value=0.01,max_value=3.0,value=1.3,step=0.01)
        coarse=c3.number_input("Coarse fragment fraction (0–1)",min_value=0.0,max_value=0.99,value=0.1,step=0.01)
        lat=c1.number_input("Sampling latitude",min_value=-90.0,max_value=90.0,value=float(farm.get("latitude") or 0),format="%.6f")
        lon=c2.number_input("Sampling longitude",min_value=-180.0,max_value=180.0,value=float(farm.get("longitude") or 0),format="%.6f")
        source=c3.selectbox("Data source mode",["FIELD_LAB","DEMO","UPLOAD"])
        notes=st.text_area("Notes / provenance details")
        lab_file=st.file_uploader("Laboratory report attachment (PDF/CSV/image)",type=["pdf","csv","png","jpg","jpeg","webp"])
        save=st.form_submit_button("Save soil sample",type="primary")
    if save:
        try:
            if not zone.strip() or not sample_id.strip(): raise ValueError("Sampling zone ID and sample ID are required")
            if depth_bottom<=depth_top: raise ValueError("Sampling depth end must be greater than depth start")
            depth=depth_bottom-depth_top
            stock=calculate_soc_stock(soc,bd,coarse,depth)
            attachment=None
            if lab_file:
                evidence=rt["practice_service"].save_upload(lab_file,farm["id"],None)
                attachment=evidence["stored_path"]
            repo.create("soil_samples",{"farm_id":farm["id"],"zone_id":zone.strip(),"zone_area_ha":zone_area or None,
                "sample_identifier":sample_id.strip(),"sample_date":sample_date.isoformat(),"latitude":lat,"longitude":lon,
                "depth_top_cm":depth_top,"depth_bottom_cm":depth_bottom,"soc_g_kg":soc,"bulk_density_g_cm3":bd,
                "coarse_fragment_fraction":coarse,"measurement_method":method,"laboratory_reference":lab_ref,
                "laboratory_attachment":attachment,"calculated_soc_stock_mg_c_ha":stock,"measurement_period":period,
                "source_mode":source,"notes":notes})
            repo.audit(farm["id"],"soil_sample",sample_id,"CREATE",f"{period} soil sample recorded","USER")
            st.success(f"Sample saved. Fixed-depth SOC stock: {stock:.3f} Mg C/ha."); st.rerun()
        except Exception as exc: st.error(str(exc))

samples=sorted(repo.list("soil_samples",farm_id=farm["id"]),key=lambda x:x.get("sample_date",""))
st.subheader("Recorded soil samples")
if samples:
    df=pd.DataFrame(samples)
    show=["sample_identifier","zone_id","sample_date","measurement_period","depth_top_cm","depth_bottom_cm","soc_g_kg","bulk_density_g_cm3","coarse_fragment_fraction","calculated_soc_stock_mg_c_ha","measurement_method","source_mode"]
    st.dataframe(df[[c for c in show if c in df.columns]],use_container_width=True,hide_index=True)
    st.download_button("Download soil samples CSV",df.to_csv(index=False),file_name=f"{farm['id']}_soil_samples.csv",mime="text/csv")
    comparison=compare_samples(samples,farm.get("area_ha"))
    st.subheader("Baseline vs follow-up comparison")
    if comparison["comparisons"]:
        comp=pd.DataFrame(comparison["comparisons"])
        st.dataframe(comp,use_container_width=True,hide_index=True)
        totals=st.columns(3)
        totals[0].metric("Comparable zones",len(comp))
        totals[1].metric("Carbon stock change",f"{comparison['total_carbon_stock_change_mg_c']:.3f} Mg C" if comparison["total_carbon_stock_change_mg_c"] is not None else "—")
        totals[2].metric("CO₂e equivalent",f"{comparison['total_co2e_change_mg']:.3f} Mg CO₂e" if comparison["total_co2e_change_mg"] is not None else "—")
        chart_data=comp.melt(id_vars="zone_id",value_vars=["baseline_stock_mg_c_ha","followup_stock_mg_c_ha"],var_name="Period",value_name="SOC stock (Mg C/ha)")
        fig=px.bar(chart_data,x="zone_id",y="SOC stock (Mg C/ha)",color="Period",barmode="group",title="SOC stock by sampling zone")
        st.plotly_chart(fig,use_container_width=True)
    for warning in comparison["warnings"]: st.warning(warning)
else:
    st.info("No soil samples recorded for this farm. Add a baseline sample and a compatible follow-up sample to calculate stock change.")
