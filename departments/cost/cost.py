from aerosandbox.library.costs import modified_DAPCA_IV_production_cost_analysis, \
    electric_aircraft_direct_operating_cost_analysis

from data.concept_parameters.aircraft import Aircraft


def production_cost_per_ac(aircraft: Aircraft, n_ac: int, engine_cost: float = 20_000, avionics_cost: float = 100_000) -> float:
    """
    Calculate the production cost of an aircraft
    :param aircraft: Aircraft object
    :param n_ac: Number of aircraft to be produced
    :param engine_cost: Estimated cost of the engine
    :param avionics_cost: Estimated cost of the avionics
    :return: Production cost per aircraft
    """
    production_costs = modified_DAPCA_IV_production_cost_analysis(
        design_empty_weight=aircraft.total_mass - aircraft.payload_mass,
        design_maximum_airspeed=aircraft.cruise_velocity,
        n_airplanes_produced=n_ac,
        n_engines_per_aircraft=aircraft.motor_prop_count,
        cost_per_engine=engine_cost,
        cost_avionics_per_airplane=avionics_cost,
        n_pax=aircraft.n_pax,
        primary_structure_material="carbon_fiber",  # "aluminum" - "carbon_fiber" - "fiberglass" - "steel" - "titanium"
        per_passenger_cost_model="regional_transport",  # "regional_transport" or "general_aviation"
    )
    production_costs_single_ac = {k: v / n_ac for k, v in production_costs.items()}
    return production_costs_single_ac['total']


def operating_cost_per_pax_mile(aircraft: Aircraft, production_cost_single_ac: float) -> float:
    op_costs = electric_aircraft_direct_operating_cost_analysis(
        production_cost_per_airframe=production_cost_single_ac,
        nominal_cruise_airspeed=aircraft.mission_profile.CRUISE.horizontal_speed,
        nominal_mission_range=aircraft.range,
        battery_capacity=aircraft.mission_profile.energy,
        num_passengers_nominal=aircraft.n_pax,
        num_crew=0,
        battery_fraction_used_on_nominal_mission=1 - aircraft.SoC_min,
        typical_passenger_utilization=0.75,
        flight_hours_per_year=15 * 365,
        airframe_lifetime_years=10,
        airframe_eol_resale_value_fraction=0.6,
        electricity_cost_per_kWh=0.145,
        ascent_time=aircraft.mission_profile.TAKEOFF.duration + aircraft.mission_profile.HOVER_CLIMB.duration,
        descent_time=aircraft.mission_profile.DESCENT.duration + aircraft.mission_profile.LANDING.duration,
    )
    return op_costs['total']


if __name__ == '__main__':
    ac = Aircraft.load('C2.1', directory='end_of_trade-off_concepts')
    n_planes = 100
    prod_cost = production_cost_per_ac(ac, n_planes)
    op_cost = operating_cost_per_pax_mile(ac, prod_cost)
    print(f'Production cost: {prod_cost:.2f} USD/aircraft')
    print(f'Operating cost:  {op_cost:.2f} USD/passenger-mile')
