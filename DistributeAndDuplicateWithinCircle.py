import bpy
import random
from math import pi, sqrt, sin, cos
from mathutils import Vector

def distribute_and_duplicate_objects(area_center, area_radius, num_duplicates, exclusion_zones=None, padding=0.1):
    """
    Duplicates selected objects and distributes them within a circular area.

    :param area_center: Vector - Center of the circular area
    :param area_radius: float - Radius of the circular area
    :param num_duplicates: int - Number of times each selected object is duplicated
    :param exclusion_zones: List of tuples [(Vector, float)] - Each tuple is (center, radius)
    :param padding: float - Minimum distance between objects
    """
    selected_objects = bpy.context.selected_objects

    if not selected_objects:
        print("No objects selected.")
        return

    exclusion_zones = exclusion_zones or []
    positions = []

    # Use a grid-based optimization for faster collision checking
    grid_size = area_radius / 50  # Adjust grid granularity as needed
    grid = {}

    def add_to_grid(pos, obj_dimensions):
        """Add object to the spatial grid for overlap checking."""
        grid_cell = (int(pos.x // grid_size), int(pos.y // grid_size))
        if grid_cell not in grid:
            grid[grid_cell] = []
        grid[grid_cell].append((pos, obj_dimensions))

    def is_valid_position(pos, obj_dimensions):
        """Check if position is outside exclusion zones and does not overlap with existing objects."""
        # Check if within the circular area
        if sqrt((pos.x - area_center.x) ** 2 + (pos.y - area_center.y) ** 2) > area_radius:
            return False

        # Check exclusion zones
        for zone_center, zone_radius in exclusion_zones:
            if sqrt((pos.x - zone_center.x) ** 2 + (pos.y - zone_center.y) ** 2) < zone_radius:
                return False

        # Check overlap using the grid
        grid_cell = (int(pos.x // grid_size), int(pos.y // grid_size))
        neighbors = [(grid_cell[0] + dx, grid_cell[1] + dy) for dx in range(-1, 2) for dy in range(-1, 2)]
        for neighbor in neighbors:
            if neighbor in grid:
                for existing_pos, existing_dims in grid[neighbor]:
                    dist = sqrt((pos.x - existing_pos.x) ** 2 + (pos.y - existing_pos.y) ** 2)
                    min_dist = max(obj_dimensions.x, obj_dimensions.y) / 2 + \
                               max(existing_dims.x, existing_dims.y) / 2 + padding
                    if dist < min_dist:
                        return False

        return True

    for obj in selected_objects:
        obj_dimensions = obj.dimensions

        # Place the original object in a valid position
        for attempt in range(1000):
            rand_angle = random.uniform(0, 2 * pi)
            rand_radius = sqrt(random.uniform(0, 1)) * area_radius
            rand_x = area_center.x + rand_radius * cos(rand_angle)
            rand_y = area_center.y + rand_radius * sin(rand_angle)
            position = Vector((rand_x, rand_y, 0))

            if is_valid_position(position, obj_dimensions):
                obj.location = position
                add_to_grid(position, obj_dimensions)
                break
        else:
            print(f"Could not place object {obj.name} after 1000 attempts.")

        # Duplicate the object
        for _ in range(num_duplicates):
            # Attempt to place the duplicate object in a valid position
            for attempt in range(1000):
                rand_angle = random.uniform(0, 2 * pi)
                rand_radius = sqrt(random.uniform(0, 1)) * area_radius
                rand_x = area_center.x + rand_radius * cos(rand_angle)
                rand_y = area_center.y + rand_radius * sin(rand_angle)
                position = Vector((rand_x, rand_y, 0))

                if is_valid_position(position, obj_dimensions):
                    # Duplicate the object
                    new_obj = obj.copy()
                    new_obj.location = position
                    bpy.context.collection.objects.link(new_obj)

                    # Add position to the spatial grid
                    add_to_grid(position, obj_dimensions)
                    break
            else:
                print(f"Could not place duplicate of object {obj.name} after 1000 attempts.")

# Example usage
area_center = Vector((0, 0, 0))
area_radius = 27
num_duplicates = 10  # Number of duplicates per selected object
exclusion_zones = [
    (Vector((0, 0, 0)), 10)  # Exclude a circle in the middle with radius 10
]

# Call the function to duplicate and distribute objects
distribute_and_duplicate_objects(area_center, area_radius, num_duplicates, exclusion_zones)
