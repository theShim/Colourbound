import math
from PIL import Image
import numpy as np

class Vec:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Vec(x={self.x}, y={self.y}, z={self.z})"

    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        if isinstance(scalar, Vec):
            return Vec(self.x * scalar.x, self.y * scalar.y, self.z * scalar.z)
        return Vec(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        return Vec(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self):
        return Vec(-self.x, -self.y, -self.z)

    def length(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def dot_product(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross_product(self, other):
        return Vec(self.y * other.z - self.z * other.y,
                   self.z * other.x - self.x * other.z,
                   self.x * other.y - self.y * other.x)

    def normalized(self):
        len = self.length()
        return self / len if len != 0 else self

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction.normalized()

    def __repr__(self):
        return f"Ray(origin={self.origin}, direction={self.direction})"

    def point_at_parameter(self, t):
        return self.origin + self.direction * t

class Light:
    def __init__(self, position, intensity):
        self.position = position
        self.intensity = intensity

class Material:
    def __init__(self, color, ambient, diffuse, specular, shininess):
        self.color = color
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess

class Sphere:
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def intersect(self, ray):
        oc = ray.origin - self.center
        a = ray.direction.dot_product(ray.direction)
        b = 2.0 * oc.dot_product(ray.direction)
        c = oc.dot_product(oc) - self.radius ** 2
        discriminant = b ** 2 - 4 * a * c

        if discriminant < 0:
            return False, None

        t1 = (-b - discriminant ** 0.5) / (2.0 * a)
        t2 = (-b + discriminant ** 0.5) / (2.0 * a)

        if t1 < 0 and t2 < 0:
            return False, None

        t = t1 if t1 < t2 else t2
        if t < 0:
            t = t2

        intersection_point = ray.point_at_parameter(t)
        normal = (intersection_point - self.center).normalized()
        return True, (intersection_point, normal)

def compute_lighting(point, normal, view, material, lights, objects):
    ambient = material.ambient
    diffuse = 0
    specular = 0

    for light in lights:
        light_dir = (light.position - point).normalized()

        # Shadow check
        shadow_ray = Ray(point, light_dir)
        shadow_hit = False
        for obj in objects:
            hit, _ = obj.intersect(shadow_ray)
            if hit:
                shadow_hit = True
                break
        if shadow_hit:
            continue

        # Diffuse shading
        diff = max(normal.dot_product(light_dir), 0)
        diffuse += light.intensity * material.diffuse * diff

        # Specular shading
        reflect_dir = 2 * normal.dot_product(light_dir) * normal - light_dir
        spec = max(reflect_dir.dot_product(view), 0) ** material.shininess
        specular += light.intensity * material.specular * spec

    return ambient + diffuse + specular

def trace_ray(ray, objects, lights):
    closest_t = float('inf')
    hit_color = Vec(0, 0, 0)

    for obj in objects:
        hit, result = obj.intersect(ray)
        if hit:
            intersection_point, normal = result
            t = (intersection_point - ray.origin).length()
            if t < closest_t:
                closest_t = t
                view = -ray.direction
                lighting = compute_lighting(intersection_point, normal, view, obj.material, lights, objects)
                hit_color = Vec(obj.material.color.x * lighting, obj.material.color.y * lighting,
                                obj.material.color.z * lighting)

    return hit_color

def main():
    width, height = 400, 400
    ss_factor = 2  # Supersampling factor
    image = Image.new("RGB", (width, height))
    camera_position = Vec(0, 0, 0)
    screen = (-1, 1, 1, -1)  # left, top, right, bottom

    material = Material(Vec(1, 0, 0), 0.1, 0.6, 0.3, 32)
    sphere = Sphere(Vec(0, 0, -5), 1, material)
    light = Light(Vec(5, 5, -5), 1.0)
    lights = [light]

    objects = [sphere]



    # Create arrays for pixel coordinates
    x_coords = np.tile(np.arange(width), (height, 1))
    y_coords = np.tile(np.arange(height).reshape(height, 1), (1, width))

    # Supersampling offsets
    ss_offsets = (np.arange(ss_factor) + 0.5) / ss_factor
    ss_offsets_x, ss_offsets_y = np.meshgrid(ss_offsets, ss_offsets)

    # Initialize color buffer
    color_buffer = np.zeros((height, width, 3), dtype=np.float32)

    for sy in range(ss_factor):
        for sx in range(ss_factor):
            # Compute pixel positions
            px = screen[0] + (screen[2] - screen[0]) * (x_coords + ss_offsets_x[sy, sx]) / width
            py = screen[1] + (screen[3] - screen[1]) * (y_coords + ss_offsets_y[sy, sx]) / height

            directions = np.stack((px, py, np.full_like(px, -1)), axis=-1)
            directions /= np.linalg.norm(directions, axis=-1, keepdims=True)

            # Trace rays for the current supersample
            for i in range(height):
                for j in range(width):
                    ray = Ray(camera_position, Vec(*directions[i, j]))
                    color = trace_ray(ray, objects, lights)
                    color_buffer[i, j] += np.array([color.x, color.y, color.z])

    # Average the samples
    color_buffer /= ss_factor ** 2

    # Convert to image
    image = Image.fromarray(np.clip(color_buffer * 255, 0, 255).astype(np.uint8))

    image.save("render.png")

main()