import bpy
import random
from mathutils import Vector

def distribute_and_duplicate_objects(area_min, area_max, num_duplicates, exclusion_zones=None, padding=0.1):
    """
    Duplicates selected objects and distributes them within a specified area.

    :param area_min: Vector - Minimum corner of the bounding box (x, y)
    :param area_max: Vector - Maximum corner of the bounding box (x, y)
    :param num_duplicates: int - Number of times each selected object is duplicated
    :param exclusion_zones: List of tuples [(Vector, Vector)] - Each tuple is (min_corner, max_corner)
    :param padding: float - Minimum distance between objects
    """
    selected_objects = bpy.context.selected_objects

    if not selected_objects:
        print("No objects selected.")
        return

    exclusion_zones = exclusion_zones or []
    positions = []

    # Use a grid-based optimization for faster collision checking
    grid_size = max((area_max - area_min).x, (area_max - area_min).y) / 100  # Adjust grid granularity as needed
    grid = {}

    def add_to_grid(pos, obj_dimensions):
        """Add object to the spatial grid for overlap checking."""
        grid_cell = (int(pos.x // grid_size), int(pos.y // grid_size))
        if grid_cell not in grid:
            grid[grid_cell] = []
        grid[grid_cell].append((pos, obj_dimensions))

    def is_valid_position(pos, obj_dimensions):
        """Check if position is outside exclusion zones and does not overlap with existing objects."""
        # Check exclusion zones
        for zone_min, zone_max in exclusion_zones:
            if (zone_min.x <= pos.x <= zone_max.x and
                zone_min.y <= pos.y <= zone_max.y):
                return False

        # Check overlap using the grid
        grid_cell = (int(pos.x // grid_size), int(pos.y // grid_size))
        neighbors = [(grid_cell[0] + dx, grid_cell[1] + dy) for dx in range(-1, 2) for dy in range(-1, 2)]
        for neighbor in neighbors:
            if neighbor in grid:
                for existing_pos, existing_dims in grid[neighbor]:
                    dist = (pos - existing_pos).length
                    min_dist = max(obj_dimensions.x, obj_dimensions.y) / 2 + \
                               max(existing_dims.x, existing_dims.y) / 2 + padding
                    if dist < min_dist:
                        return False

        return True

    for obj in selected_objects:
        obj_dimensions = obj.dimensions

        # Place the original object in a valid position
        for attempt in range(1000):
            rand_x = random.uniform(area_min.x, area_max.x)
            rand_y = random.uniform(area_min.y, area_max.y)
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
                rand_x = random.uniform(area_min.x, area_max.x)
                rand_y = random.uniform(area_min.y, area_max.y)
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
area_min = Vector((-27, -27))
area_max = Vector((27, 27))
num_duplicates = 10  # Number of duplicates per selected object
exclusion_zones = [
    (Vector((-15, -15)), Vector((17, 16)))  # Exclude a square in the middle
]

# Call the function to duplicate and distribute objects
distribute_and_duplicate_objects(area_min, area_max, num_duplicates, exclusion_zones)