from data.concept_parameters.aircraft import Aircraft
from data.concept_parameters.aircraft_components import Fuselage, Wing

concept_C1_5 = Aircraft(
    name="Concept C1.5 (Fixed Wing)",
    motor_prop_count=4,
    motor_wing_count=0,
    propeller_radius=1.25,
    propeller_blade_number=4,
    wing=Wing(
        area=20,
        span=12,
    ),
    fuselage=Fuselage(
        length=4,
        maximum_section_perimeter=3,
    ),
    estimated_CD0=0.04,
    sref = 25,
    TA = 400


)

concept_C2_1 = Aircraft(
    name="Concept C2.1 (Pterodynamics)",
    motor_prop_count=4,
    motor_wing_count=4,
    propeller_radius=1.25,
    propeller_blade_number=4,
    wing=Wing(
        area=20,
        span=14,
    ),
    fuselage=Fuselage(
        length=8,
        maximum_section_perimeter=2.5,
    ),
    estimated_CD0=0.03,
    sref = 12.5,
    TA = 400
)

concept_C2_6 = Aircraft(
    name="Concept C2.6 (Folding Wing)",
    motor_prop_count=6,
    motor_wing_count=4,
    propeller_radius=0.75,
    propeller_blade_number=4,
    wing=Wing(
        area=20,
        span=10,
    ),
    fuselage=Fuselage(
        length=4,
        maximum_section_perimeter=2.5,
    ),
    estimated_CD0=0.035,
    sref = 25,
    TA = 400
)

concept_C2_10 = Aircraft(
    # modeled as a 3 prop aircraft, but model doesn't account for this design yet
    name="Concept C2.10 (Tomaso)",
    motor_prop_count=3,
    motor_wing_count=0,
    propeller_radius=1,
    propeller_blade_number=2,
    wing=Wing(
        area=20,
        span=8,
    ),
    fuselage=Fuselage(
        length=8.5,
        maximum_section_perimeter=2.5,
    ),
    estimated_CD0=0.04,
    sref = 20,
    TA = 400
)
