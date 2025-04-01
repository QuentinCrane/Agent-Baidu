using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PositionManager : MonoBehaviour
{
    public static PositionManager Instance { get; private set; }

    [SerializeField] private List<InstancePosition> instancePositions;

    void Awake()
    {
        if (Instance != null)
        {
            Debug.LogError("Singleton");
            Destroy(gameObject);
        }
        Instance = this;
    }

    public Vector3? GetPositionByName(string name)
    {
        if (instancePositions == null) return null;
        for (int i = 0; i < instancePositions.Count; i++)
        {
            if (name == instancePositions[i].instanceName)
            {
                return instancePositions[i].GetPosition();
            }
        }
        return null;
    }
}

[System.Serializable]
public class InstancePosition
{
    public string instanceName;
    [SerializeField] private Transform position;

    public Vector3 GetPosition()
    {
        return position.position;
    }
}
