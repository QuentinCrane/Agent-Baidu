using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;

public class GMCmd : Editor
{
    [MenuItem("GMCmd/Test CMD Parse")]
    public static void TestCommandParse()
    {
        string txt = @"½Ú×àdskdfljsdlf 
                        fds
                        {Tom:cmd =[move_left, move_up,mouse_click]}\ndfsd
                        fdssx
{Jerry:cmd=[move_down,move_down]}
                        dfd";
        var commands = CommandFactory.Parse(txt);

        foreach(var cmd in commands)
        {
            Debug.Log(cmd);
        }
    }
}
