using System;
using System.Collections;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEngine;

public class CommandFactory
{
    private static readonly EmptyCommand emptyCommand = new();
    private static readonly MoveUpCommand moveUpCommand = new();
    private static readonly MoveDownCommand moveDownCommand = new();
    private static readonly MoveLeftCommand moveLeftCommand = new();
    private static readonly MoveRightCommand moveRightCommand = new();
    private static readonly CloseDialogCommand closeDialogCommand = new();

    public static EmptyCommand GetEmptyCommand() { return emptyCommand; }

    /// <summary>
    /// cmd = [xxx,xxx,...]
    /// </summary>
    /// <param name="cmdText"></param>
    /// <returns></returns>
    public static Dictionary<string, List<Command>> Parse(string cmdText)
    {
        Dictionary<string, List<Command>> dict = new();
        List<Command> list;
        string pattern = @"\{(.*?):cmd *= *\[(.*?)\]\}";

        var mc = Regex.Matches(cmdText, pattern);
        foreach (Match match in mc)
        {
            try
            {
                string txt;
                string msg = null;
                string name = match.Groups[1].Value;
                string cmds = match.Groups[2].Value;
                string[] cmdArray = cmds.Split(',');
                list = new();
                for (int i = 0; i < cmdArray.Length; i++)
                {
                    txt = cmdArray[i].Trim();
                    if (txt.StartsWith(CommandDef.DIALOG_COMMAND))
                    {
                        string[] arr = txt.Split(':');
                        txt = arr[0];
                        msg = arr[1];
                    }
                    Command cmd = GenerateCommandByName(txt, msg);
                    list.Add(cmd);
                }
                if (!dict.ContainsKey(name))
                {
                    dict.Add(name, list);
                }
                else
                {
                    dict[name].AddRange(list);
                }
            }
            catch (Exception e)
            {
                Debug.LogError("½âÎöÃüÁîÊ§°Ü. error: " + e);
            }
        }

        return dict;
    }

    public static Command GenerateCommandByName(string cmdName, string message = null)
    {
        return cmdName switch
        {
            CommandDef.MOVE_UP_COMMAND => moveUpCommand,
            CommandDef.MOVE_DOWN_COMMAND => moveDownCommand,
            CommandDef.MOVE_LEFT_COMMAND => moveLeftCommand,
            CommandDef.MOVE_RIGHT_COMMAND => moveRightCommand,
            CommandDef.DIALOG_COMMAND => new DialogCommand(message),
            CommandDef.CLOSE_DIALOG_COMMAND => closeDialogCommand,
            _ => emptyCommand,
        };
    }
}
