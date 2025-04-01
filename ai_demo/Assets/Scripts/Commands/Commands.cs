public class EmptyCommand : Command
{
    public void Execute(CharacterController character)
    {
        // do nothing
        _ = character;
    }
}
public class MoveUpCommand : Command
{
    public void Execute(CharacterController character)
    {
        if (character != null)
        {
            character.MoveUp();
        }
    }
}
public class MoveDownCommand : Command
{
    public void Execute(CharacterController character)
    {
        if (character != null)
        {
            character.MoveDown();
        }
    }
}
public class MoveLeftCommand : Command
{
    public void Execute(CharacterController character)
    {
        if (character != null)
        {
            character.MoveLeft();
        }
    }
}
public class MoveRightCommand : Command
{
    public void Execute(CharacterController character)
    {
        if (character != null)
        {
            character.MoveRight();
        }
    }
}

public class DialogCommand : Command
{
    private string message;

    public DialogCommand(string message)
    {
        this.message = message;
    }

    public void Execute(CharacterController character)
    {
        if (character != null)
            character.SetDialogMessage(message);
    }
}
public class CloseDialogCommand : Command
{
    public void Execute(CharacterController character)
    {
        if (character != null)
            character.CloseDialogMessage();
    }
}