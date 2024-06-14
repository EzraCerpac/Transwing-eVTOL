import control as ct
from aerosandbox import numpy as np
from matplotlib import pyplot as plt


def SS_symetric(C_X_u, C_X_alpha, C_Z_0, C_X_q, C_Z_u, C_Z_alpha, C_X_0, C_Z_q, \
                mu_c, C_m_u, C_m_alpha, C_m_q, C_X_delta_e, C_Z_delta_e, C_m_delta_e, c, V, C_Z_alpha_dot,
                C_m_alpha_dot, \
                K_Y_squared, T=1):
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
    C = np.identity(4)
    D = np.zeros_like(B)
    C[-1, -1] *= V / c
    D[-1, -1] *= V / c

    sys = ct.ss(A, B, C, D,
                inputs=[r'$\delta_e$'],
                states=[r'$\hat{u}$', r'$\alpha$', r'$\theta$', r'$\frac{q\hat{c}}{V}$'],
                outputs=[r'$\hat{u}$', r'$\alpha$', r'$\theta$', r'$q$'],
                name='Longitudinal Dynamics'
                )

    alpha_0 = 0
    theta_0 = 0
    q_0 = 0

    T = np.linspace(0, T, 1000)
    X0 = np.array([0, alpha_0, theta_0, q_0])
    U = np.zeros((1, T.shape[0]))
    U[:, 0] = -5

    response = ct.forced_response(sys, X0=X0, T=T, U=U)
    fig, axs = plt.subplots(5, 1, figsize=(12, 12), sharex=True)
    axs = axs.reshape(-1, 1)
    response.plot(ax=axs)
    plt.show()


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
    D = np.array([0, 0, 2 * V / b, 2 * V / b]).reshape(-1, 1)

    sys = ct.ss(A, B, C, D,
                inputs=[r'$\delta_a$'],
                states=[r'$\beta$', r'$\phi$', r'$\frac{pb}{2V}$', r'$\frac{rb}{2V}$'],
                outputs=[r'$\beta$', r'$\phi$', r'$p$', r'$r$'],
                name='Lateral Dynamics'
                )


    T = np.linspace(0, T, 1000)
    X0 = np.zeros(4)
    U = np.zeros(T.shape[0])
    U[0] = -5

    response = ct.forced_response(sys, X0=X0, T=T, U=U)
    fig, axs = plt.subplots(5, 1, figsize=(12, 12), sharex=True)
    axs = axs.reshape(-1, 1)
    response.plot(ax=axs)
    plt.show()



def cessna_SS(T=1):
    c = 2.022
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

    SS_symetric(C_X_u, C_X_alpha, C_Z_0, C_X_q, C_Z_u, C_Z_alpha, C_X_0, C_Z_q, \
                mu_c, C_m_u, C_m_alpha, C_m_q, C_X_delta_e, C_Z_delta_e, C_m_delta_e, c, V, C_Z_alpha_dot,
                C_m_alpha_dot, \
                K_Y_squared, T=T)


if __name__ == '__main__':
    cessna_SS(10)
