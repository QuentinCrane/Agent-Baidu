using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AutonomousAnimalMovement : MonoBehaviour
{
    public float moveSpeed = 1f;
    public float Max_X;
    public float Min_X;
    public float Max_Y;
    public float Min_Y;
    public float _distance;
    public float waitTimeMin;
    public float waitTimeMax;
    
    public float waitTime = 2f;

    public Vector3 targetPosition;
    public Vector3 pos;
    public bool isMoving = true;

    private Animator animator;

    void Start()
    {
        // 初始时设置目标点
        StartCoroutine(WaitAndSetNewTarget());
        animator = GetComponent<Animator>();
       // transform.position = Vector3.MoveTowards(transform.position, targetPosition, moveSpeed * Time.deltaTime);
    }

    void Update()
    {
        // 移动小动物
        MoveAnimal();
    }

    void MoveAnimal()
    {
        if (isMoving)
        {
            if (Vector3.Distance(transform.position, targetPosition) > 0.1f)
            {
                transform.position = Vector3.MoveTowards(transform.position, targetPosition, moveSpeed * Time.deltaTime);
            }
            else
            {
                StartCoroutine(WaitAndSetNewTarget());
            }
        }
        setAnimation();
    }

    IEnumerator WaitAndSetNewTarget()
    {
        isMoving = false;

        // 等待一段时间
        waitTime = Random.Range(waitTimeMin, waitTimeMax);
        yield return new WaitForSeconds(waitTime);
        // 设置新的目标点
        isMoving = true;
        targetPosition = SetNewRandomTarget();
    }

    public Vector3 SetNewRandomTarget()
    {
        
        do{
        // 生成新的目标点在指定范围内
        float randomX = Random.Range(Min_X, Max_X);
        float randomY = Random.Range(Min_Y, Max_Y);
        pos = new Vector3(randomX, randomY, transform.position.z);
        }while(Vector3.Distance(pos,transform.position) > _distance);
        return pos;
    }

    public void setAnimation()
    {
        if (isMoving)
        {
            animator.SetFloat("Speed", 1);
            animator.SetFloat("x",targetPosition.x - transform.position.x);
            animator.SetFloat("y", targetPosition.y - transform.position.y);
        }
        else
        {
            animator.SetFloat("Speed", 0);
            animator.SetFloat("x", targetPosition.x - transform.position.x);
            animator.SetFloat("y", targetPosition.y - transform.position.y);
        }

    }
}
