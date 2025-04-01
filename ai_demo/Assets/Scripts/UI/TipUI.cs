using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class TipUI : MonoBehaviour
{
    [SerializeField] private Image tipBackground;
    [SerializeField] private Text message;
    [SerializeField] private float padding = 30f;

    private static TipUI tipUi;
    private static Color colorNormal = Color.white;
    private static Color colorError = new(0.5943396f, 0.0756942f, 0.0756942f);

    private void Awake()
    {
        tipUi = this;
    }

    public void Show()
    {
        tipUi.tipBackground.gameObject.SetActive(true);
    }

    public void Hide()
    {
        tipUi.tipBackground.gameObject.SetActive(false);
    }

    public static void Tip(string message, Color color, float duration = 1f)
    {
        tipUi.CancelInvoke(nameof(Hide));
        tipUi.tipBackground.color = color;
        tipUi.message.text = message;
        tipUi.tipBackground.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Vertical, tipUi.message.preferredHeight + tipUi.padding);
        tipUi.Show();
        tipUi.Invoke(nameof(Hide), duration);
    }

    public static void TipNormal(string message, float duration = 1f)
    {
        Tip(message, colorNormal, duration);
    }

    public static void TipError(string message, float duration = 2f)
    {
        Tip(message, colorError, duration);
    }
}
