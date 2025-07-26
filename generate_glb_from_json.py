import subprocess
import os
import bpy
import json
import bmesh
import random
from mathutils import Vector

# Step 2: Load the generated world JSON
json_path = os.path.join(os.path.dirname(__file__), "data/generated_world.json")
with open(json_path, "r") as f:
    scene = json.load(f)

# Step 3: Clear all existing objects in the Blender scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)



# Step 4: Create 3D objects in Blender from the JSON data
world_objects = []
def create_feature_and_keep(parent_object, feature, world_objects):
    """
    Create a feature object and keep it (no deletion).
    """
    pos = feature["position"]
    scale = feature["scale"]
    shape = feature.get("shape", "cube")
    color = feature.get("color", [0.8, 0.8, 0.8])

    loc_x = parent_object.location.x + pos[0]
    loc_y = parent_object.location.y + pos[1]
    loc_z = parent_object.location.z + pos[2]

    # Create based on shape
    if shape == "cube":
        bpy.ops.mesh.primitive_cube_add(location=(loc_x, loc_y, loc_z))
    elif shape == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(location=(loc_x, loc_y, loc_z))
    elif shape == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(location=(loc_x, loc_y, loc_z))
    elif shape == "cone":
        bpy.ops.mesh.primitive_cone_add(location=(loc_x, loc_y, loc_z))
    else:
        bpy.ops.mesh.primitive_cube_add(location=(loc_x, loc_y, loc_z))

    feature_obj = bpy.context.object
    feature_obj.scale = [max(0.01, s / 2) for s in scale]
    feature_obj.name = feature["type"]

    # Apply material
    mat = bpy.data.materials.new(name=f"{feature['type']}_mat")
    mat.diffuse_color = (*color, 1)
    feature_obj.data.materials.append(mat)

    # Add to world
    world_objects.append(feature_obj)

for obj in scene:
    pos = obj["position"]
    scale = obj["scale"]
    shape = obj.get("shape", "cube")
    color = obj.get("color", [0.5, 0.5, 0.5])

    scale = [max(0.01, s / 2) for s in scale]  # Normalize scale (Blender's default cube is size 2)

    # Create primitive mesh based on shape type
    if shape == "cube":
        bpy.ops.mesh.primitive_cube_add(location=pos)
    elif shape == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(location=pos)
    elif shape == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(location=pos)
    elif shape == "cone":
        bpy.ops.mesh.primitive_cone_add(location=pos)
    elif shape == "plane":
        bpy.ops.mesh.primitive_plane_add(location=pos)
    else:
        bpy.ops.mesh.primitive_cube_add(location=pos)  # Default fallback

    obj3d = bpy.context.object
    obj3d.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True) 
    obj3d.name = obj["type"]

    # Add material with color
    mat = bpy.data.materials.new(name=f"{obj['type']}_mat")
    mat.diffuse_color = (*color, 1)  # RGBA
    obj3d.data.materials.append(mat)

    world_objects.append(obj3d)
    if "features" in obj:
        for feature in obj["features"]:
            create_feature_and_keep(obj3d, feature, world_objects)

def bbox(obj):
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_corner = Vector(map(min, zip(*bbox_corners)))
    max_corner = Vector(map(max, zip(*bbox_corners)))
    return min_corner, max_corner

def boxes_intersect(box1, box2):
    min1, max1 = box1
    min2, max2 = box2
    for i in range(3):
        if max1[i] <= min2[i] or min1[i] >= max2[i]:
            return False
    return True

def update_position(obj1, obj2):
    padding = 0.1 # Small extra gap

    box1_min, box1_max = bbox(obj1)
    box2_min, box2_max = bbox(obj2)

    size2 = box2_max - box2_min  # Size of obj2

    # Move obj2 just to the right of obj1
    new_x = box1_max.x + size2.x / 2 + padding
    new_y = obj2.location.y  # Keep Y the same
    new_z = obj2.location.z  # Keep Z the same

    obj2.location = Vector((new_x, new_y, new_z))
    bpy.context.view_layer.update()


world_objects.sort(key=lambda obj: obj.location.x)
for i in range(len(world_objects)):
    for j in range(i + 1, len(world_objects)):
        obj1 = world_objects[i]
        obj2 = world_objects[j]
        print(obj1.name,bbox(obj1),obj2.name,bbox(obj2))
        if boxes_intersect(bbox(obj1), bbox(obj2)):
            print(f" Intersection between {obj1.name} and {obj2.name}")
            iteration = 0
            print(bbox(obj1),bbox(obj2))
            print(obj2.scale)
            while boxes_intersect(bbox(obj1), bbox(obj2)):
                update_position(obj1, obj2)
                iteration += 1
                if iteration > 50:
                    print(f"Gave up fixing {obj2.name} vs {obj1.name}")
                    print(bbox(obj1),bbox(obj2))
                    #obj2.location= Vector((3,3,3))
                    #bpy.context.view_layer.update()
                    #print(bbox(obj1),bbox(obj2))
                    #print(obj2.location)
                    break
    
            print(bbox(obj1),bbox(obj2))
            print(obj2.scale)
    #all the objects in world_sorted[i:] have removed their intersections
    world_objects[i+1:] = sorted(world_objects[i+1:], key=lambda obj: obj.location.x)

# Step 5: Export the scene as a GLB file
output_path = os.path.join(os.path.dirname(__file__), "generated_world.fbx")
bpy.ops.export_scene.fbx(filepath=output_path)

