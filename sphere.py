import numpy as np

def normalize(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm

class Sphere:
    def __init__(self, position, radius, material_index):
        self.position = np.array(position)
        self.radius = radius
        self.material_index = material_index

    def intersect(self, ray):
        oc = ray.origin - self.position
        a = np.dot(ray.direction, ray.direction)
        b = 2.0 * np.dot(oc, ray.direction)
        c = np.dot(oc, oc) - self.radius * self.radius
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None
        t1 = (-b - np.sqrt(discriminant)) / (2.0 * a)
        t2 = (-b + np.sqrt(discriminant)) / (2.0 * a)
        if t1 > 0 and t2 > 0:
            return min(t1, t2)
        elif t1 > 0:
            return t1
        elif t2 > 0:
            return t2
        else:
            return None

    def get_normal(self, intersection_point):
        return normalize(intersection_point - self.position)
