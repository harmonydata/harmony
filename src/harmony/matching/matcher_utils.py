import numpy as np
from numpy import dot, mat, matmul, ndarray
from numpy.linalg import norm

def cosine_similarity(vec1: ndarray, vec2: ndarray) -> ndarray:
    dp = dot(vec1, vec2.T)
    m1 = mat(norm(vec1, axis=1))
    m2 = mat(norm(vec2.T, axis=0))

    return np.asarray(dp / matmul(m1.T, m2))


