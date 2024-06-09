import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import matplotlib
from casadi import *
import random as random
from aircraft_models.rotating_wing import ac
from data.concept_parameters.aircraft import AC
from aircraft_models.trans_wing import generate_airplane
from departments.aerodynamics.aero import Aero


class TransitionAnim:

    def __init__(self, alpha: float = 45, beta: float = 35) -> None:

        self.eta = np.deg2rad(alpha)
        self.beta = np.deg2rad(beta)

        self.C_z = np.array([[np.cos(self.eta), -np.sin(self.eta), 0],
                             [np.sin(self.eta),
                              np.cos(self.eta), 0], [0, 0, 1]])

        self.C_y = np.array([
            [np.cos(np.pi / 2 - self.beta), 0,
             np.sin(np.pi / 2 - self.beta)], [0, 1, 0],
            [-np.sin(np.pi / 2 - self.beta), 0,
             np.cos(np.pi / 2 - self.beta)]
        ])

        self.axis = self.C_z @ self.C_y @ np.array([[0], [0], [1]])

        # Propusion system parameters
        # Propulsion system location
        self.r_prop = [
            np.array([[0.1], [-0.5], [0]]),
            np.array([[0.1], [0.1], [0]])
        ]
        # Thrust vector in local coordinates
        self.v_prop = [
            np.array([[0.2], [0], [0]]),
            np.array([[0.2], [0], [0]])
        ]
        self.eta = []
        self.lmbd = []
        self.gamma = []

    def set_C_axis(self, q) -> None:

        q = np.deg2rad(q)
        self.C_axis = np.cos(q) * np.eye(3, 3) + np.sin(q) * np.array([
            [0, -self.axis[2, 0], self.axis[1, 0]],
            [self.axis[2, 0], 0, -self.axis[0, 0]],
            [-self.axis[1, 0], self.axis[0, 0], 0]
        ]) + (1 - np.cos(q)) * self.axis * self.axis.T

    def init_animation(self, ) -> None:

        self.tip_le = np.array([[0.1], [-0.75], [0]])
        self.root_le = np.array([[0.2], [0.25], [0]])
        self.root_te = np.array([[-0.1], [0.25], [0]])
        self.tip_te = np.array([[-0.1], [-0.75], [0]])

        Xc, Yc, Zc = self.cylinder_data(0, .35, 0.5, 1, 0.1)

        self.animation_ax.plot_surface(Zc,
                                       Yc,
                                       Xc,
                                       alpha=1,
                                       rstride=10,
                                       cstride=5,
                                       color="blue")

        self.ax = self.animation_ax.quiver(0,
                                           0,
                                           0,
                                           self.axis[0, 0],
                                           self.axis[1, 0],
                                           self.axis[2, 0],
                                           arrow_length_ratio=0.1,
                                           color='red')

        self.line1 = self.animation_ax.plot(
            [self.tip_le[0], self.root_le[0]],
            [self.tip_le[1], self.root_le[1]],
            zs=[self.tip_le[2], self.root_le[2]],
            c='purple')
        self.line2 = self.animation_ax.plot(
            [self.root_le[0], self.root_te[0]],
            [self.root_le[1], self.root_te[1]],
            zs=[self.root_le[2], self.root_te[2]],
            c='purple')
        self.line3 = self.animation_ax.plot(
            [self.root_te[0], self.tip_te[0]],
            [self.root_te[1], self.tip_te[1]],
            zs=[self.root_te[2], self.tip_te[2]],
            c='purple')
        self.line4 = self.animation_ax.plot(
            [self.tip_le[0], self.tip_te[0]], [self.tip_le[1], self.tip_te[1]],
            zs=[self.tip_le[2], self.tip_te[2]],
            c='purple')

        self.vectors = []

        for r, v in zip(self.r_prop, self.v_prop):
            tmp_v = r + v
            self.vectors.append(
                self.animation_ax.quiver(r[0, 0],
                                         r[1, 0],
                                         r[2, 0],
                                         v[0, 0],
                                         v[1, 0],
                                         v[2, 0],
                                         arrow_length_ratio=0.3,
                                         color='green'))

        self.x_axis = self.animation_ax.plot([0, 1], [0, 0],
                                             zs=[0, 0],
                                             c='blue')
        self.y_axis = self.animation_ax.plot([0, 0], [0, 1],
                                             zs=[0, 0],
                                             c='blue')
        self.z_axis = self.animation_ax.plot([0, 0], [0, 0],
                                             zs=[0, 1],
                                             c='blue')

        self.x_axis = self.animation_ax.plot([0, 1], [0, 0],
                                             zs=[0, 0],
                                             c='blue')
        self.y_axis = self.animation_ax.plot([0, 0], [0, 1],
                                             zs=[0, 0],
                                             c='blue')
        self.z_axis = self.animation_ax.plot([0, 0], [0, 0],
                                             zs=[0, 1],
                                             c='blue')

    def cylinder_data(self, center_x, center_y, center_z, height_z, radius):

        z = np.linspace(0, height_z, 50) - center_z
        theta = np.linspace(0, 2 * np.pi, 50)
        theta_grid, z_grid = np.meshgrid(theta, z)
        x_grid = radius * np.cos(theta_grid) + center_x
        y_grid = radius * np.sin(theta_grid) + center_y
        return x_grid, y_grid, z_grid

    def draw_wing(self, i) -> None:

        self.line1.pop(0).remove()
        self.line2.pop(0).remove()
        self.line3.pop(0).remove()
        self.line4.pop(0).remove()

        self.tip_le = self.C_axis @ self.tip_le
        self.root_le = self.C_axis @ self.root_le
        self.root_te = self.C_axis @ self.root_te
        self.tip_te = self.C_axis @ self.tip_te

        self.line1 = self.animation_ax.plot(
            [self.tip_le[0], self.root_le[0]],
            [self.tip_le[1], self.root_le[1]],
            zs=[self.tip_le[2], self.root_le[2]],
            c='purple')
        self.line2 = self.animation_ax.plot(
            [self.root_le[0], self.root_te[0]],
            [self.root_le[1], self.root_te[1]],
            zs=[self.root_le[2], self.root_te[2]],
            c='purple')
        self.line3 = self.animation_ax.plot(
            [self.root_te[0], self.tip_te[0]],
            [self.root_te[1], self.tip_te[1]],
            zs=[self.root_te[2], self.tip_te[2]],
            c='purple')
        self.line4 = self.animation_ax.plot(
            [self.tip_le[0], self.tip_te[0]], [self.tip_le[1], self.tip_te[1]],
            zs=[self.tip_le[2], self.tip_te[2]],
            c='purple')

        eff = []

        for r, v in zip(self.r_prop, self.v_prop):
            tmp_v = r + v
            self.vectors.pop(0).remove()

            v = np.linalg.matrix_power(self.C_axis, i) @ v
            r = np.linalg.matrix_power(self.C_axis, i) @ r

            # Print Thrust lifting efficiency
            eff.append(np.squeeze(v.T @ np.array([[0], [0], [1]])))
            #Plot vector
            self.vectors.append(
                self.animation_ax.quiver(r[0, 0],
                                         r[1, 0],
                                         r[2, 0],
                                         v[0, 0],
                                         v[1, 0],
                                         v[2, 0],
                                         arrow_length_ratio=0.3,
                                         color='green'))

        eff = np.array(eff)
        eff = int(
            np.sum(eff) / np.sum(np.linalg.norm(self.v_prop, axis=1)) *
            100)  #TODO: Test this
        #print(f"Lifting efficiency: {eff}%")

        v_sweep = self.tip_le - self.root_le
        v_sweep[2, 0] = 0
        v_dehidral = 0
        v_aoa = self.tip_le - self.tip_te
        v_aoa[1, 0] = 0
        v_dehidral = np.cross((self.root_te - self.root_le).T,
                              (self.tip_le - self.root_le).T)
        v_dehidral[0, 0] = 0

        tmp_lmbd = float(
            np.arccos(v_sweep.T @ np.array([[0], [-1], [0]]) /
                      (np.linalg.norm(v_sweep))))
        tmp_alpha = float(
            np.arccos(v_aoa.T @ np.array([[1], [0], [0]]) /
                      (np.linalg.norm(v_aoa))))
        tmp_gamma = float(
            np.arccos(v_dehidral @ np.array([[0], [0], [1]]) /
                      (np.linalg.norm(v_dehidral))))
        print(f"Sweep: {np.rad2deg(tmp_lmbd)}%")
        print(f"AoA: {np.rad2deg(tmp_alpha)}%")
        print(f"Dehidral: {np.rad2deg(tmp_gamma)}%")
        self.eta.append(tmp_alpha)
        self.lmbd.append(tmp_lmbd)
        self.gamma.append(tmp_gamma)

        self.ax.set_aspect('equal')

    def plot_lift(self, show:bool=False) -> None:
        S = 14
        rho = 1.225
        airplane = generate_airplane(0)
        airplane = AC(
            name=ac.full_name,
            data=ac,
            parametric=airplane,
        )
        aero = Aero(airplane)

        cl = []
        for alpha in self.eta:
            cl.append(aero.CL(np.rad2deg(alpha)))
        print(cl)
        max_lift = 1 / 2 * np.cos(np.array(self.lmbd))**2 * np.array(max(cl)) * S * np.cos(self.gamma) * rho * np.cos(
                self.eta)
        norm_lift = 1 / 2 * np.cos(np.array(self.lmbd))**2 * np.array(cl) * S * np.cos(self.gamma) * rho * np.cos(
                self.eta)
        self.norm_lift_real = np.where(np.arange(len(self.eta)) / len(self.eta) > 0.66, 0, norm_lift)
        self.max_lift_real = np.where(np.arange(len(self.eta)) / len(self.eta) > 0.66, 0, max_lift)
        if show:
            plt.plot(np.arange(len(self.eta)) / len(self.eta), norm_lift)
            plt.plot(np.arange(len(self.eta)) / len(self.eta), self.norm_lift_real)
            plt.show()

    def conversion_corridor(self):
        p_max = 50000
        MTOW = 1500 * 9.81
        S = 14
        rho = 1.225
        airplane = generate_airplane(0)
        airplane = AC(
            name=ac.full_name,
            data=ac,
            parametric=airplane,
        )
        aero = Aero(airplane)

        self.eta = np.flip(self.eta)
        self.gamma = np.flip(self.gamma)
        self.lmbd = np.flip(self.lmbd)

        cl = []
        cd = []

        for alpha in self.eta:
            cl.append(aero.CL(alpha))
            cd.append(aero.CD(alpha))
        print(aero.aero_data.keys())
        #L = 1 / 2 * np.cos(np.array(self.lmbd))**2 * np.array(cl) * S * np.cos(
        #    self.gamma) * rho
        L = np.flip(self.norm_lift_real)
        v_stall = np.sqrt(MTOW / L)

        v_steady = np.where(np.arange(len(self.eta)) / len(self.eta) < 0.33, 0, np.sqrt(MTOW / (L + 0.5 * np.array(cd) * rho * S * np.tan(self.eta))))

        v_stall = np.sqrt(MTOW / (np.flip(self.max_lift_real) + 0.5 * np.array(cd) * rho * S * np.tan(self.eta)))

        v_min_cl_max = np.sqrt((MTOW - 3.1 * MTOW * np.sin(self.eta)) / np.flip(self.max_lift_real))
        v_min = np.sqrt((MTOW - 3.1 * MTOW * np.sin(self.eta)) / L)

        v_max = (p_max*np.cos(self.eta)/(0.5*np.array(cd)*rho*S))**(1/3)

        #plt.plot(v_stall, np.rad2deg(self.eta), label='CL_max')
        plt.plot(v_steady, np.rad2deg(self.eta), label = 'steady')
        plt.plot(v_min, np.rad2deg(self.eta), label='v_min with max power (unsteady)')
        plt.plot(v_min_cl_max, np.rad2deg(self.eta), label='v_min with max power max cl (unsteady)')
        plt.plot(v_max, np.rad2deg(self.eta), label='v_max with max power (unsteady)')
        plt.xlabel('v [m/s]')
        plt.ylabel('n [deg]')
        plt.xlim(0, 250)
        plt.legend()
        plt.show()

    def run_animation(self,
                      q: float = -110,
                      n: int = 500,
                      save_anim: bool = False) -> None:

        dq = q / n

        self.set_C_axis(dq)

        self.animation_fig = plt.figure()
        self.animation_ax = self.animation_fig.add_subplot(projection='3d')
        self.animation_ax.set_aspect('equal')

        ani = animation.FuncAnimation(self.animation_fig,
                                      self.draw_wing,
                                      frames=n,
                                      interval=1,
                                      repeat=False,
                                      init_func=self.init_animation)
        #ani.save(filename="./rotation.gif", writer="pillow", dpi=300)

        self.tip_le = np.array([[0.1], [-0.75], [0]])
        self.root_le = np.array([[0.1], [0.25], [0]])
        self.root_te = np.array([[-0.1], [0.25], [0]])
        self.tip_te = np.array([[-0.1], [-0.75], [0]])

        self.animation_ax.set_xlabel('X')
        self.animation_ax.set_ylabel('Y')
        self.animation_ax.set_zlabel('Z')

        self.animation_ax.set_xlim(-1, 1)
        self.animation_ax.set_ylim(-1, 1)
        self.animation_ax.set_zlim(-1, 1)

        plt.show()



if __name__ == '__main__':

    sim = TransitionAnim()
    sim.run_animation()
    sim.plot_lift()
    sim.conversion_corridor()
