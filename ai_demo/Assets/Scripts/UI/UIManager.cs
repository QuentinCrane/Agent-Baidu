using System;
using System.Text;
using UnityEngine;
using UnityEngine.UI;

public class UIManager : MonoBehaviour
{
    public static UIManager Instance { get; private set; }

    #region UI
    [SerializeField] private Canvas headCanvas;
    [SerializeField] private Canvas popCanvas;
    [SerializeField] private Canvas bottomCanvas;

    // LeftUI
    [SerializeField] private Text officeName;
    [SerializeField] private Text day;

    // RightUI
    [SerializeField] private Text task;
    [SerializeField] private RectTransform taskRectTransform;
    [SerializeField] private Image taskProcessBar;
    [SerializeField] private Text taskProcessPercent;
    [SerializeField] private Button printDaily;

    // Dialog Max UI
    [SerializeField] private GameObject dialog;
    [SerializeField] private Image dialogIcon;
    [SerializeField] private Text dialogNpcName;
    [SerializeField] private Text dialogNpcPosition;
    [SerializeField] private Text dialogNpcJobContent;
    [SerializeField] private float dialogBaseHeight = 148f;

    // CenterUI
    [SerializeField] private Button printClosingReportBtn;
    [SerializeField] private Image printerWindow;
    [SerializeField] private Button closePrinterWindowBtn;
    [SerializeField] private Text printerWindowContent;
    [SerializeField] private Button printReport;

    // BottomUI
    [SerializeField] private InputField taskInput;
    [SerializeField] private Button submit;
    #endregion

    // 事件
    public static event Action<string> NewTaskSubmitHandler;
    public static event Action PrintBtnClickHandler;

    [SerializeField] private float taskScrollSpeed = 30f;
    private bool isTaskScrolling = false;

    private GameObject[] npcArray;

    private StringBuilder employeeDaily;
    private string closingReport;

    private void Awake()
    {
        if (Instance != null)
        {
            Debug.LogError("Singleton!!!");
            Destroy(this);
        }
        Instance = this;

        npcArray = GameObject.FindGameObjectsWithTag("NPC");
    }

    private void OnEnable()
    {
        printDaily.onClick.AddListener(PrintDailyBtnClicked);
        printClosingReportBtn.onClick.AddListener(PrintClosingReportClicked);
        submit.onClick.AddListener(TaskSubmitBtnClicked);
        closePrinterWindowBtn.onClick.AddListener(OnClosePrintWindowBtnClicked);
        printReport.onClick.AddListener(OnReportBtnClicked);
        taskInput.onSubmit.AddListener(val => submit.onClick.Invoke());

        RegisterNpcBodyClickHandler();

        UnitySocketClient.OnTaskReceiveHandler += OnTaskReceive;
    }

    private void OnDisable()
    {
        printDaily.onClick.RemoveListener(PrintDailyBtnClicked);
        printClosingReportBtn.onClick.RemoveListener(PrintClosingReportClicked);
        submit.onClick.RemoveListener(TaskSubmitBtnClicked);
        closePrinterWindowBtn.onClick.RemoveListener(OnClosePrintWindowBtnClicked);
        printReport.onClick.RemoveListener(OnReportBtnClicked);
        taskInput.onSubmit.RemoveAllListeners();

        UnregisterNpcBodyClickHandler();

        UnitySocketClient.OnTaskReceiveHandler -= OnTaskReceive;
    }

    private void Start()
    {
        printClosingReportBtn.gameObject.SetActive(false);
        printerWindow.gameObject.SetActive(false);
        employeeDaily = new();
        printDaily.interactable = false;
    }

    private bool playerActionsIsDisable = false;
    private void Update()
    {
        if (isTaskScrolling)
        {
            taskRectTransform.anchoredPosition += taskScrollSpeed * Time.deltaTime * Vector2.left;
            if (taskRectTransform.anchoredPosition.x <= -taskRectTransform.rect.width)
            {
                taskRectTransform.anchoredPosition = new Vector2(0, taskRectTransform.anchoredPosition.y);
            }
        }

        if (taskInput.isFocused)
        {
            if (!playerActionsIsDisable)
            {
                GameInput.Instance.DisablePlayerActions();
                playerActionsIsDisable = true;
            }
        }
        else
        {
            if (playerActionsIsDisable)
            {
                GameInput.Instance.EnablePlayerActions();
                playerActionsIsDisable = false;
            }
        }

#if UNITY_EDITOR
        if (Input.GetKeyUp(KeyCode.O))
        {
            SetAndShowDialogMax(true, dialogIcon.sprite, "李四", "代理商看到附件", "武器好硒鼓");
        }
        if (Input.GetKeyUp(KeyCode.P))
        {
            SetAndShowDialogMax(true, dialogIcon.sprite, "刘一", "代理商", "反倒是看看发了打开设计费打开福建省劳动法可接受的发的开发觉得舒服了第三方可接受的发了肯德基数量快递费结算单发了收到咖啡机上岛咖啡了解收到复礼克己水电费离开水电费");
        }
#endif
    }

    private void RegisterNpcBodyClickHandler()
    {
        if (npcArray == null) return;

        for (int i = 0; i < npcArray.Length; i++)
        {
            if (!npcArray[i].TryGetComponent<NpcController>(out var controller)) continue;
            controller.BodyIsClickedHandler += OnNpcBodyClicked;
        }
    }

