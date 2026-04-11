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
    
    # Risk for each PCA instread of each pillar
    def pca_risk(self, curve, Q):
        # Risk per pillar instrument
        S =  self.risk(curve)

        # eigen values and eigen vector (PCs) of the covariance matrix Q
        lambda_, E = PCA_.pca(Q)

        # Risk per PC
        # Risk along PC0 = E[0,0] * S[0] + E[1,0] * S[1] + E[2,0] * S[2] = sum(E[:,0] * S) = sum(E.T[0, :] * S)
        # Risk along PC1 = E[0,1] * S[0] + E[1,1] * S[1] + E[2,1] * S[2] = sum(E[:,1] * S) = sum(E.T[1, :] * S)
        # Risk along ith PC = E.T[i, :] * S => PC risk = E.T @ S
        return np.matmul(E.T, S);

    # Allocating the total VaR to each PC instead of each pillar
    def pca_covar_alloc(self, curve, Q):
        # Risk along each PC
        S_tilde = self.pca_risk(curve, Q)
        # eigen values and eigen vector (PCs) of the covariance matrix Q
        lambda_, E = PCA_.pca(Q)

        # Total VaR (c)
        c = self.covar(curve, Q)

        # Allocating the total VaR to each PC
        S_tilde_squared = S_tilde ** 2 # Risk squared along each pc [[S_tilde[0]**2], [S_tilde[1]**2], [S_tilde[2]**2]]
        eigen_value_scaled_risk_sq = S_tilde_squared[:,0] * lambda_
        c_alloc = eigen_value_scaled_risk_sq / c

        # Return column vector of c_alloc
        return c_alloc[:, np.newaxis]


