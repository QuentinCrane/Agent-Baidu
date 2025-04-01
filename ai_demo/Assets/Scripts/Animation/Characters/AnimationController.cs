using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AnimationController : MonoBehaviour
{

    private Animator moveAnimator;
    // Start is called before the first frame update
    void Awake()
    {
        moveAnimator = transform.GetComponent<Animator>();
    }

    public void SetPlayAimations(Vector2 Direction,float speed)
    {
        if (Direction != Vector2.zero)
        {
            moveAnimator.SetFloat("x", Direction.x);
            moveAnimator.SetFloat("y", Direction.y);
        }
        moveAnimator.SetFloat("Speed", speed);
    }
}
