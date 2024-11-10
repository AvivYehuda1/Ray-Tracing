# **Ray Tracing Project**

This project implements a basic ray tracing algorithm, developed as part of a Graphics course at Tel Aviv University. Ray tracing is a rendering technique that simulates the way light interacts with objects to produce realistic images.

## **Features**

- **Basic Shapes**: Supports rendering of spheres, planes, and cubes.
- **Lighting**: Implements point light sources with diffuse and specular reflections.
- **Materials**: Includes basic material properties such as color and reflectivity.
- **Camera**: Configurable camera position and orientation for scene rendering.

## **Project Structure**

- `camera.py`: Defines the camera's position, orientation, and projection.
- `cube.py`: Contains the implementation for rendering cubes.
- `infinite_plane.py`: Handles the rendering of infinite planes.
- `light.py`: Manages light sources and their properties.
- `material.py`: Defines material properties for objects.
- `ray.py`: Represents rays used in tracing computations.
- `ray_tracer.py`: Core ray tracing algorithm implementation.
- `scene_settings.py`: Configures the scene, including objects and lighting.
- `sphere.py`: Contains the implementation for rendering spheres.
- `utility.py`: Provides utility functions for vector operations and other calculations.
- `scenes/`: Directory containing predefined scene configurations.
- `surfaces/`: Directory with surface definitions and textures.

## **Usage**

To render a scene, execute the `ray_tracer.py` script with the desired scene configuration:

```bash
python ray_tracer.py --scene scenes/pool.txt
```

Replace `scenes/pool.txt` with the path to your specific scene configuration file.

## **Examples**

Rendered images are saved in the project directory. For instance, rendering the `pool` scene will generate an image named `pool.png`.
