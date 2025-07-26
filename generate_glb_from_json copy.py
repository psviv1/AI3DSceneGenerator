import subprocess
import os
import bpy
import json
from mathutils import Vector
# ✅ Call external Python to generate the world
python_path = r"C:\Users\psviv\.pyenv\pyenv-win\versions\3.12.0\python.exe"  # <- your working Python
script_path = os.path.join(os.path.dirname(__file__), "ai_generate_world.py")
subprocess.run([python_path, script_path])
# Step 2: Load the generated world JSON
json_path = os.path.join(os.path.dirname(__file__), "data/generated_world.json")
with open(json_path, "r") as f:
    scene = json.load(f)

# Step 3: Clear all existing objects in the Blender scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
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

def update_position(obj):
    step = 0.5
    obj.location.x += step
    return
world_objects = []
# Step 4: Create 3D objects in Blender from the JSON data
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
    else:
        bpy.ops.mesh.primitive_cube_add(location=pos)  # Default fallback

    obj3d = bpy.context.object
    obj3d.scale = scale
    obj3d.name = obj["type"]

    # Add material with color
    mat = bpy.data.materials.new(name=f"{obj['type']}_mat")
    mat.diffuse_color = (*color, 1)  # RGBA
    obj3d.data.materials.append(mat)

    world_objects.append((obj3d, shape))
    

for i in range(len(world_objects)):
    for j in range(i + 1, len(world_objects)):
        obj1, shape1 = world_objects[i]
        obj2, shape2 = world_objects[j]

        is2d_1 = shape1 in ["plane"]
        is2d_2 = shape2 in ["plane"]

        box1 = bbox(obj1)
        box2 = bbox(obj2)
        if boxes_intersect(box1, box2, is2d_1, is2d_2):
            while not update_position(box1,box2):
                continue

# Step 5: Export the scene as a GLB file
output_path = os.path.join(os.path.dirname(__file__), "generated_world.fbx")
bpy.ops.export_scene.fbx(filepath=output_path)
