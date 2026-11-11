import pytest
from farmcarbon.services.soil_carbon_service import calculate_soc_stock, compare_samples


def test_soc_stock_example():
    assert calculate_soc_stock(10, 1.3, 0.10, 30) == pytest.approx(35.1)

@pytest.mark.parametrize("values", [(-1,1.3,0.1,30),(10,0,0.1,30),(10,1.3,1,30),(10,1.3,0.1,0)])
def test_invalid_inputs(values):
    with pytest.raises(ValueError): calculate_soc_stock(*values)


def test_comparison_requires_matching_zone_depth_and_method():
    samples=[
      {"id":"b","farm_id":"f","zone_id":"z","measurement_period":"Baseline","sample_date":"2024-01-01","source_mode":"LAB","depth_top_cm":0,"depth_bottom_cm":30,"measurement_method":"A","calculated_soc_stock_mg_c_ha":35,"zone_area_ha":2,"bulk_density_g_cm3":1.3},
      {"id":"m","farm_id":"f","zone_id":"z","measurement_period":"Monitoring","sample_date":"2025-01-01","source_mode":"LAB","depth_top_cm":0,"depth_bottom_cm":30,"measurement_method":"A","calculated_soc_stock_mg_c_ha":36,"zone_area_ha":2,"bulk_density_g_cm3":1.3},
      {"id":"bad","farm_id":"f","zone_id":"z","measurement_period":"Monitoring","depth_top_cm":0,"depth_bottom_cm":20,"measurement_method":"A","calculated_soc_stock_mg_c_ha":99,"bulk_density_g_cm3":1.3},
    ]
    result=compare_samples(samples)
    assert len(result["comparisons"])==1
    assert result["comparisons"][0]["carbon_stock_change_mg_c"]==pytest.approx(2)
