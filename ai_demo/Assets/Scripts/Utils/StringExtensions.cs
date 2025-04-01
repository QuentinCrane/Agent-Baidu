using System;
using System.Text.RegularExpressions;

public static class StringExtensions
{
    public static string ToUTF32(this string input)
    {
        string output = input;
        Regex pattern = new(@"\\u[a-zA-Z0-9]*");
        while (output.Contains(@"\u"))
        {
            output = pattern.Replace(output, @"\U000" + output.Substring(output.IndexOf(@"\u", StringComparison.Ordinal) + 2, 5), 1);
        }
        return output;
    }
}
