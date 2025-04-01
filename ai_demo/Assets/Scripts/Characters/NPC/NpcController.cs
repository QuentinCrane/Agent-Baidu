using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class NpcController : CharacterController
{
    private float stayTime = 0;
    private Command lastCommand = CommandFactory.GetEmptyCommand();
    private readonly List<Command> commandQueue = new();

    private Sprite sprite;

    private NpcTaskResult npcTaskResult;

    public event Action WorkDoneHandler;
    public event Action StartWorkHandler;

    //                      isDisplay info         displayTime
    public event Action<bool, Sprite, NpcTaskResult, float> BodyIsClickedHandler;
    [SerializeField] private float displayFullMessageTime = 5f;
    private bool isDisplay = false;

    [SerializeField] private NPCAI npcAi;

    protected override void Awake()
    {
        base.Awake();
        if (transform.Find("Sprite").TryGetComponent<SpriteRenderer>(out var spriteRenderer))
        {
            sprite = spriteRenderer.sprite;
        }

        npcTaskResult = new()
        {
            name = characterName,
            position = "无",
            do_ = "无"
        };
    }

    void OnEnable()
    {
        UnitySocketClient.OnTaskReceiveHandler += OnTaskReceive;
        npcAi.OnArrivalHandler += OnArrival;
    }

    void OnDisable()
    {
        UnitySocketClient.OnTaskReceiveHandler -= OnTaskReceive;
        npcAi.OnArrivalHandler -= OnArrival;
    }

    void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Player") && other.isTrigger)
        {
            isDisplay = !isDisplay;
            BodyIsClickedHandler?.Invoke(isDisplay, sprite, npcTaskResult, -1);
        }
    }

    void OnTriggerExit2D(Collider2D other)
    {
        if (other.CompareTag("Player") && other.isTrigger)
        {
            isDisplay = !isDisplay;
            BodyIsClickedHandler?.Invoke(isDisplay, sprite, npcTaskResult, -1);
        }
    }

    private void OnMouseDown()
    {
        BodyIsClickedHandler?.Invoke(isDisplay, sprite, npcTaskResult, displayFullMessageTime);
        if (isDisplay)
        {
            CloseDialogMessage();
            Invoke(nameof(ShowDialogMessage), displayFullMessageTime);
        }
        else
        {
            CancelInvoke(nameof(ShowDialogMessage));
            ShowDialogMessage();
        }
        isDisplay = !isDisplay;
    }

    protected override Command HandleCommand()
    {
        if (stayTime > 0)
        {
            stayTime -= Time.deltaTime;
            return lastCommand;
        }
        if (commandQueue.Count == 0)
        {
            lastCommand = CommandFactory.GetEmptyCommand();
            return lastCommand;
        }

        Command command = commandQueue[0];
        commandQueue.RemoveAt(0);
        lastCommand = command;
        // TODO ��������ִ��ʱ��
        if (command is not DialogCommand && command is not CloseDialogCommand)
            stayTime = 1f;

        return command;
    }

    private void OnTaskReceive(TaskResult result)
    {
        if (result == null || result.resultType != TypeFieldDefs.RESULT_TASK) return;

        foreach (var npcTask in result.tasks)
        {
            if (characterName != npcTask.name) continue;

            SetDialogMessage(npcTask.emoji.ToUTF32());
            npcTaskResult = npcTask;
            var position = PositionManager.Instance.GetPositionByName(npcTask.to);
            if (position.HasValue)
            {
                npcAi.SetTargetPos(position.Value);
                StartWorkHandler?.Invoke();
            }
            else
            {
                Debug.LogError($"[{characterName}]没有找到要去的地方[{npcTask.to}]");
                TipUI.TipError($"[{characterName}]没有找到要去的地方[{npcTask.to}]");
            }
            break;
        }
    }

    private void OnArrival()
    {
        StartCoroutine(GoWork());
    }

    private IEnumerator GoWork()
    {
        float workTime = 2f;

        while (workTime > 0)
        {
            yield return null;
            workTime -= Time.deltaTime;
        }
        WorkDoneHandler?.Invoke();
    }

    public void SubmitCommands(params Command[] commands)
    {
        if (commands == null) return;
        commandQueue.AddRange(commands);
    }
}
