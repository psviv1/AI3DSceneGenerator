import numpy as np

def generate_terrain(features):
    terrain = {"vertices": [], "edges": [], "features": []}
    if "floating island" in features:
        terrain["features"].append("generate island mesh")
    if "waterfall" in features:
        terrain["features"].append("add downward flowing stream")
    # Add Voronoi, L-system, etc. later
    return terrain
