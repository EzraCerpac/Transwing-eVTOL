import control as ct
from aerosandbox import numpy as np
from matplotlib import pyplot as plt

from departments.stability_and_control.stability.visualisation import show_3D_lateral, show_3D_longitudinal


def SS_symetric(C_X_u, C_X_alpha, C_Z_0, C_X_q, C_Z_u, C_Z_alpha, C_X_0, C_Z_q, \
                mu_c, C_m_u, C_m_alpha, C_m_q, C_X_delta_e, C_Z_delta_e, C_m_delta_e, c, V, C_Z_alpha_dot,
                C_m_alpha_dot, \
                K_Y_squared, T=1, u=None, show_3D=False):
    Q = np.array([
        [-C_X_u, -C_X_alpha, -C_Z_0, -C_X_q],
        [-C_Z_u, -C_Z_alpha, C_X_0, -(C_Z_q + 2 * mu_c)],
        [0, 0, 0, -1],
        [-C_m_u, -C_m_alpha, 0, -C_m_q],
    ])
    eigvals, eigvecs = np.linalg.eig(-Q)
    print(eigvals)

    R = np.array([
        [-C_X_delta_e],
        [-C_Z_delta_e],
        [0],
        [-C_m_delta_e],
    ])
    P = np.array([
        [-2 * mu_c * c / V, 0, 0, 0],
        [0, (C_Z_alpha_dot - 2 * mu_c) * c / V, 0, 0],
        [0, 0, -c / V, 0],
        [0, C_m_alpha_dot * c / V, 0, -2 * mu_c * K_Y_squared * c / V],
    ])
    A = np.linalg.inv(P) @ Q
    B = np.linalg.inv(P) @ R
    C = np.diag([1, np.degrees(1), np.degrees(1), V / c * np.degrees(1)])
    D = np.zeros_like(B)

    sys = ct.ss(A, B, C, D,
                inputs=[r'$\delta_e$ [rad]'],
                states=[r'$\hat{u}$', r'$\alpha$', r'$\theta$', r'$\frac{q\hat{c}}{V}$'],
                outputs=[r'$\hat{u} [m/s]$', r'$\alpha [deg]$', r'$\theta$ [deg]', r'$q$ [deg/s]'],
                name='Longitudinal Dynamics'
                )

    alpha_0 = 0
    theta_0 = 0
    q_0 = 0

    T = np.linspace(0, T, 1000)
    X0 = np.array([0, alpha_0, theta_0, q_0])
    U = np.zeros((1, T.shape[0]))
    U[:, 0] = u

    response = ct.forced_response(sys, X0=X0, T=T, U=U)
    fig, axs = plt.subplots(5, 1, figsize=(12, 12), sharex=True)
    axs = axs.reshape(-1, 1)
    response.plot(ax=axs)
    plt.show()

    if show_3D:
        show_3D_longitudinal(response)

    # C = np.array([0, 0, 1, 0])
    # D = np.array([0])
    # sys_pz = ct.ss(A, B, C, D,
    #                  inputs=[r'$\delta_e$'],
    #                  states=[r'$\hat{u}$', r'$\alpha$', r'$\theta$', r'$\frac{q\hat{c}}{V}$'],
    #                  outputs=[r'$\hat{u}$'],
    #                  name='Longitudinal Dynamics'
    #                  )
    #
    # ct.nyquist_plot(sys_pz)
    # plt.show()


