# Flask API to convert JSON scene into .glb using Blender
from flask import Flask, request, send_file
import json
import subprocess
import os

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_world():
    scene = request.json

    # Save JSON to disk
    with open("generated_world.json", "w") as f:
        json.dump(scene, f)

    # Call Blender to generate the .glb (assumes generate_glb_from_json.py is in the same folder)
    subprocess.run([
        "blender", "--background", "--python", "generate_glb_from_json.py"
    ])

    # Return the generated .glb file
    return send_file("generated_world.glb", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
