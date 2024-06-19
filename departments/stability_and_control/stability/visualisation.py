import control as ct
import aerosandbox as asb
import aerosandbox.numpy as np

from aircraft_models import rot_wing

MODEL_SCALE = 5

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

def show_3D_lateral(response: ct.TimeResponseData, end_time=6):
    import pyvista as pv
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
    # plotter = pv.Plotter()
    plotter: pv.Plo = dyn.draw(
        ac.parametric,
        scale_vehicle_model=MODEL_SCALE,
        n_vehicles_to_draw=8,
        show=False,
        draw_axes=False,
        draw_global_axes=False,
        draw_altitude_drape=False,
        draw_ground_plane=False,
        set_sky_background=False,
        # draw_global_grid=False,
    )
    # plotter.camera.up = (0, 0, 0)
    plotter.camera.Azimuth(180)
    # plotter.camera.Elevation(00)
    plotter.show(interactive=False, full_screen=True)
    plotter.screenshot("roll3D", transparent_background=True, scale=5)

