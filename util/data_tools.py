import numpy as np


def expand_cov(cov):
    """
    Expand the covariance matrix corresponding to the initial points
    """

    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    sorted_indices = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[sorted_indices]
    eigenvectors = eigenvectors[:, sorted_indices]

    largest_eigenvalues = eigenvalues[0] * np.ones((3, ))

    V = eigenvectors.copy()
    L = np.diag(eigenvalues)
    L_largest = np.diag(largest_eigenvalues)
    
    Sigma = V @ L @ V.T
    Sigma_sphere = V @ L_largest @ V.T
    # Sigma = Vs[k] @ np.diag([lambda_1_, lambda_2_, lambda_3]) @ Vs[k].T
    
    return Sigma_sphere