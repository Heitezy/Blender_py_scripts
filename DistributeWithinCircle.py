import bpy
import random
import math
from mathutils import Vector

def distribute_objects_in_area(area_center, area_radius, exclusion_zones=None, padding=0.1):
    """
    Distributes selected objects within a circular area.

    :param area_center: Vector - Center of the distribution circle (x, y, z)
    :param area_radius: float - Radius of the distribution circle
    :param exclusion_zones: List of tuples [(Vector, float)] - Each tuple is (center, radius) for exclusion zones
    :param padding: float - Minimum distance between objects
    """
    selected_objects = bpy.context.selected_objects

    if not selected_objects:
        print("No objects selected.")
        return

    exclusion_zones = exclusion_zones or []
    positions = []

    def is_valid_position(pos, obj_dimensions):
        # Check if position is inside the distribution circle
        if (pos - area_center).length > area_radius:
            return False

        # Check if position is outside exclusion zones
        for zone_center, zone_radius in exclusion_zones:
            if (pos - zone_center).length <= zone_radius:
                return False

        # Check for overlaps with existing objects
        for existing_pos, existing_dims in positions:
            dist = (pos.xy - existing_pos.xy).length
            min_dist = max(obj_dimensions.x, obj_dimensions.y) / 2 + \
                       max(existing_dims.x, existing_dims.y) / 2 + padding
            if dist < min_dist:
                return False

        return True

    for obj in selected_objects:
        obj_dimensions = obj.dimensions

        # Attempt to place the object in a valid position
        for attempt in range(1000):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, area_radius)
            rand_x = area_center.x + radius * math.cos(angle)
            rand_y = area_center.y + radius * math.sin(angle)
            position = Vector((rand_x, rand_y, area_center.z))

            if is_valid_position(position, obj_dimensions):
                positions.append((position, obj_dimensions))
                obj.location = position
                break
        else:
            print(f"Could not place object {obj.name} after 1000 attempts.")

# Example usage
area_center = Vector((0, 0, 0))
area_radius = 27
exclusion_zones = [
    (Vector((0, 0, 0)), 18)  # Exclude a circle in the middle with radius 18
]

# Call the function to distribute objects
distribute_objects_in_area(area_center, area_radius, exclusion_zones)
