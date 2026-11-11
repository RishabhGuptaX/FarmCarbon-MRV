import pytest
from farmcarbon.utils.validators import validate_coordinate, validate_date_range
from datetime import date


def test_coordinate_validation():
    assert validate_coordinate(16.5,80.6)==(16.5,80.6)
    with pytest.raises(ValueError): validate_coordinate(100,80)


def test_date_validation():
    validate_date_range(date(2025,1,1),date(2025,1,2))
    with pytest.raises(ValueError): validate_date_range(date(2025,1,2),date(2025,1,1))
