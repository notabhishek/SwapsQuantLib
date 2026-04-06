import numpy as np 

class PCA_:

    @staticmethod
    def pca(Q):
        # Eigen values and vectors for the covariance matrix Q
        # np.linalg.eigh assumes matrix Q is symmetric and returns eigen values in ascending order
        eigenvalues, eigenvectors = np.linalg.eigh(Q)

        # return descending order of eigen values and corresponding eigen vectors
        return eigenvalues[::-1], eigenvectors[:,::-1]
    
    @classmethod
    def historical_multipliers(cls, Q, data):
        eigenvalues, eigenvectors = cls.pca(Q)

        centralised_data = data - data.mean(axis=0)
        multipliers = np.dot(centralised_data, eigenvectors)
        return multipliers