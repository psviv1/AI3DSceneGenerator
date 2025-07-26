from langchain.llms import OpenAI
from langchain.prompts import ChatPromptTemplate
import json
from dotenv import load_dotenv
import os
import random
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
prompt = ChatPromptTemplate.from_template("""
You are a 3D modeling assistant. Given an object type, respond with a valid JSON object with two keys:
- "shape" (choose from: plane, cube, sphere, cylinder, cone)
- "color" (an RGB list of 3 floats between 0 and 1)

Choose "plane" if the object is flat like ground, floor, or farm.

Only return the JSON. No extra explanation.

Example format:
{{
  "shape": "cube",
  "color": [0.5, 0.5, 0.5]
}}

Now, describe:
Object type: "{object_type}"            
""")

llm = OpenAI(temperature=0, api_key=OPENAI_KEY)

"""scene = [
    {"type": "robot", "position": [0, 0, 0], "scale": [1, 2, 1]},
    {"type": "tree", "position": [5, 0, 0], "scale": [2, 4, 2]},
]"""
def needs_expansion(object_type):
    """
    Determine if this object represents a cluster (like 'forest', 'neighborhood', etc.)
    """
    cluster_prompt = f"""
    You are a 3D world-building assistant.

    For the following object type, determine if it represents a group (cluster) of many similar items.

    Examples:
    - 'forest' → yes
    - 'neighborhood' → yes
    - 'city' → yes
    - 'house' → no
    - 'tree' → no
    - 'river' → no
    - 'car' → no

    Object: "{object_type}"

    Answer only "yes" or "no".
    """
    response = llm.invoke(cluster_prompt).strip().lower()
    return response == "yes"
def group_same_type_objects(scene, group_radius=15):
    """
    Move objects of the same type closer together but stay inside the farm boundaries.
    """
    # Find parent surface (e.g., farm)
    parent = None
    for obj in scene:
        if obj["type"] in ["farm", "ground", "plane"]:
            parent = obj
            break

    if not parent:
        print(" No farm/ground found! Cannot constrain clustering.")
        return

    parent_center_x, parent_center_y, parent_center_z = parent["position"]
    parent_width, parent_height, parent_depth = parent["scale"]

    parent_min_x = parent_center_x - parent_width / 2
    parent_max_x = parent_center_x + parent_width / 2
    parent_min_y = parent_center_y - parent_height / 2
    parent_max_y = parent_center_y + parent_height / 2

    type_to_indexes = {}

    # Group indexes by type
    for idx, obj in enumerate(scene):
        obj_type = obj["type"]
        type_to_indexes.setdefault(obj_type, []).append(idx)

    for obj_type, indexes in type_to_indexes.items():
        if len(indexes) > 1:
            # Choose a random cluster center **inside farm bounds**
            center_x = random.uniform(parent_min_x + group_radius, parent_max_x - group_radius)
            center_y = random.uniform(parent_min_y + group_radius, parent_max_y - group_radius)

            for idx in indexes:
                obj = scene[idx]
                obj["position"][0] = center_x + random.uniform(-group_radius, group_radius)
                obj["position"][1] = center_y + random.uniform(-group_radius, group_radius)
                # Keep depth (Z) unchanged

                # 🛡️ Extra safeguard: clamp inside farm bounds
                obj["position"][0] = max(parent_min_x, min(obj["position"][0], parent_max_x))
                obj["position"][1] = max(parent_min_y, min(obj["position"][1], parent_max_y))

    print("Grouped same types INSIDE parent farm bounds.")
with open("data/generated_world.json", "r") as f:
    scene = json.load(f)
print(scene)
for obj in scene:
    messages = prompt.format_messages(object_type=obj["type"])
    response = llm.invoke(messages)
    #result = json.loads(response.content)
    print("response:" ,response)
    info = json.loads(response)
    obj["shape"] = info.get("shape", "cube")
    obj["color"] = info.get("color", [0.5, 0.5, 0.5])
    #feature handling
    if "features" in obj:
        for feature in obj["features"]:
            messages = prompt.format_messages(object_type=feature["type"])
            response = llm.invoke(messages)
            print("response feature:", response)
            feature_info = json.loads(response)

            feature["shape"] = feature_info.get("shape", "cube")
            feature["color"] = feature_info.get("color", [0.5, 0.5, 0.5])


group_same_type_objects(scene)

with open("data/generated_world.json", "w") as f:
    json.dump(scene, f, indent=2)

print("World JSON generated with shapes/colors")
