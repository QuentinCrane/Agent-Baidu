using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using System;

public class NPCCmdSenderWindow : EditorWindow
{
    string cmdText = "{name:cmd = []}";

    [MenuItem("GMCmd/Input NPC Command")]
    static void Init()
    {
        NPCCmdSenderWindow window = EditorWindow.GetWindow<NPCCmdSenderWindow>();
        window.Show();
    }

    private void OnGUI()
    {
        cmdText = GUILayout.TextArea(cmdText, GUILayout.MinHeight(100));
        if (GUILayout.Button("执行"))
        {
            if (!EditorApplication.isPlaying)
            {
                Debug.LogError("必须启动游戏才能执行");
                return;
            }
            if (string.IsNullOrEmpty(cmdText)) return;
            var cmds = CommandFactory.Parse(cmdText);
            foreach(var cmd in cmds)
            {
                try
                {
                    var controller = GameObject.Find(cmd.Key).GetComponent<NpcController>();
                    controller.SubmitCommands(cmd.Value.ToArray());
                }
                catch(Exception e)
                {
                    Debug.Log($"没有名称为{cmd.Key}的NPC。error: {e}");
                }
            }
        }
    }
}
