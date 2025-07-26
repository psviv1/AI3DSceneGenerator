def validate(world_json):
    # Simplified logic check
    if "floating island" in world_json and "underground tunnel" in world_json:
        return False, "Incompatible features: floating + underground"
    return True, "Valid world"
