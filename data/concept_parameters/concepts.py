from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.aircraft_components import Fuselage, Wing

concept_C1_5 = Aircraft(id='C1.5',
                        name="Winged Rotorcraft",
                        motor_prop_count=4,
                        motor_wing_count=0,
                        propeller_radius=1,
                        propeller_blade_number=4,
                        hinge_location=0.66,
                        wing=Wing(
                            area=20,
                            span=12,
                        ),
                        fuselage=Fuselage(
                            length=4,
                            maximum_section_perimeter=1.5,
                        ),
                        estimated_CD0=0.04,
                        s_fus=6,
                        TA=400)

concept_C2_1 = Aircraft(id='C2.1',
                        name="Rotating Wing",
                        motor_prop_count=4,
                        motor_wing_count=4,
                        propeller_radius=0.75,
                        propeller_blade_number=4,
                        hinge_location=0.15,
                        wing=Wing(
                            area=20,
                            span=14,
                        ),
                        fuselage=Fuselage(
                            length=8,
                            maximum_section_perimeter=2.5,
                        ),
                        estimated_CD0=0.03,
                        s_fus=12.5,
                        TA=400)

concept_C2_6 = Aircraft(id='C2.6',
                        name="Folding Wing",
                        motor_prop_count=4,
                        motor_wing_count=4,
                        propeller_radius=0.75,
                        propeller_blade_number=5,
                        hinge_location=0.66,
                        wing=Wing(
                            area=20,
                            span=12,
                        ),
                        fuselage=Fuselage(
                            length=4,
                            maximum_section_perimeter=1.5,
                        ),
                        estimated_CD0=0.035,
                        s_fus=6,
                        TA=400)

concept_C2_10 = Aircraft(
    # modeled as a 3 prop aircraft, but model doesn't account for this design yet
    id='C2.10',
    name="Variable Skew Quadplane",
    motor_prop_count=4,
    motor_wing_count=0,
    propeller_radius=1,
    propeller_blade_number=2,
    hinge_location=0,
    wing=Wing(
        area=20,
        span=8,
    ),
    fuselage=Fuselage(
        length=8,
        maximum_section_perimeter=1.5,
    ),
    estimated_CD0=0.04,
    s_fus=12,
    TA=400)

all_concepts = [concept_C1_5, concept_C2_1, concept_C2_6, concept_C2_10]

example_cg_dict = {
    'payload': 0.5,
    'battery': 0.5,
    'fuselage': 0.5,
    'wing': 0.4,
    'horizontal_tail': 1,
    'vertical_tail': 1,
    'landing_gear': 0.5,
    'motors': 0.4,
    'propellers': 0.4,
}