    private void UnregisterNpcBodyClickHandler()
    {
        if (npcArray == null) return;

        try
        {
            for (int i = 0; i < npcArray.Length; i++)
            {
                if (!npcArray[i].TryGetComponent<NpcController>(out var controller)) continue;
                controller.BodyIsClickedHandler -= OnNpcBodyClicked;
            }
        }
        catch
        {
            // do nothing
        }
    }

    private void OnNpcBodyClicked(bool isDisplay, Sprite sprite, NpcTaskResult result, float visibleTime)
    {
        SetAndShowDialogMax(isDisplay, sprite, result.name, result.position, result.do_);

        if (visibleTime > 0)
        {
            if (isDisplay)
            {
                Invoke(nameof(HideDialogMax), visibleTime);
            }
            else
            {
                CancelInvoke(nameof(HideDialogMax));
            }
        }
    }

    private void OnReportBtnClicked()
    {
        // 输出日报
        PrintBtnClickHandler?.Invoke();
    }

    private void OnClosePrintWindowBtnClicked()
    {
        if (!string.IsNullOrEmpty(closingReport))
        {
            printClosingReportBtn.gameObject.SetActive(true);
        }
        bottomCanvas.gameObject.SetActive(true);
        printerWindow.gameObject.SetActive(false);
    }

    private void HideDialogMax()
    {
        dialog.SetActive(false);
    }

    private void OnTaskReceive(TaskResult result)
    {
        if (result.resultType == TypeFieldDefs.RESULT_TASK)
        {
            SetDay(result.time);
            SetCurrentTask(result.task);
            SetCurrentTaskPercent(result.process);

            GenerateDaily(result);
        }
        else if (result.resultType == TypeFieldDefs.RESULT_CLOSING_REPORT)
        {
            closingReport = result.closingReport;
            // display print button
            printClosingReportBtn.gameObject.SetActive(true);
        }
        else
        {
            Debug.LogError("error resultType: " + result.resultType);
        }
    }

    /// <summary>
    /// 生成日报
    /// </summary>
    /// <param name="result"></param>
    private void GenerateDaily(TaskResult result)
    {
        printDaily.interactable = false;

        employeeDaily.Clear();
        employeeDaily.Append("任务名称：");
        employeeDaily.Append(Environment.NewLine);
        employeeDaily.Append(result.task);
        employeeDaily.Append(Environment.NewLine);
        employeeDaily.Append(Environment.NewLine);
        employeeDaily.Append("任务进度：");
        employeeDaily.Append(result.process);
        employeeDaily.Append("%");
        employeeDaily.Append(Environment.NewLine);
        employeeDaily.Append(Environment.NewLine);
        employeeDaily.Append("第 ");
        employeeDaily.Append(result.time);
        employeeDaily.Append(" 天工作内容：");
        employeeDaily.Append(Environment.NewLine);
        foreach (var npc in result.tasks)
        {
            employeeDaily.Append(npc.position);
            employeeDaily.Append(npc.name);
            employeeDaily.Append("：");
            employeeDaily.Append(npc.do_);
            employeeDaily.Append(Environment.NewLine);
        }

        printDaily.interactable = true;
    }

    private void TaskSubmitBtnClicked()
    {
        NewTaskSubmitHandler?.Invoke(taskInput.text);
        taskInput.text = string.Empty;
        closingReport = string.Empty;
        employeeDaily.Clear();
        printDaily.interactable = false;
    }

    private void PrintClosingReportClicked()
    {
        SetAndShowPrinterWindow(closingReport);
    }

    private void PrintDailyBtnClicked()
    {
        SetAndShowPrinterWindow(employeeDaily.ToString());
    }

    public void SetCurrentTaskPercent(int percent)
    {
        taskProcessBar.fillAmount = percent / 100f;
        taskProcessPercent.text = percent + "%";
    }

    public void SetCurrentTask(string task)
    {
        this.task.text = task;
        if ((taskRectTransform.parent as RectTransform).rect.size.x < this.task.preferredWidth)
        {
            StartTaskTextScrolling();
        }
        else
        {
            StopTaskTextScrolling();
        }
    }

    public void StartTaskTextScrolling()
    {
        isTaskScrolling = true;
    }

    public void StopTaskTextScrolling()
    {
        isTaskScrolling = false;
    }

    public void SetDay(int day)
    {
        this.day.text = $"第 {day} 天";
    }

    public void SetDayString(string text)
    {
        day.text = text;
    }

    public void SetAndShowPrinterWindow(string content)
    {
        printClosingReportBtn.gameObject.SetActive(false);
        bottomCanvas.gameObject.SetActive(false);
        printerWindowContent.text = content;
        printerWindow.gameObject.SetActive(true);
    }

    public void SetAndShowDialogMax(bool isDisplay, Sprite sprite, string name, string position, string jobContent)
    {
        if (isDisplay)
        {
            dialogIcon.sprite = sprite;
            dialogNpcName.text = name;
            dialogNpcPosition.text = position;
            dialogNpcJobContent.text = jobContent;

            (dialog.transform as RectTransform).SetSizeWithCurrentAnchors(RectTransform.Axis.Vertical, dialogNpcJobContent.preferredHeight + dialogBaseHeight);
        }
        dialog.SetActive(isDisplay);
    }
}
