import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import matplotlib
from casadi import *
import random as random

class TransitionSim:

    def __init__(self, alpha:float=45, beta:float=40) -> None:

        self.alpha = np.deg2rad(alpha)
        self.beta = np.deg2rad(beta)

        self.C_z = np.array([[np.cos(self.alpha), -np.sin(self.alpha), 0],
                [np.sin(self.alpha), np.cos(self.alpha), 0], [0, 0, 1]])

        self.C_y = np.array([[np.cos(np.pi / 2 - self.beta), 0,
                        np.sin(np.pi / 2 - self.beta)], [0, 1, 0],
                        [-np.sin(np.pi / 2 - self.beta), 0,
                        np.cos(np.pi / 2 - self.beta)]])

        self.axis = self.C_z @ self.C_y @ np.array([[0], [0], [1]])

        def init_animation(self,) -> None:
            self.

        def draw_wing(self, i) -> None:





alpha = 0.852786  #35/180*np.pi
beta = 0.0124301  #40/180*np.pi

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.set_aspect('equal')
wing, = ax.plot([], [], [])


def random_color():
    np.random.seed()
    rgbl = [np.random.random(), np.random.random(), np.random.random()]
    print(np.random.random())
    return tuple(rgbl)


C_z = np.array([[np.cos(alpha), -np.sin(alpha), 0],
                [np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])

C_y = np.array([[np.cos(np.pi / 2 - beta), 0,
                 np.sin(np.pi / 2 - beta)], [0, 1, 0],
                [-np.sin(np.pi / 2 - beta), 0,
                 np.cos(np.pi / 2 - beta)]])


def solve():
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


def update(frame_number):

    alpha = 45 / 180 * np.pi  #0.852786 #35/180*np.pi
    beta = 40 / 180 * np.pi  #0.0124301 #40/180*np.pi

    C_z = np.array([[np.cos(alpha), -np.sin(alpha), 0],
                    [np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])

    C_y = np.array([[np.cos(np.pi / 2 - beta), 0,
                     np.sin(np.pi / 2 - beta)], [0, 1, 0],
                    [-np.sin(np.pi / 2 - beta), 0,
                     np.cos(np.pi / 2 - beta)]])

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

    for i in range(frame_number):
        color = random_color()
        A = C_axis @ A
        B = C_axis @ B
        C = C_axis @ C
        D = C_axis @ D

    ax.plot([A[0], B[0]], [A[1], B[1]], zs=[A[2], B[2]], c=color)
    ax.plot([B[0], C[0]], [B[1], C[1]], zs=[B[2], C[2]], c=color)
    ax.plot([C[0], D[0]], [C[1], D[1]], zs=[C[2], D[2]], c=color)
    ax.plot([A[0], D[0]], [A[1], D[1]], zs=[A[2], D[2]], c=color)

    ax.scatter(A[0], A[1], A[2], c=color)
    ax.scatter(B[0], B[1], B[2], c=color)
    ax.scatter(C[0], C[1], C[2], c=color)
    ax.scatter(D[0], D[1], D[2], c=color)


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
    C_z = np.array([[np.cos(alpha), -np.sin(alpha), 0],
                    [np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])

    C_y = np.array([[np.cos(np.pi / 2 - beta), 0,
                     np.sin(np.pi / 2 - beta)], [0, 1, 0],
                    [-np.sin(np.pi / 2 - beta), 0,
                     np.cos(np.pi / 2 - beta)]])

    alpha = 45 / 180 * np.pi  #0.852786 #35/180*np.pi
    beta = 40 / 180 * np.pi  #0.0124301 #40/180*np.pi

    #visualize2(alpha, beta)

    animation.FuncAnimation(fig=fig, func=update, frames=20, interval=30)
    plt.show()
