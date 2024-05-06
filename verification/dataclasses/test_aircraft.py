import pytest
from data.concept_parameters.aircraft import Aircraft

def test_aircraft_with_positive_parameters():
    aircraft = Aircraft(
        propeller_radius=1.0,
        propeller_rotation_speed=1.0,
        tension_coefficient=0.5
    )
    assert aircraft.propeller_radius == 1.0
    assert aircraft.propeller_rotation_speed == 1.0
    assert aircraft.tension_coefficient == 0.5

def test_aircraft_with_zero_parameters_raises_error():
    with pytest.raises(ValueError):
        Aircraft(
            propeller_radius=0,
            propeller_rotation_speed=0,
            tension_coefficient=0
        )

def test_aircraft_with_negative_parameters_raises_error():
    with pytest.raises(ValueError):
        Aircraft(
            propeller_radius=-1.0,
            propeller_rotation_speed=-1.0,
            tension_coefficient=-0.5
        )

def test_aircraft_with_efficiency_greater_than_one_raises_error():
    with pytest.raises(ValueError):
        Aircraft(
            propeller_radius=1.0,
            propeller_rotation_speed=1.0,
            tension_coefficient=1.5,
            electric_propulsion_efficiency=1.1
        )

def test_aircraft_with_tension_coefficient_greater_than_one_raises_error():
    with pytest.raises(ValueError):
        Aircraft(
            propeller_radius=1.0,
            propeller_rotation_speed=1.0,
            tension_coefficient=1.1,
            electric_propulsion_efficiency=0.5
        )