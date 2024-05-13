from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.mission_profile import typical_wingless_mission_profile

test_from_excel = Aircraft(
    name='test_from_excel',
    propeller_radius=0.5,  # m
    propeller_rotation_speed=200,  # rotations/s
    tension_coefficient=0.04,
)

sizing_example_powered_lift = Aircraft(
    name='eVTOL sizing example from paper (powered lift)',
    payload_mass=400,  # kg
    n_pax=4,
    figure_of_merit=0.75,
    computed_drag_coefficient=0.04353,
    propulsion_efficiency=0.85,
    prop_count=4,
    motor_power_margin=0.5,
    SoC_min=0.2,
    battery_energy_density=0.25,  # kWh/kg
    battery_system_efficiency=0.85,
    aerofoil_lift_coefficient=1.5,
    aspect_ratio=7.0,
    oswald_efficiency_factor=0.85,
    fuselage_length=5.0,  # m
    fuselage_maximum_section_perimeter=4.7,  # m
    mission_profile=typical_wingless_mission_profile)
