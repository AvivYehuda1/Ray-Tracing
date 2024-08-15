import numpy as np

class Cube:
    def __init__(self, position, scale, material_index):
        self.position = np.array(position)
        self.scale = scale
        self.material_index = material_index
        half_size = scale / 2
        self.min_bound = self.position - half_size
        self.max_bound = self.position + half_size

    def intersect(self, ray):
        t_min = (self.min_bound - ray.origin) / ray.direction
        t_max = (self.max_bound - ray.origin) / ray.direction

        t1 = np.minimum(t_min, t_max)
        t2 = np.maximum(t_min, t_max)

        t_near = np.max(t1)
        t_far = np.min(t2)

        if t_near > t_far or t_far < 0:
            return None
        return t_near if t_near >= 0 else t_far

    def get_normal(self, intersection_point):
        delta = intersection_point - self.position
        abs_delta = np.abs(delta)
        max_index = np.argmax(abs_delta)
        
        normal = np.zeros(3)
        normal[max_index] = np.sign(delta[max_index])
        return normal
