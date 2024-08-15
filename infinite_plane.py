import numpy as np
from ray import Ray

class InfinitePlane:
    def __init__(self, normal, offset, material_index):
        self.normal = np.array(normal)
        self.offset = offset
        self.material_index = material_index

    def intersect(self, ray):
        denom = np.dot(self.normal, ray.direction)
        if np.abs(denom) > 1e-6:
            t = (self.offset - np.dot(self.normal, ray.origin)) / denom
            if t >= 0:
                return t
        return None

    def get_normal(self, intersection_point):
        return self.normal
