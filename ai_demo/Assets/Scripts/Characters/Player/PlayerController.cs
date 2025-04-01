using UnityEngine;

public class PlayerController : CharacterController
{
    protected override Command HandleCommand()
    {
        Vector2 movement = GameInput.Instance.GetMovementVectorNormalized();

        if (movement.y > 0)
        {
            return moveUpCommand;
        }
        else if (movement.y < 0)
        {
            return moveDownCommand;
        }
        else if (movement.x < 0)
        {
            return moveLeftCommand;
        }
        else if (movement.x > 0)
        {
            return moveRightCommand;
        }

        return CommandFactory.GetEmptyCommand();
    }
}
