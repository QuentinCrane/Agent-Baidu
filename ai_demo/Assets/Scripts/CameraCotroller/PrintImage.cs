using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using Unity.Mathematics;
using UnityEngine;
using UnityEngine.Diagnostics;

public class PrintImage : MonoBehaviour
{
    public RectTransform UIRect;
    private const string dirName = "StreamingAssets/";
    private static string fullDirPath;

    private void Awake()
    {
        fullDirPath = Path.Combine(Application.dataPath, dirName);
    }

    private void OnEnable()
    {
        UIManager.PrintBtnClickHandler += OnPrintReport;
    }

    private void OnDisable()
    {
        UIManager.PrintBtnClickHandler -= OnPrintReport;
    }

    private void OnPrintReport()
    {
        GenratePicture();
    }

    public void GenratePicture()
    {
        IEnumerator coroutine = CaptureByUI(UIRect);
        StartCoroutine(coroutine);
    }
    public IEnumerator CaptureByUI(RectTransform UIRect)
    {
        CheckDir();
        //等待帧画面渲染结束
        string fileName = Path.Combine(fullDirPath, $"{GetRandomChars(20)}.png");
        yield return new WaitForEndOfFrame();

        int width = (int)(UIRect.rect.width);
        int height = (int)(UIRect.rect.height);

        Texture2D tex = new Texture2D(width, height, TextureFormat.RGB24, false);

        //左下角为原点（0, 0）
        float leftBtmX = UIRect.transform.position.x + UIRect.rect.xMin;
        float leftBtmY = UIRect.transform.position.y + UIRect.rect.yMin;

        //从屏幕读取像素, leftBtmX/leftBtnY 是读取的初始位置,width、height是读取像素的宽度和高度
        tex.ReadPixels(new Rect(leftBtmX, leftBtmY, width, height), 0, 0);
        //执行读取操作
        tex.Apply();
        byte[] bytes = tex.EncodeToPNG();
        //保存
        System.IO.File.WriteAllBytes(fileName, bytes);
        Debug.Log("打印完成");
        TipUI.TipNormal("打印完成,文件位于:"+ fullDirPath, 3);
    }

    private void CheckDir()
    {
        if (!File.Exists(fullDirPath))
        {
            try
            {
                Directory.CreateDirectory(fullDirPath);
            }
            catch
            {
                TipUI.TipError($"无法创建文件夹[{fullDirPath}]");
            }
        }
    }

    private const string chars = "ABCDEFGHIJKLMNOPQRSTUWVXYZ0123456789abcdefghijklmnopqrstuvwxyz";
    private static readonly System.Random random = new System.Random();

    public static string GetRandomChars(int length)
    {
        char[] res = new char[length];
        for (int i = 0; i < length; ++i)
        {
            res[i] = chars[random.Next(chars.Length)];
        }
        return new string(res);
    }
}
