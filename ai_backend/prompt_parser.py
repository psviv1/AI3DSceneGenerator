
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY") 
llm = OpenAI(temperature=0,api_key=OPENAI_KEY)

prompt_template = PromptTemplate.from_template("""
You are a Unity 3D world-building assistant.

Given a user prompt describing a scene, return a structured JSON array of objects to be placed in Unity.

Each object must have:
- "type": the object type (e.g., "house", "tree", "road", "farm")
- "position": [x, y, z] coordinates (center point)
- "scale": [width, height, depth]
- Optionally:
  - "rotation": [x, y, z] in degrees
  - "features": list of features (only for certain objects, like buildings which have accessories like windows, doors, etc, don't include if prompt doesn't mention these accessories)

Each feature (if present) must have:
- "type": a short label for the feature (examples: "window", "door", "frame", "sign", "balcony", etc.)
- "position": [relative x, y, z] coordinates from the object's center
- "scale": [width, height, depth]

Strict rules you must follow:
- If the prompt describes an object as **being on** another object (e.g., "house on a farm" or "tree on ground"), you must set:
  - The **bottom face** of the object (position[2] - scale[2]/2) **equal** to the **top face** of the surface (position[2] + scale[2]/2).
  - The vertical axis is **Z** (not Y).
- If an object is described as **left of** another object, its **x-coordinate must be less** than the other object's x-coordinate.
- If an object is described as **right of** another object, its **x-coordinate must be greater**.
- If an object is described as **above** another object, its **z-coordinate must be greater**.
- If an object is described as **below** another object, its **z-coordinate must be less**.
- Flat surfaces like farms, grounds, and planes should have a **very small height** (e.g., 0.1) and large width/depth.
- Houses and buildings **may** (but do not have to) include features like windows, doors, balconies, etc.
-- If a **feature** (window, door, frame, etc) is attached to a **parent** object:
  - The **X-scale** (width) must be very small (e.g., 0.1).
  - The **feature's X-center** should match parent[0] + parent[0]/2 
                                               
Only output the JSON array.
No extra explanation, no comments, no natural language.

Example output:

[
  {{
    "type": "farm",
    "position": [0, 0, 0],
    "scale": [50, 50, 0.1]
  }},
  {{
    "type": "house",
    "position": [10, 10, 5.05],
    "scale": [10, 10, 10],
    "features": [
      {{
        "type": "door",
        "position": [5.05, -4, 0],   // move to front face (parent X + parent.width/2)
        "scale": [0.1, 4, 2]         // thin X (0.1), height=4, width=2
      }},
      {{
        "type": "window",
        "position": [5.05, 2, 0],    // move to front face (same X)
        "scale": [0.1, 1, 1]         // thin X (0.1), height=1, width=1
      }}
    ]
  }}
]

Prompt: {user_prompt}
""")


def parse_prompt(user_prompt):
    prompt = prompt_template.format(user_prompt=user_prompt)
    response = llm.invoke(prompt)
    print(response)
    return response
