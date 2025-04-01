using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameInput : MonoBehaviour
{
    public static GameInput Instance { get; private set; }

    private PlayerInputActions playerInputActions;

    private void Awake()
    {
        if (Instance != null)
        {
            Debug.LogError("GameInput is Singleton");
            Destroy(gameObject);
        }
        Instance = this;

        playerInputActions = new PlayerInputActions();
        EnablePlayerActions();
    }

    public Vector2 GetMovementVectorNormalized()
    {
        Vector2 inputVector = playerInputActions.Player.Move.ReadValue<Vector2>();

        return inputVector.normalized;
    }
    
    public Vector2 GetMouseVector2()
    {
        Vector2 inputVector = playerInputActions.Player.Look.ReadValue<Vector2>();

        return inputVector;
    }

    public void EnablePlayerActions()
    {
        playerInputActions.Player.Enable();
    }

    public void DisablePlayerActions()
    {
        playerInputActions.Player.Disable();
    }
}
