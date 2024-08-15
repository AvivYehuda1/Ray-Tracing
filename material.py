import numpy as np

class Material:
    def __init__(self, diffuse_color, specular_color, reflection_color, shininess, transparency):
        self.diffuse_color = np.array(diffuse_color)
        self.specular_color = np.array(specular_color)
        self.reflection_color = np.array(reflection_color)  # Store reflection color as an array
        self.shininess = shininess
        self.transparency = transparency
        self.reflection_coefficient = np.mean(reflection_color)  # Keep this if needed as scalar

