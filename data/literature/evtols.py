from data.concept_parameters.aircraft import Aircraft
from utility.unit_conversion import convert_float

joby_s4 = Aircraft(  # from https://aviationweek.com/aerospace/advanced-air-mobility/joby-aviation-s4-program
    # MTOW = 2,177 kg/4,800 lbs.
    # Empty weight: 4000 lb (1814 kg)
    name="Joby Aviation S4",
    n_pax=5,
    payload_mass=5 * 100,  # estimation
    cruise_velocity=convert_float(322, 'km/h', 'm/s'),
    cruise_altitude=4572,  # 15,000 ft
    range=convert_float(241, 'km', 'm'),  # 150 miles
    motor_prop_count=6,
    propeller_radius=1.4,  # estimation
    propeller_blade_number=4,
    # wingspan = 11.8 m (39 ft)
    aspect_ratio=11.8 / 2,
    wing_area=11.8 * 2,
    # total length = 6.4 m (21 ft)
    fuselage_length=4,  # estimation
    fuselage_maximum_section_perimeter=1.4,  # estimation
    estimated_CD0=0.04,  # estimation
)
