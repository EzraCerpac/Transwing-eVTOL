from data.concept_parameters.aircraft import Aircraft

concept_C1_5 = Aircraft(
    name="Concept C1.5 (Fixed Wing)",
    motor_prop_count=4,
    propeller_radius=1.25,
    propeller_blade_number=4,
    aspect_ratio=8 / 1.5,
    wing_area=8 * 1.5,
    fuselage_length=4,
    fuselage_maximum_section_perimeter=3,
    estimated_CD0=0.04,
)

# concept_C1_7 = Aircraft(
#     # modeled as a 3 prop aircraft, but model doesn't account for this design yet
#     name="Concept C1.7 (Prop in Wing)",
#     motor_prop_count=3,
#     propeller_radius=1.25,
#     propeller_blade_number=4,
#     aspect_ratio=8 / 1.7,
#     wing_area=8 * 1.7,
#     fuselage_length=4,
#     fuselage_maximum_section_perimeter=3,
#     estimated_CD0=0.04,
# )

concept_C2_1 = Aircraft(
    name="Concept C2.1 (Pterodynamics)",
    motor_prop_count=4,
    propeller_radius=1.25,
    propeller_blade_number=4,
    aspect_ratio=14 / 2,
    wing_area=14 * 2,
    fuselage_length=8,
    fuselage_maximum_section_perimeter=2.5,
    estimated_CD0=0.03,
)

concept_C2_6 = Aircraft(
    name="Concept C2.6 (Folding Wing)",
    motor_prop_count=6,
    propeller_radius=0.75,
    propeller_blade_number=4,
    aspect_ratio=14 / 2,
    wing_area=14 * 2,
    fuselage_length=4,
    fuselage_maximum_section_perimeter=2.5,
    estimated_CD0=0.035,
)

concept_C2_10 = Aircraft(
    # modeled as a 3 prop aircraft, but model doesn't account for this design yet
    name="Concept C2.10 (Tomaso)",
    motor_prop_count=3,
    propeller_radius=1,
    propeller_blade_number=2,
    aspect_ratio=8.5 / 2.5,
    wing_area=8.5 * 2.5,
    fuselage_length=8.5,
    fuselage_maximum_section_perimeter=2.5,
    estimated_CD0=0.04,
)