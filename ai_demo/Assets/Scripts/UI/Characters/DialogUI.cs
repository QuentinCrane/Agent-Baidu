using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class DialogUI : MonoBehaviour
{
    [SerializeField] private GameObject canvas;
    [SerializeField] private Image dialogBackground;
    [SerializeField] private TextMeshProUGUI message;
    [SerializeField] private TextMeshProUGUI nameText;
    [SerializeField] private float HorizontalPadding = 8f;

    private void Awake()
    {
        Hide();
    }

    public void SetMessage(string message)
    {
        if (string.IsNullOrEmpty(message)) return;

        this.message.text = message;
        dialogBackground.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Horizontal, this.message.preferredWidth + HorizontalPadding);
    }

    public void SetName(string name)
    {
        nameText.text = name;
    }

    public void Hide()
    {
        canvas.SetActive(false);
    }

    public void Show()
    {
        canvas.SetActive(true);
    }
}
