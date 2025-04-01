using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public abstract class CharacterController : MonoBehaviour, Movement
{
    [SerializeField] protected float moveSpeed = 1f;
    [SerializeField] protected string characterName;
    protected Command moveUpCommand;
    protected Command moveDownCommand;
    protected Command moveLeftCommand;
    protected Command moveRightCommand;

    protected Vector2 moveDirection = Vector2.zero;
    protected bool isMoving = false;
    private Vector3 lastPosition;

    protected AnimationController animationController;
    protected DialogUI dialogUI;

    protected virtual void Awake()
    {
        moveUpCommand = CommandFactory.GenerateCommandByName(CommandDef.MOVE_UP_COMMAND);
        moveDownCommand = CommandFactory.GenerateCommandByName(CommandDef.MOVE_DOWN_COMMAND);
        moveLeftCommand = CommandFactory.GenerateCommandByName(CommandDef.MOVE_LEFT_COMMAND);
        moveRightCommand = CommandFactory.GenerateCommandByName(CommandDef.MOVE_RIGHT_COMMAND);

        animationController = GetComponent<AnimationController>();
        dialogUI = transform.Find("Dialog").GetComponent<DialogUI>();

        lastPosition = transform.position;

        SetDialogCharacterName(characterName);
    }

    protected abstract Command HandleCommand();

    protected virtual void Update()
    {
        isMoving = transform.position != lastPosition;
        lastPosition = transform.position;

        var command = HandleCommand();
        command.Execute(this);

        PlayAnimation();
    }

    public virtual void MoveUp()
    {
        moveDirection = Vector2.up;
        transform.position += moveSpeed * Time.deltaTime * Vector3.up;
    }
    public virtual void MoveDown()
    {
        moveDirection = Vector2.down;
        transform.position -= moveSpeed * Time.deltaTime * Vector3.up;
    }
    public virtual void MoveLeft()
    {
        moveDirection = Vector2.left;
        transform.position -= moveSpeed * Time.deltaTime * Vector3.right;
    }
    public virtual void MoveRight()
    {
        moveDirection = Vector2.right;
        transform.position += moveSpeed * Time.deltaTime * Vector3.right;
    }

    public virtual void SetDialogMessage(string message)
    {
        dialogUI.SetMessage(message);
        ShowDialogMessage();
    }

    public virtual void SetDialogCharacterName(string name)
    {
        dialogUI.SetName(name);
    }

    public virtual void CloseDialogMessage()
    {
        dialogUI.Hide();
    }

    public virtual void ShowDialogMessage()
    {
        dialogUI.Show();
    }

    protected virtual void PlayAnimation()
    {
        animationController.SetPlayAimations(moveDirection, isMoving ? 1 : 0);
    }
}
