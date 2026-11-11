from farmcarbon.services.report_service import generate_farm_pdf


def test_pdf_report_is_generated_without_soil_samples():
    farm={"name":"R&D Demo Farm","project_identifier":"FC-<TEST>","area_ha":1.2,"latitude":16.5,"longitude":80.6,
          "boundary_geojson":{"type":"Polygon","coordinates":[[[80,16],[80.01,16],[80.01,16.01],[80,16.01],[80,16]]]}}
    assessment={"status":"Monitoring Active","completeness_score":50,"warnings":["Example <warning> & limitation"]}
    pdf=generate_farm_pdf(farm,[],[],[],[],assessment)
    assert pdf.startswith(b"%PDF-")
    assert len(pdf)>1000
