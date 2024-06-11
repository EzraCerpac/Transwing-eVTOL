import numpy as np

def skew(v:np.ndarray) -> np.ndarray:
    """Function converting a vector into a skew symmetric matrix

    Args:
        v (np.ndarray): The vector to be converted

    Returns:
        np.ndarray: Resulting skew symmetric matrix
    """
    
    return np.array([[ 0,    -v[2],  v[1]],
                     [ v[2],    0,   v[0]],
                     [-v[1],  v[0],     0]])