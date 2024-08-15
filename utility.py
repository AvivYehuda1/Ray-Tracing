import numpy as np

def dot(v1, v2):
    return np.dot(v1, v2)

def cross(v1, v2):
    return np.cross(v1, v2)

def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm if norm != 0 else v