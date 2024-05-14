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
    estimated_CD0=0.04,  # from Philip
    propulsion_efficiency=0.85,
    motor_prop_count=4,
    motor_power_margin=0.5,
    SoC_min=0.2,
    battery_energy_density=0.275,  # kWh/kg
    battery_system_efficiency=0.85,
    aerofoil_lift_coefficient=1.5,
    aspect_ratio=7.0,
    oswald_efficiency_factor=0.85,
    fuselage_length=7.0,  # m
    fuselage_maximum_section_perimeter=3,  # m
    mission_profile=typical_wingless_mission_profile,
    # from here on, the values are not from the paper
    wing_area=10.0,  # m^2
    design_load_factor=1.5,
    S_th=0.5,  # m^2
    AR_th=4.0,
    t_rh=0.1,  # m
    S_tv=0.5,  # m^2
    AR_tv=4.0,
    t_rv=0.1,  # m
    lambda_quart_tv=0.0,  # rad
    l_lg=0.5,  # m
    eta_lg=1.5,
    propeller_radius=1.25,  # m
    propeller_blade_number=2,
)
