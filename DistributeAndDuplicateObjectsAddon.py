bl_info = {
    "name": "Object Distribution and Duplication",
    "blender": (2, 80, 0),
    "category": "Object",
    "version": (1, 1, 0),
    "author": "heitezy",
    "description": "Distribute selected objects within specified square or circle area with customizable exclusion zones, duplication option and adjustable padding.",
}

import bpy
import random
from math import pi, sqrt, sin, cos
from mathutils import Vector

def distribute_and_duplicate_objects(area_center, area_size, zone_center, zone_size, num_duplicates, padding=0.1, is_circle=True, distribute_only=False):
    """
    Distributes and optionally duplicates selected objects within a specified area.

    :param area_center: Vector - Center of the area
    :param area_size: float or tuple (float, float) - Size of the area (radius for circle, (width, height) for square)
    :param num_duplicates: int - Number of times each selected object is duplicated
    :param exclusion_zones: List of tuples - [(center, size, is_circle)]
    :param padding: float - Minimum distance between objects
    :param is_circle: bool - True for circular area, False for square area
    :param distribute_only: bool - If True, only distribute without duplicating
    """
    selected_objects = bpy.context.selected_objects

    if not selected_objects:
        print("No objects selected.")
        return

    positions = []

    def is_inside_area(pos):
        if is_circle:
            return (pos - area_center).length <= area_size
        else:
            half_width, half_height = area_size[0] / 2, area_size[1] / 2
            return (area_center.x - half_width <= pos.x <= area_center.x + half_width and
                    area_center.y - half_height <= pos.y <= area_center.y + half_height)

    def is_inside_exclusion_zone(pos):
        if is_circle:
            if (pos - zone_center).length < zone_size:
                return True
        else:
            half_width, half_height = zone_size[0] / 2, zone_size[1] / 2
            if (zone_center.x - half_width <= pos.x <= zone_center.x + half_width and
                    zone_center.y - half_height <= pos.y <= zone_center.y + half_height):
                return True
        return False

    def is_valid_position(pos, obj_dimensions):
        if not is_inside_area(pos):
            return False
        if is_inside_exclusion_zone(pos):
            return False

        for existing_pos, existing_dims in positions:
            dist = (pos - existing_pos).length
            min_dist = max(obj_dimensions.x, obj_dimensions.y) / 2 + \
                       max(existing_dims.x, existing_dims.y) / 2 + padding
            if dist < min_dist:
                return False

        return True

    def random_position():
        if is_circle:
            rand_angle = random.uniform(0, 2 * pi)
            rand_radius = sqrt(random.uniform(0, 1)) * area_size
            return Vector((area_center.x + rand_radius * cos(rand_angle),
                           area_center.y + rand_radius * sin(rand_angle),
                           0))
        else:
            half_width, half_height = area_size[0] / 2, area_size[1] / 2
            rand_x = random.uniform(area_center.x - half_width, area_center.x + half_width)
            rand_y = random.uniform(area_center.y - half_height, area_center.y + half_height)
            return Vector((rand_x, rand_y, 0))

    for obj in selected_objects:
        obj_dimensions = obj.dimensions

        for attempt in range(1000):
            position = random_position()
            if is_valid_position(position, obj_dimensions):
                obj.location = position
                positions.append((position, obj_dimensions))
                break
        else:
            print(f"Could not place object {obj.name} after 1000 attempts.")

        if distribute_only:
            continue

        for _ in range(num_duplicates):
            for attempt in range(1000):
                position = random_position()
                if is_valid_position(position, obj_dimensions):
                    new_obj = obj.copy()
                    new_obj.location = position
                    bpy.context.collection.objects.link(new_obj)
                    positions.append((position, obj_dimensions))
                    break
            else:
                print(f"Could not place duplicate of object {obj.name} after 1000 attempts.")

class OBJECT_OT_DistributeAndDuplicate(bpy.types.Operator):
    """Distribute and Duplicate Objects"""
    bl_idname = "object.distribute_and_duplicate"
    bl_label = "Distribute and Duplicate Objects"
    bl_options = {'REGISTER', 'UNDO'}

    distribute_only: bpy.props.BoolProperty(
        name="Distribute Only",
        default=True,
        description="If enabled, only distribute objects without duplication"
    )

    area_form: bpy.props.EnumProperty(
        name="Area Form",
        items=[('CIRCLE', "Circle", "Use a circular area"),
               ('SQUARE', "Square", "Use a square area")],
        default='CIRCLE',
        description="Shape of the distribution area"
    )

    area_radius: bpy.props.FloatProperty(
        name="Area Radius",
        default=10.0,
        min=0.1,
        description="Radius of the circular area (used if Area Form is Circle)"
    )

    area_width: bpy.props.FloatProperty(
        name="Area Width",
        default=10.0,
        min=0.1,
        description="Width of the square area (used if Area Form is Square)"
    )

    area_height: bpy.props.FloatProperty(
        name="Area Height",
        default=10.0,
        min=0.1,
        description="Height of the square area (used if Area Form is Square)"
    )

    num_duplicates: bpy.props.IntProperty(
        name="Number of Duplicates",
        default=2,
        min=0,
        description="Number of duplicates for each selected object"
    )

    padding: bpy.props.FloatProperty(
        name="Padding",
        default=0.1,
        min=0.0,
        description="Minimum distance between objects"
    )

    exclusion_zone_radius: bpy.props.FloatProperty(
        name="Exclusion Zone Radius",
        default=3.0,
        min=0.1,
        description="Radius of the circular exclusion zone (used if Exclusion Zone Form is Circle)"
    )

    exclusion_zone_width: bpy.props.FloatProperty(
        name="Exclusion Zone Width",
        default=3.0,
        min=0.1,
        description="Width of the square exclusion zone (used if Exclusion Zone Form is Square)"
    )

    exclusion_zone_height: bpy.props.FloatProperty(
        name="Exclusion Zone Height",
        default=3.0,
        min=0.1,
        description="Height of the square exclusion zone (used if Exclusion Zone Form is Square)"
    )

    def execute(self, context):
        zone_center = Vector((0, 0, 0))  # Replace with user input or default positions
        zone_size = self.exclusion_zone_radius if self.area_form == 'CIRCLE' else (self.exclusion_zone_width, self.exclusion_zone_height)

        area_center = Vector((0, 0, 0))  # Center is assumed at origin for now
        area_size = self.area_radius if self.area_form == 'CIRCLE' else (self.area_width, self.area_height)
        distribute_and_duplicate_objects(area_center, area_size, zone_center, zone_size, self.num_duplicates, self.padding, self.area_form == 'CIRCLE', self.distribute_only)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_DistributeAndDuplicate.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_DistributeAndDuplicate)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_DistributeAndDuplicate)

if __name__ == "__main__":
    register()
