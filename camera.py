import numpy as np
from ray import Ray

class Camera:
    def __init__(self, position, look_at, up_vector, screen_distance, screen_width):
        self.position = np.array(position)
        self.look_at = np.array(look_at)
        self.up_vector = np.array(up_vector)
        self.screen_distance = screen_distance
        self.screen_width = screen_width
        self.compute_camera_parameters()

    def compute_camera_parameters(self):
        # Calculate direction vector from camera to look-at point
        self.direction = self.look_at - self.position
        self.direction = self.direction / np.linalg.norm(self.direction)
        
        # Recalculate the up vector to make it perpendicular to the direction vector
        self.right_vector = np.cross(self.direction, self.up_vector)
        self.right_vector = self.right_vector / np.linalg.norm(self.right_vector)
        self.up_vector = np.cross(self.right_vector, self.direction)
        self.up_vector = self.up_vector / np.linalg.norm(self.up_vector)
        
        # Calculate aspect ratio and screen height
        self.aspect_ratio = self.screen_width / self.screen_distance
        self.screen_height = self.screen_width / self.aspect_ratio

    def get_pixel_location(self, pixel_x, pixel_y, image_width, image_height):
        # Convert pixel coordinate to normalized device coordinate (NDC)
        ndc_x = (pixel_x + 0.5) / image_width  # Normalize pixel_x to [0, 1]
        ndc_y = (pixel_y + 0.5) / image_height  # Normalize pixel_y to [0, 1]

        # Convert NDC to screen space
        screen_x = (ndc_x - 0.5) * self.screen_width
        screen_y = (0.5 - ndc_y) * self.screen_height

        # Calculate the world space coordinates of the pixel on the screen plane
        pixel_world_position = (
            self.position +
            self.direction * self.screen_distance +
            screen_x * self.right_vector +
            screen_y * self.up_vector
        )

        return pixel_world_position

    def get_ray(self, pixel_x, pixel_y, image_width, image_height):
        aspect_ratio = image_width / image_height  # This line ensures the aspect ratio is correctly calculated
        self.screen_height = self.screen_width / aspect_ratio  # Correct screen height calculation
        pixel_location = self.get_pixel_location(pixel_x, pixel_y, image_width, image_height)
        ray_direction = pixel_location - self.position
        ray_direction = ray_direction / np.linalg.norm(ray_direction)  # Normalize the ray direction
        return Ray(self.position, ray_direction)

