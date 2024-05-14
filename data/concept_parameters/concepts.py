from data.concept_parameters.aircraft import Aircraft

concept_C2_1 = Aircraft(
    name="Concept C2.1 (Pterodynamics)",
    motor_prop_count=4,
    propeller_radius=1.25,
    propeller_blade_number=4,
    aspect_ratio=14/2,
    wing_area=14*2,
    fuselage_length=8,
    fuselage_maximum_section_perimeter=2.5,
    estimated_CD0=0.03,
)