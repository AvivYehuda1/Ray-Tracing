import argparse
from PIL import Image
import numpy as np

from camera import Camera
from light import Light
from material import Material
from scene_settings import SceneSettings
from surfaces.cube import Cube
from surfaces.infinite_plane import InfinitePlane
from surfaces.sphere import Sphere
from ray import Ray

def normalize(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm

def reflect(ray_direction, normal):
    return ray_direction - 2 * np.dot(ray_direction, normal) * normal

def find_nearest_intersection(ray, objects):
    nearest_t = np.inf
    nearest_object = None
    for obj in objects:
        t = obj.intersect(ray)
        if t is not None and t < nearest_t:
            nearest_t = t
            nearest_object = obj
    return nearest_t, nearest_object

def compute_reflection_rays(lights_rays_directions, surface_normals):
    return lights_rays_directions - 2 * np.sum(lights_rays_directions * surface_normals, axis=-1, keepdims=True) * surface_normals

def compute_specular_colors(surfaces_specular_color, surfaces_phong_coefficient, surfaces_to_lights_directions, viewer_directions, surface_normals, lights_specular_intensity, light_color):

    Ks = surfaces_specular_color
    Lm = surfaces_to_lights_directions
    Rm = compute_reflection_rays(lights_rays_directions=Lm, surface_normals=surface_normals)

    V = viewer_directions
    alpha = surfaces_phong_coefficient
    Ims = lights_specular_intensity

    Rm_dot_V = np.sum(Rm * V, axis=-1, keepdims=True)

    specular_colors = np.sum(Ks * (Rm_dot_V ** alpha) * Ims * light_color, axis=0)
    specular_colors = np.nan_to_num(specular_colors, nan=0.0)

    return specular_colors


def compute_lighting(intersection_point, normal, view_direction, nearest_object, materials, lights, objects, background_color, num_shadow_rays=5, max_recursion_depth=3, recursion_depth=0):
    if recursion_depth > max_recursion_depth:
        return background_color

    material = materials[nearest_object.material_index - 1]

    ambient_intensity = np.array([0.5, 0.5, 0.5])
    ambient_reflectivity = material.diffuse_color
    ambient_color = ambient_reflectivity * ambient_intensity
    color = ambient_color

    for light in lights:
        light_intensity = 0.0
        for _ in range(num_shadow_rays):
            light_sample = light.position + light.radius * np.random.uniform(-0.25, 0.25, 3)
            light_direction = normalize(light_sample - intersection_point)
            shadow_ray = Ray(intersection_point + normal * 1e-5, light_direction)
            shadow_t, shadow_object = find_nearest_intersection(shadow_ray, objects)
            if shadow_object is None or shadow_t > np.linalg.norm(light_sample - intersection_point):
                light_intensity += 1.0

        light_intensity /= num_shadow_rays

        diffuse_intensity = max(np.dot(normal, light_direction), 0)
        diffuse = diffuse_intensity * material.diffuse_color * light.color

        specular = compute_specular_colors(
            material.specular_color, 
            material.shininess, 
            light_direction[np.newaxis, :], 
            view_direction[np.newaxis, :], 
            normal[np.newaxis, :], 
            light.specular_intensity,
            light.color 
        )[0]

        color += (diffuse + specular) * light_intensity * (1 - light.shadow_intensity) * 3

    if recursion_depth < max_recursion_depth and material.reflection_coefficient > 0:
        reflection_direction = reflect(view_direction, normal)
        reflection_ray = Ray(intersection_point + normal * 1e-5, reflection_direction)
        reflection_t, reflection_object = find_nearest_intersection(reflection_ray, objects)
        if reflection_object is not None:
            reflection_intersection_point = reflection_ray.origin + reflection_t * reflection_ray.direction
            reflection_normal = reflection_object.get_normal(reflection_intersection_point)
            reflection_view_direction = -reflection_ray.direction
            reflection_color = compute_lighting(
                reflection_intersection_point, reflection_normal, reflection_view_direction,
                reflection_object, materials, lights, objects, background_color,
                num_shadow_rays, max_recursion_depth, recursion_depth + 1
            )
            color += reflection_color * material.reflection_coefficient

    if recursion_depth < max_recursion_depth and material.transparency > 0:
        transmission_ray = Ray(intersection_point - normal * 1e-5, view_direction)
        transmission_t, transmission_object = find_nearest_intersection(transmission_ray, objects)
        if transmission_object is not None:
            transmission_intersection_point = transmission_ray.origin + transmission_t * transmission_ray.direction
            transmission_normal = transmission_object.get_normal(transmission_intersection_point)
            transmission_view_direction = -transmission_ray.direction
            transmission_color = compute_lighting(transmission_intersection_point, transmission_normal, transmission_view_direction, transmission_object, materials, lights, objects, background_color, num_shadow_rays, max_recursion_depth, recursion_depth + 1)
            color = color * (1 - material.transparency) + transmission_color * material.transparency
    
    return np.clip(color, 0, 1)


def render_scene(camera, objects, lights, materials, image_width, image_height, background_color, num_shadow_rays, max_recursion_depth):
    image_array = np.zeros((image_height, image_width, 3))

    for y in range(image_height):
        for x in range(image_width):
            ray = camera.get_ray(image_width - x - 1, y, image_width, image_height)  
            nearest_t, nearest_object = find_nearest_intersection(ray, objects)
            if nearest_object is not None:
                intersection_point = ray.origin + nearest_t * ray.direction
                normal = nearest_object.get_normal(intersection_point)

                view_direction = -ray.direction

                color = compute_lighting(intersection_point, normal, view_direction, nearest_object, materials, lights, objects, background_color, num_shadow_rays, max_recursion_depth)
                image_array[y, x] = color * 255
            else:
                image_array[y, x] = background_color[:3] * 255  
    
    return image_array

def save_image(image_array, output_image):
    image = Image.fromarray(np.uint8(image_array))
    image.save(output_image)

def parse_scene_file(file_path):
    objects = []
    materials = []
    lights = []
    camera = None
    scene_settings = None
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            obj_type = parts[0]
            params = [float(p) for p in parts[1:]]
            if obj_type == "cam":
                camera = Camera(params[:3], params[3:6], params[6:9], params[9], params[10])
            elif obj_type == "set":
                scene_settings = SceneSettings(params[:3], int(params[3]), int(params[4]))
                print(f"Parsed scene settings: {scene_settings}")
            elif obj_type == "mtl":
                diffuse_color = params[:3]
                specular_color = params[3:6]
                reflection_color = params[6:9]
                shininess = params[9]
                transparency = params[10]
                material = Material(diffuse_color, specular_color, reflection_color, shininess, transparency)
                materials.append(material)
            elif obj_type == "sph":
                sphere = Sphere(params[:3], params[3], int(params[4]))
                objects.append(sphere)
            elif obj_type == "pln":
                plane = InfinitePlane(params[:3], params[3], int(params[4]))
                objects.append(plane)
            elif obj_type == "cub":
                cube = Cube(params[:3], params[3], int(params[4]))
                objects.append(cube)
            elif obj_type == "lgt":
                light = Light(params[:3], params[3:6], params[6], params[7], params[8])
                lights.append(light)
            else:
                raise ValueError("Unknown object type: {}".format(obj_type))
    return camera, scene_settings, objects, materials, lights



def main():
    parser = argparse.ArgumentParser(description='Python Ray Tracer')
    parser.add_argument('scene_file', type=str, help='Path to the scene file')
    parser.add_argument('output_image', type=str, help='Name of the output image file')
    parser.add_argument('--width', type=int, default=300, help='Image width')
    parser.add_argument('--height', type=int, default=300, help='Image height')
    args = parser.parse_args()

    camera, scene_settings, objects, materials, lights = parse_scene_file(args.scene_file)

    if scene_settings is None:
        raise ValueError("Scene settings not properly defined in the scene file.")

    image_array = render_scene(camera, objects, lights, materials, args.width, args.height, scene_settings.background_color, scene_settings.root_number_shadow_rays, scene_settings.max_recursions)

    save_image(image_array, args.output_image)

if __name__ == '__main__':
    main()

