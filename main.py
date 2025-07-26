import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_backend.prompt_parser import parse_prompt
from geometry.terrain import generate_terrain
from ai_backend.validator import validate

def main():
    prompt = input("Describe your world: ")
    parsed = parse_prompt(prompt)
    parsed_json = json.loads(parsed)

    #valid, msg = validate(parsed_json["features"])
    """if not valid:
        print(" Error:", msg)
        return"""

    #world = generate_terrain(parsed_json["features"])
    world=parsed_json
    with open("data/generated_world.json", "w") as f:
        json.dump(world, f, indent=2)

    print("World generated and saved!")

if __name__ == "__main__":
    main()
