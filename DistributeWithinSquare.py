import bpy
import random
from mathutils import Vector

def distribute_objects_in_area(area_min, area_max, exclusion_zones=None, padding=0.1):
    """
    Distributes selected objects within a specified area.

    :param area_min: Vector - Minimum corner of the bounding box (x, y)
    :param area_max: Vector - Maximum corner of the bounding box (x, y)
    :param exclusion_zones: List of tuples [(Vector, Vector)] - Each tuple is (min_corner, max_corner)
    :param padding: float - Minimum distance between objects
    """
    selected_objects = bpy.context.selected_objects

    if not selected_objects:
        print("No objects selected.")
        return

    exclusion_zones = exclusion_zones or []
    positions = []

    def is_valid_position(pos, obj_dimensions):
        # Check if position is outside exclusion zones and does not overlap with existing objects
        for zone_min, zone_max in exclusion_zones:
            if (zone_min.x <= pos.x <= zone_max.x and
                zone_min.y <= pos.y <= zone_max.y):
                return False

        for existing_pos, existing_dims in positions:
            dist = (pos - existing_pos).length
            min_dist = max(obj_dimensions.x, obj_dimensions.y) / 2 + \
                       max(existing_dims.x, existing_dims.y) / 2 + padding
            if dist < min_dist:
                return False

        return True

    for obj in selected_objects:
        obj_dimensions = obj.dimensions

        # Attempt to place the object in a valid position
        for attempt in range(1000):
            rand_x = random.uniform(area_min.x, area_max.x)
            rand_y = random.uniform(area_min.y, area_max.y)
            position = Vector((rand_x, rand_y, 0))

            if is_valid_position(position, obj_dimensions):
                positions.append((position, obj_dimensions))
                obj.location = position
                break
        else:
            print(f"Could not place object {obj.name} after 1000 attempts.")

# Example usage
area_min = Vector((-27, -27))
area_max = Vector((27, 27))
exclusion_zones = [
    (Vector((-15, -15)), Vector((17, 16)))  # Exclude a square in the middle
]

# Call the function to distribute objects
distribute_objects_in_area(area_min, area_max, exclusion_zones)