using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.IO;
using UnityEngine;

public class UnitySocketClient : MonoBehaviour
{
    [SerializeField] private string serverAddress = "127.0.0.1";
    [SerializeField] private int serverPort = 12340;
    private TcpClient client;
    private NetworkStream stream;

    private bool receiving = false;
    private StringBuilder receiveData;

    public static event Action<TaskResult> OnTaskReceiveHandler;

    /// <summary>
    /// Awake is called when the script instance is being loaded.
    /// </summary>
    void Awake()
    {
        receiveData = new StringBuilder();
        var config = ConfigManager.Instance.LoadConfig();
        if (config != null)
        {
            serverAddress = config.ip;
            serverPort = config.port;
        }
    }

    private void Start()
    {
        ConnectToServer();
    }

    public async void ConnectToServer()
    {
        try
        {
            client = new TcpClient();
            await client.ConnectAsync(serverAddress, serverPort);
            stream = client.GetStream();
            Debug.Log("Connected to server.");
        }
        catch (Exception e)
        {
            Debug.LogError("Error: " + e.Message);
            TipUI.TipError("连接大模型失败");
        }
    }

    public void Update()
    {
        //SendDataToServer("Hello from Unity!");
        ReceiveDataFromServer();
    }

    public void SendDataToServer(FunctionCallRespone sendData)
    {
        if (stream == null)
        {
            Debug.LogError("Not connected to the server.");
            TipUI.TipError("任务提交失败，尚未连接大模型");
            return;
        }
        string json = JsonUtility.ToJson(sendData);
        Debug.Log("send data: " + json);
        byte[] data = Encoding.UTF8.GetBytes(json);
        stream.Write(data, 0, data.Length);
        if (sendData.type == TypeFieldDefs.TASK_NEW)
        {
            TipUI.TipNormal("任务提交成功");
        }
    }

    public void ReceiveDataFromServer()
    {
        if (stream == null)
        {
            //Debug.LogError("Not connected to the server.");
            return;
        }

        if (stream.DataAvailable)
        {
            try
            {
                receiving = true;

                byte[] data = new byte[1024];
                int bytesRead = stream.Read(data, 0, data.Length);
                string receivedMessage = Encoding.UTF8.GetString(data, 0, bytesRead);
                // File.WriteAllText(recvfilePath, receivedMessage);
                if (string.IsNullOrEmpty(receivedMessage)) return;
                receiveData.Append(receivedMessage);
            }
            catch (Exception e)
            {
                Debug.LogError("receiveDataFromServer error: " + e);
            }
        }
        else if (receiving)
        {
#if UNITY_EDITOR
            Debug.Log(receiveData.ToString());
#endif
            TaskResult result = JsonUtility.FromJson<TaskResult>(receiveData.ToString());
            OnTaskReceiveHandler?.Invoke(result);
            receiveData.Clear();
            receiving = false;
        }
    }

    public void OnDestroy()
    {
        client?.Close();
    }
}

public class TypeFieldDefs
{
    public const string TASK_NEW = "question";
    public const string TASK_CONTINUE = "response";
    public const string RESULT_TASK = "task";
    public const string RESULT_CLOSING_REPORT = "closingReport";
}

[Serializable]
public class FunctionCallRespone
{
    public string type;
    public string question;
    public bool response;

    public FunctionCallRespone(string type, string question)
    {
        this.type = type;
        this.question = question;
    }

    public FunctionCallRespone(string type, bool response)
    {
        this.type = type;
        this.response = response;
    }
}

[Serializable]
public class TaskResult
{
    public string resultType;

    public string closingReport;

    public string task;
    public int process;
    public int time;
    public List<NpcTaskResult> tasks;

    public override string ToString()
    {
        StringBuilder sb = new();
        if (resultType == TypeFieldDefs.RESULT_TASK)
        {
            sb.Append("{\n");
            sb.Append("  \"task\": ");
            sb.Append(task);
            sb.Append(",\n  \"process\": ");
            sb.Append(process);
            sb.Append(",\n  \"time\": ");
            sb.Append(time);
            sb.Append(",\n  \"tasks\": [");
            if (tasks != null)
            {
                for (int i = 0; i < tasks.Count; i++)
                {
                    sb.Append("    {\"name\": ");
                    sb.Append(tasks[i].name);
                    sb.Append(", ");
                    sb.Append(tasks[i].do_);
                    sb.Append("},\n");
                }
            }
            sb.Append("]\n}\n");
        }
        else if (resultType == TypeFieldDefs.RESULT_CLOSING_REPORT)
        {
            sb.Append("closingReport:\n");
            sb.Append(closingReport);
        }
        else
        {
            sb.Append("error closingReport field.");
        }
        return sb.ToString();
    }
}

[Serializable]
public class NpcTaskResult
{
    public string name;
    public string position;
    public string to;
    public string do_;
    public string emoji;

    public override string ToString()
    {
        return $"{{\n  name: \"{name}\",\n  position: \"{position}\",\n  to: \"{to}\",\n  do_: \"{do_}\",\n  emoji: {emoji}\n}}";
    }
}
