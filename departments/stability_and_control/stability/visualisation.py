import control as ct
import aerosandbox as asb
import aerosandbox.numpy as np

from aircraft_models import rot_wing

MODEL_SCALE = 2

ac = rot_wing

def show_3D_longitudinal(response: ct.TimeResponseData, end_time=5):
    end_index = np.argmin(np.abs(response.time - end_time))
    V = ac.data.cruise_velocity
    dyn = asb.DynamicsPointMass3DSpeedGammaTrack(
        mass_props=ac.mass_props,
        speed=V + response.states[0][:end_index],
        alpha=response.states[1][:end_index],
        gamma=response.states[2][:end_index] - response.states[1][:end_index],
    )
    dyn.time = response.time[:end_index]
    dyn.x_e = dyn.time * dyn.speed * np.cos(dyn.gamma)
    dyn.z_e = dyn.time * dyn.speed * np.sin(dyn.gamma)
    dyn.draw(ac.parametric, scale_vehicle_model=MODEL_SCALE)

def show_3D_lateral(response: ct.TimeResponseData, end_time=5):
    end_index = np.argmin(np.abs(response.time - end_time))
    V = ac.data.cruise_velocity
    dyn = asb.DynamicsPointMass3DSpeedGammaTrack(
        mass_props=ac.mass_props,
        speed=V,
        beta=response.states[0][:end_index],
        track=response.states[0][:end_index],
        bank=response.states[1][:end_index],
    )
    dyn.time = response.time[:end_index]
    dyn.x_e = dyn.time * dyn.speed
    dyn.draw(ac.parametric, scale_vehicle_model=MODEL_SCALE)

