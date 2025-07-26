using System.Collections.Generic;
using UnityEngine;
using System.IO;

[System.Serializable]
public class WorldObject
{
    public string type;
    public Vector3 position;
    public Vector3 scale;
}

[System.Serializable]
public class WorldObjectList
{
    public List<WorldObject> objects;
}

public class WorldLoader : MonoBehaviour
{
    public GameObject groundPrefab;
    public GameObject lakePrefab;
    public GameObject treePrefab;
    public GameObject housePrefab;

    void Start()
    {
        TextAsset jsonFile = Resources.Load<TextAsset>("generated_world");
        if (jsonFile == null)
        {
            Debug.LogError("JSON file not found!");
            return;
        }

        string json = "{\"objects\":" + jsonFile.text + "}"; // wrap for array
        WorldObjectList world = JsonUtility.FromJson<WorldObjectList>(json);

        foreach (WorldObject obj in world.objects)
        {
            GameObject go = CreatePrimitiveForType(obj.type);
            go.transform.position = obj.position;
            go.transform.localScale = obj.scale;
        }
    }

    GameObject GetPrefab(string type)
    {
        switch (type.ToLower())
        {
            case "ground": return groundPrefab;
            case "lake": return lakePrefab;
            case "tree": return treePrefab;
            case "house": return housePrefab;
            default:
                Debug.LogWarning("Unknown type: " + type);
                return null;
        }
    }
    GameObject CreatePrimitiveForType(string type)
    {
        switch (type.ToLower())
        {
            case "ground":
            case "house":
            case "lot":
                return GameObject.CreatePrimitive(PrimitiveType.Cube);
            case "lake":
                var lake = GameObject.CreatePrimitive(PrimitiveType.Cube);
                lake.GetComponent<Renderer>().material.color = Color.blue;
                return lake;
            case "tree":
                return GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            default:
                Debug.LogWarning("Unknown type: " + type);
                return GameObject.CreatePrimitive(PrimitiveType.Cube);
        }
    }

}
