from casadi import *

class TransitionModel:
    
    def __init__(self) -> None:
        self.n_b = 7
        self.n_r = 2
        
        self.q_b = MX.sym('q_b', self.n_b)
        self.q_r = MX.sym('q_r', self.n_r)
        
        self.alpha = np.deg2rad(60)
        self.beta = np.deg2rad(30)
        
        self.A_r_AB = np.array([[0.2],[0.2],[0]])
        self.A_r_BE = np.array([[0],[1],[0]])
        
        self.A_axis_of_rotation = np.array([[0],[0],[1]])
        
    def C_x(q:float|MX) -> np.ndarray|MX:
        return np.array([[1,    0,          0     ],
                         [0, np.cos(q), -np.sin(q)],
                         [0, np.sin(q),  np.cos(q)]])
    
    def C_y(q:float|MX) -> np.ndarray|MX:
        return np.array([[ np.cos(q),  0, np.sin(q)],
                        [ 0,       1,  0    ],
                        [-np.sin(q),  0, np.cos(q)]])
        
    def C_z(q:float|MX) -> np.ndarray|MX:
        return np.array([[np.cos(q), -np.sin(q), 0 ],
                         [np.sin(q),   np.cos(q),  ],
                         [    0    ,       0   , 1 ]])
        
    def set_axisofrotation(self) -> None :
        """Function setting the axis of rotation for the wing frame A
        
        """
        self.C_z(self.alpha)
        
        self.A_axis_of_rotation = self.C_z(self.alpha) @ self.C_y(pi/2 - self.beta) @ self.A_axis_of_rotation
        
    def set_C(self, q: np.ndarray|MX) -> list[np.ndarray|MX]:
        
        # Rotation Between A to B
        self.C = []
        C_BA = cos(q)*np.eye(3,3) + sin(q)*skew(self.A_axis_of_rotation) + (1-cos(q))*self.A_axis_of_rotation*self.A_axis_of_rotation.T
        
    def set_A_Jp(self) -> list[np.ndarray|MX]:
        """Function setting up the positional Jacobian matrices

        Returns:
            list[np.ndarray|MX]: List containing positional Jacobian matrices
        """
        self.A_Jp = []
        self.A_Jp.append(np.cross(self.A_axis_of_rotation, self.A_r_BE))
        
    
    def set_A_Jr(self) -> list[np.ndarray|MX]:
        """Function setting up the rotational Jacobian matrices

        Returns:
            list[np.ndarray|MX]: List containing rotational Jacobian matrices
        """
        self.A_Jr = []
        self.A_Jr.append(self.A_axis_of_rotation)
    
    def set_T() -> list[np.ndarray|MX]:
        raise NotImplementedError
    
    
    
    def C_BM(self, q):
        C_z = np.array([cos(q[1]), -sin(q[1]), 0],
                       [sin(q[1]),  cos(q[1]), 0],
                       [    0    ,       0   , 1])
        C_y = np.array([ cos(pi/2-q[1]),  0, sin(pi/2-q[1])],
                       [    0,      1,              0      ],
                       [-sin(pi/2-q[1]),  0, cos(pi/2-q[1])])
        
        return C_z@C_y
    
    def C_ME(self, q):
        return np.array([1, 0, 0],
                        [0, 1, 0],
                        [0, 0, 1])
        
    def aero_forces(self) -> np.ndarray:
        pass
        
    def thrust_forces(self) -> np.ndarray:
        pass
    
    def set_eom(self, q):
        
        # EOM in the form of Mq + b + g = tau J_extF_ext
        
        self.M = 0
        self.b = 0
        self.g = 0
        
        # Positional and Rotational Jacobian
        A_Jp = NotImplemented
        A_Jr = NotImplemented
        
        # Derivatives of Jacobians
        A_dJp = NotImplemented
        A_dJr = NotImplemented
        
        # Masses and mass moment of inertia matrices
        m = NotImplemented
        B_theta = NotImplemented
        
        # Gravity force in A frame 
        A_Fg = NotImplemented
        
        # Construct Mass Matrix
        for i in range(1):
            self.M += self.A_Jp[i].T @ m[i] @ self.A_Jp[i] + (self.C[i](q).T@A_Jr[i](q)).T@B_theta[i]@C[i].T@A_Jr[i]
        
        # Get centrifugal and coriolis forces
        for i in range(9):
            self.b += A_Jp[i](q).T@m[i]@A_dJp[i](q)@self.q_r + (C[i].T@A_Jr[i](q)).T@B_theta[i]@C[i].T@A_Jr[i] + # TODO: Check B_dJr here how to conver it to A_dJr
        
        # Gravity
        for i in range(9):
            self.g += -A_Jp[i].T@A_Fg[i]
    