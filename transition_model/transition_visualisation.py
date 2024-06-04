import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import matplotlib
from casadi import *
import random as random
from matplotlib import cm


class TransitionAnim:

    def __init__(self, alpha: float = 45, beta: float = 35) -> None:

        self.alpha = np.deg2rad(alpha)
        self.beta = np.deg2rad(beta)

        self.C_z = np.array([[np.cos(self.alpha), -np.sin(self.alpha), 0],
                             [np.sin(self.alpha),
                              np.cos(self.alpha), 0], [0, 0, 1]])

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

    def set_C_axis(self, q) -> None:

        q = np.deg2rad(q)
        self.C_axis = np.cos(q) * np.eye(3, 3) + np.sin(q) * np.array([
            [0, -self.axis[2, 0], self.axis[1, 0]],
            [self.axis[2, 0], 0, -self.axis[0, 0]],
            [-self.axis[1, 0], self.axis[0, 0], 0]
        ]) + (1 - np.cos(q)) * self.axis * self.axis.T

    def init_animation(self, ) -> None:

        self.A = np.array([[0.1], [-0.75], [0]])
        self.B = np.array([[0.2], [0.25], [0]])
        self.C = np.array([[-0.1], [0.25], [0]])
        self.D = np.array([[-0.1], [-0.75], [0]])

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

        self.line1 = self.animation_ax.plot([self.A[0], self.B[0]],
                                            [self.A[1], self.B[1]],
                                            zs=[self.A[2], self.B[2]],
                                            c='purple')
        self.line2 = self.animation_ax.plot([self.B[0], self.C[0]],
                                            [self.B[1], self.C[1]],
                                            zs=[self.B[2], self.C[2]],
                                            c='purple')
        self.line3 = self.animation_ax.plot([self.C[0], self.D[0]],
                                            [self.C[1], self.D[1]],
                                            zs=[self.C[2], self.D[2]],
                                            c='purple')
        self.line4 = self.animation_ax.plot([self.A[0], self.D[0]],
                                            [self.A[1], self.D[1]],
                                            zs=[self.A[2], self.D[2]],
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

        self.A = self.C_axis @ self.A
        self.B = self.C_axis @ self.B
        self.C = self.C_axis @ self.C
        self.D = self.C_axis @ self.D

        self.line1 = self.animation_ax.plot([self.A[0], self.B[0]],
                                            [self.A[1], self.B[1]],
                                            zs=[self.A[2], self.B[2]],
                                            c='purple')
        self.line2 = self.animation_ax.plot([self.B[0], self.C[0]],
                                            [self.B[1], self.C[1]],
                                            zs=[self.B[2], self.C[2]],
                                            c='purple')
        self.line3 = self.animation_ax.plot([self.C[0], self.D[0]],
                                            [self.C[1], self.D[1]],
                                            zs=[self.C[2], self.D[2]],
                                            c='purple')
        self.line4 = self.animation_ax.plot([self.A[0], self.D[0]],
                                            [self.A[1], self.D[1]],
                                            zs=[self.A[2], self.D[2]],
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
        print(f"Lifting efficiency: {eff}%")

        self.animation_ax.set_aspect('equal')

    def run_animation(self, q: float = -110, n: int = 150, save_anim: bool = False) -> None:

        dq = q / n

        self.set_C_axis(dq)

        self.animation_fig = plt.figure()
        self.animation_ax = self.animation_fig.add_subplot(projection='3d')
        self.animation_ax.set_aspect('equal')

        ani = animation.FuncAnimation(self.animation_fig,
                                      self.draw_wing,
                                      frames=n,
                                      interval=50,
                                      repeat=True,
                                      init_func=self.init_animation)
        ani.save(filename="./rotation.gif", writer="pillow", dpi=300)

        self.A = np.array([[0.1], [-0.75], [0]])
        self.B = np.array([[0.1], [0.25], [0]])
        self.C = np.array([[-0.1], [0.25], [0]])
        self.D = np.array([[-0.1], [-0.75], [0]])

        plt.show()


#TODO: Move finctions into the class

alpha = 0
beta = 0


def random_color():
    np.random.seed()
    rgbl = [np.random.random(), np.random.random(), np.random.random()]
    return tuple(rgbl)


C_z = np.array([[np.cos(alpha), -np.sin(alpha), 0],
                [np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])

C_y = np.array([[np.cos(np.pi / 2 - beta), 0,
                 np.sin(np.pi / 2 - beta)], [0, 1, 0],
                [-np.sin(np.pi / 2 - beta), 0,
                 np.cos(np.pi / 2 - beta)]])


def optimize_axis():
    """Function calculating the rotational axis parameters for a given start and end location
    
    """
    alpha = MX.sym('alpha', 1, 1)
    beta = MX.sym('beta', 1, 1)

    C_z = np.array([[np.cos(alpha), -np.sin(alpha), 0],
                    [np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])

    C_y = np.array([[np.cos(np.pi / 2 - beta), 0,
                     np.sin(np.pi / 2 - beta)], [0, 1, 0],
                    [-np.sin(np.pi / 2 - beta), 0,
                     np.cos(np.pi / 2 - beta)]])

    # Calculate axis of rotation
    z_axis = C_z @ C_y @ np.array([[0], [0], [1]])

    q = 120 / 180 * np.pi

    C_axis = cos(q) * np.eye(3, 3) + sin(q) * np.array(
        [[0, -z_axis[2, 0], z_axis[1, 0]], [z_axis[2, 0], 0, -z_axis[0, 0]],
         [-z_axis[1, 0], z_axis[0, 0], 0]]) + (1 - cos(q)) * z_axis * z_axis.T
    print(C_axis.shape)
    #C_axis = cos(q)*DM.eye(3) + sin(q)*skew #+ (1-cos(q))*z_axis@z_axis.T

    C_axis1 = C_axis @ np.array([[-1], [0], [0.0]]) - np.array([[0], [-1],
                                                                [0.0]])
    C_axis2 = C_axis @ np.array([[-1], [0], [0.1]]) - np.array([[-0.1], [-1],
                                                                [0.0]])

    g = Function('g', [alpha, beta],
                 [C_axis1[0, 0], C_axis1[1, 0], C_axis1[2, 0]])

    a = np.linspace(0, np.pi, 100)
    b = np.linspace(0, np.pi, 100)
    xv, yv = np.meshgrid(a, b)
    x = g(xv[0], xv[1])
    x2 = g(yv[0], yv[1])
    print(np.max(x[0]))

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_aspect('equal')

    ax.scatter(xv[0], xv[1], x[0])
    ax.scatter(yv[0], yv[1], x2[0])
    plt.show()

    G = rootfinder('G', 'newton', g, {
        'print_iteration': False,
        'line_search': False,
        'abstol': 0.0001
    })
    print(G(0.5, 0.5))


def run_animation():
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')


def visualize(alpha: float, beta: float) -> None:

    C_z = np.array([[np.cos(alpha), -np.sin(alpha), 0],
                    [np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])

    C_y = np.array([[np.cos(np.pi / 2 - beta), 0,
                     np.sin(np.pi / 2 - beta)], [0, 1, 0],
                    [-np.sin(np.pi / 2 - beta), 0,
                     np.cos(np.pi / 2 - beta)]])

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_aspect('equal')

    x_axis = C_z @ C_y @ np.array([1, 0, 0])
    y_axis = C_z @ C_y @ np.array([0, 1, 0])
    z_axis = C_z @ C_y @ np.array([0, 0, 1])

    #original axes
    ax.plot([0, 1], [0, 0], zs=[0, 0], c='blue')
    ax.plot([0, 0], [0, 1], zs=[0, 0], c='blue')
    ax.plot([0, 0], [0, 0], zs=[0, 1], c='blue')

    #ax.plot([0, x_axis[0]], [0, x_axis[1]], zs=[0, x_axis[2]], c='blue')
    #ax.plot([0, y_axis[0]], [0, y_axis[1]], zs=[0, y_axis[2]], c='blue')
    ax.plot([0, z_axis[0]], [0, z_axis[1]], zs=[0, z_axis[2]], c='red')
    ax.scatter(0, 0, 0)

    q = 105 / 180 * np.pi / 100  #100/180*np.pi/100

    C_axis = np.cos(q) * np.eye(3, 3) + np.sin(q) * np.array(
        [[0, -z_axis[2], z_axis[1]], [z_axis[2], 0, -z_axis[0]],
         [-z_axis[1], z_axis[0], 0]]) + (1 - np.cos(q)) * z_axis * z_axis.T

    C_axis = np.cos(q) * np.eye(3, 3) + np.sin(q) * np.array(
        [[0, -z_axis[2], z_axis[1]], [z_axis[2], 0, -z_axis[0]],
         [-z_axis[1], z_axis[0], 0]]) + (1 - np.cos(q)) * z_axis * z_axis.T

    wing1 = np.array([-1, 0, 0.0])
    wing2 = np.array([-1, 0, 0.1])

    for i in range(100):
        wing1 = C_axis @ wing1
        wing2 = C_axis @ wing2
        ax.plot([0, wing1[0]], [0, wing1[1]], zs=[0, wing1[2]], c='blue')
        ax.plot([0, wing2[0]], [0, wing2[1]], zs=[0, wing2[2]], c='green')

    plt.show()


def visualize2(alpha: float, beta: float) -> None:

    C_z = np.array([[np.cos(alpha), -np.sin(alpha), 0],
                    [np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])

    C_y = np.array([[np.cos(np.pi / 2 - beta), 0,
                     np.sin(np.pi / 2 - beta)], [0, 1, 0],
                    [-np.sin(np.pi / 2 - beta), 0,
                     np.cos(np.pi / 2 - beta)]])

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_aspect('equal')

    x_axis = C_z @ C_y @ np.array([1, 0, 0])
    y_axis = C_z @ C_y @ np.array([0, 1, 0])
    z_axis = C_z @ C_y @ np.array([0, 0, 1])

    #original axes
    ax.plot([0, 1], [0, 0], zs=[0, 0], c='blue')
    ax.plot([0, 0], [0, 1], zs=[0, 0], c='blue')
    ax.plot([0, 0], [0, 0], zs=[0, 1], c='blue')

    #ax.plot([0, x_axis[0]], [0, x_axis[1]], zs=[0, x_axis[2]], c='blue')
    #ax.plot([0, y_axis[0]], [0, y_axis[1]], zs=[0, y_axis[2]], c='blue')
    ax.plot([0, z_axis[0]], [0, z_axis[1]], zs=[0, z_axis[2]], c='red')
    ax.scatter(0, 0, 0)

    q = -120 / 180 * np.pi / 3  #100/180*np.pi/100

    C_axis = np.cos(q) * np.eye(3, 3) + np.sin(q) * np.array(
        [[0, -z_axis[2], z_axis[1]], [z_axis[2], 0, -z_axis[0]],
         [-z_axis[1], z_axis[0], 0]]) + (1 - np.cos(q)) * z_axis * z_axis.T

    A = np.array([[0.1], [-0.75], [0]])
    B = np.array([[0.1], [0.25], [0]])
    C = np.array([[-0.1], [0.25], [0]])
    D = np.array([[-0.1], [-0.75], [0]])

    for i in range(3 + 1):

        color = random_color()

        ax.plot([A[0], B[0]], [A[1], B[1]], zs=[A[2], B[2]], c=color)
        ax.plot([B[0], C[0]], [B[1], C[1]], zs=[B[2], C[2]], c=color)
        ax.plot([C[0], D[0]], [C[1], D[1]], zs=[C[2], D[2]], c=color)
        ax.plot([A[0], D[0]], [A[1], D[1]], zs=[A[2], D[2]], c=color)

        ax.scatter(A[0], A[1], A[2], c=color)
        ax.scatter(B[0], B[1], B[2], c=color)
        ax.scatter(C[0], C[1], C[2], c=color)
        ax.scatter(D[0], D[1], D[2], c=color)

        A = C_axis @ A
        B = C_axis @ B
        C = C_axis @ C
        D = C_axis @ D

    ax.set_aspect('equal')
    plt.show()


if __name__ == '__main__':

    sim = TransitionAnim()
    sim.run_animation()
