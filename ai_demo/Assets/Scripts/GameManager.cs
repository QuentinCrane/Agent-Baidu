using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    [SerializeField] private UnitySocketClient unitySocketClient;

    private GameObject[] npcArray;
    public GameObject[] NpcArray { get { return npcArray; } }

    private int workDoneCount = 0;
    private int workerCount = 0;

    void Awake()
    {
        if (Instance != null)
        {
            Debug.LogError("Singleton");
            Destroy(gameObject);
        }
        Instance = this;

        npcArray = GameObject.FindGameObjectsWithTag("NPC");
    }

    void OnEnable()
    {
        UIManager.NewTaskSubmitHandler += OnSubmitTask;
        RegisterNpcWorkDoneHandler();
    }

    void OnDisable()
    {
        UIManager.NewTaskSubmitHandler -= OnSubmitTask;
        UnregisterNpcWorkDoneHandler();
    }

    private void RegisterNpcWorkDoneHandler()
    {
        if (npcArray == null) return;

        for (int i = 0; i < npcArray.Length; i++)
        {
            if (!npcArray[i].TryGetComponent<NpcController>(out var controller)) continue;
            controller.WorkDoneHandler += OnNpcWorkDone;
            controller.StartWorkHandler += OnNpcStartWork;
        }
    }

    private void UnregisterNpcWorkDoneHandler()
    {
        if (npcArray == null) return;

        try
        {
            for (int i = 0; i < npcArray.Length; i++)
            {
                if (!npcArray[i].TryGetComponent<NpcController>(out var controller)) continue;
                controller.WorkDoneHandler -= OnNpcWorkDone;
                controller.StartWorkHandler -= OnNpcStartWork;
            }
        }
        catch
        {
            // do nothing
        }
    }

    private void OnNpcStartWork()
    {
        workerCount++;
    }

    private void OnNpcWorkDone()
    {
        workDoneCount++;

        if (workDoneCount == workerCount)
        {
            // task is done
            SubmitOrContinueTask(new FunctionCallRespone(TypeFieldDefs.TASK_CONTINUE, true));
        }
    }

    private void OnSubmitTask(string task)
    {
        SubmitOrContinueTask(new FunctionCallRespone(TypeFieldDefs.TASK_NEW, task));
    }

    private void SubmitOrContinueTask(FunctionCallRespone data)
    {
        workerCount = 0;
        workDoneCount = 0;
        unitySocketClient.SendDataToServer(data);
    }
}