def SS_asymetric(
        C_L,
        C_Y_beta,
        C_Y_beta_dot,
        C_l_beta,
        C_l_beta_dot,
        C_n_beta,
        C_n_beta_dot,
        C_Y_p,
        C_l_p,
        C_n_p,
        C_Y_r,
        C_l_r,
        C_n_r,
        C_Y_delta_a,
        C_l_delta_a,
        C_n_delta_a,
        C_Y_delta_r,
        C_l_delta_r,
        C_n_delta_r,
        mu_b,
        b,
        V,
        K_X_squared,
        K_XZ,
        K_Z_squared,
        T=1,
        u=None,
        show_3D=False,
):
    Q = -np.array([
        [C_Y_beta, C_L, C_Y_p, C_Y_r - 4 * mu_b],
        [0, 0, 1, 0],
        [C_l_beta, 0, C_l_p, C_l_r],
        [C_n_beta, 0, C_n_p, C_n_r],
    ])
    eigvals, eigvecs = np.linalg.eig(-Q)
    print(eigvals)

    R = np.array([
        [-C_Y_delta_a],
        [0],
        [-C_l_delta_a],
        [-C_n_delta_a],
    ])
    P = b / V * np.array([
        [C_Y_beta_dot - 2 * mu_b, 0, 0, 0],
        [0, -1/2, 0, 0],
        [0, 0, -4 * mu_b * K_X_squared, 4 * mu_b * K_XZ],
        [C_n_beta_dot, 0, 4 * mu_b * K_XZ, -4 * mu_b * K_Z_squared],
    ])

    A = np.linalg.inv(P) @ Q
    B = np.linalg.inv(P) @ R
    C = np.diag([1, 1, 2 * V / b, 2 * V / b])
    D = np.zeros_like(B)
    C = np.degrees(C)

    sys = ct.ss(A, B, C, D,
                inputs=[r'$\delta_a$'],
                states=[r'$\beta$', r'$\phi$', r'$\frac{pb}{2V}$', r'$\frac{rb}{2V}$'],
                outputs=[r'$\beta$ [deg]', r'$\phi$ [deg]', r'$p$ [deg/s]', r'$r$ [deg/s]'],
                name='Lateral Dynamics'
                )


    T = np.linspace(0, T, 1000)
    X0 = np.zeros(4)
    U = np.zeros(T.shape[0])
    U = u

    response = ct.forced_response(sys, X0=X0, T=T, U=U)
    fig, axs = plt.subplots(5, 1, figsize=(12, 12), sharex=True)
    axs = axs.reshape(-1, 1)
    response.plot(ax=axs)

    plt.show()

    if show_3D:
        show_3D_lateral(response)

    # C = np.array([1, 0, 0, 0])
    # D = np.array([0])
    # sys_pz = ct.ss(A, B, C, D,
    #                  inputs=[r'$\delta_e$'],
    #                  states=[r'$\hat{u}$', r'$\alpha$', r'$\theta$', r'$\frac{q\hat{c}}{V}$'],
    #                  outputs=[r'$\hat{u}$'],
    #                  name='Longitudinal Dynamics'
    #                  )
    #
    # ct.pole_zero_plot(sys_pz, grid=True)
    # plt.show()



def cessna_SS(T=1):
    c = 2.022
    b = 13.36
    V = 59.9

    mu_c = 102.7
    K_Y_squared = 0.980

    C_X_0 = 0
    C_X_u = -0.2199
    C_X_alpha = 0.4653
    C_X_q = 0
    C_X_delta_e = 0
    C_Z_0 = -1.1360
    C_Z_u = -2.2710
    C_Z_alpha = -5.1600
    C_Z_alpha_dot = -1.4300
    C_Z_q = -3.8600
    C_Z_delta_e = -0.6238
    C_m_0 = 0
    C_m_u = 0
    C_m_alpha = -0.4300
    C_m_alpha_dot = -3.7000
    C_m_q = -7.0400
    C_m_delta_e = -1.5530

    K_X_squared = 0.012
    K_XZ = 0.002
    K_Z_squared = 0.037
    mu_b = 15.5

    C_L = 1.1360
    C_Y_beta = -0.9896
    C_Y_beta_dot = 0
    C_l_beta = -0.0772
    C_l_beta_dot = 0
    C_n_beta = 0.1638
    C_n_beta_dot = 0
    C_Y_p = -0.087
    C_l_p = -0.344
    C_n_p = -0.0108
    C_Y_r = 0.43
    C_l_r = 0.28
    C_n_r = -0.1930
    C_Y_delta_a = 0
    C_l_delta_a = -0.2349
    C_n_delta_a = 0.0286
    C_Y_delta_r = 0.3037
    C_l_delta_r = 0.0286
    C_n_delta_r = -0.1261

    # SS_symetric(C_X_u, C_X_alpha, C_Z_0, C_X_q, C_Z_u, C_Z_alpha, C_X_0, C_Z_q, \
    #             mu_c, C_m_u, C_m_alpha, C_m_q, C_X_delta_e, C_Z_delta_e, C_m_delta_e, c, V, C_Z_alpha_dot,
    #             C_m_alpha_dot, \
    #             K_Y_squared, T=T)

    # SS_asymetric(C_L, C_Y_beta, C_Y_beta_dot, C_l_beta, C_l_beta_dot, C_n_beta, C_n_beta_dot, C_Y_p, C_l_p, C_n_p, C_Y_r,
    #              C_l_r, C_n_r, C_Y_delta_a, C_l_delta_a, C_n_delta_a, C_Y_delta_r, C_l_delta_r, C_n_delta_r, mu_b,
    #              b, V, K_X_squared, K_XZ, K_Z_squared, T=T,
    #              )

    for name in dir():
        if name.startswith('C_'):
            print(name, '=', eval(name))



if __name__ == '__main__':
    cessna_SS(10)
