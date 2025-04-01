using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class ConfigManager : MonoBehaviour
{
    public static ConfigManager Instance { get; private set; }
    private const string FILE_NAME = "config.json";
    private string configFile;

    [System.Serializable]
    public class Config
    {
        public string ip;
        public int port;

        public override string ToString()
        {
            return $@"{{""ip"":""{ip}"", ""port"":{port}}}";
        }
    }

    private void Awake()
    {
        if (Instance != null)
        {
            Debug.LogError("Singleton");
            Destroy(gameObject);
        }
        Instance = this;
        configFile = Path.Combine(Application.dataPath, FILE_NAME);
    }

    public void SaveConfig(string ip, int port)
    {
        string content = $"{{\"ip\":\"{ip}\",\"port\":{port}}}";
        File.WriteAllText(configFile, content);
    }

    public void SaveConfig(Config config)
    {
        string content = JsonUtility.ToJson(config);
        File.WriteAllText(configFile, content);
    }

    public Config LoadConfig()
    {
        Config config = null;
        try
        {
            string content = File.ReadAllText(configFile);
            config = JsonUtility.FromJson<Config>(content);
        }catch
        {
            // do nothing
        }
        return config;
    }
}
