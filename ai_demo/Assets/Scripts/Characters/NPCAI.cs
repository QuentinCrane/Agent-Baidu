using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

public class NPCAI : MonoBehaviour
{
    public NavMeshAgent meshAgent;
    public Transform target;
    public bool isClickCtrl;
    private Animator animator;
    private float dev_x;
    private float dev_y;
    private Vector3 lastPos;
    private Vector3 newPos;
    private bool isWorkDone = true;
    private Vector3 targetPosition;

    public event System.Action OnArrivalHandler;

    // Start is called before the first frame update
    void Start()
    {
        //�ر���ת
        meshAgent.updateRotation = false;
        meshAgent.updateUpAxis = false;
        //�ر��Զ�����λ��
        //meshAgent.updatePosition = false;
        animator = GetComponent<Animator>();
        lastPos = newPos = transform.position;
    }

    // Update is called once per frame
    void Update()
    {
        Move();
        // CheckWorkDone();
        //动画
        NavAnimation();

#if UNITY_EDITOR
        if (Input.GetKeyDown(KeyCode.Space))
        {
            SetTargetPos(new Vector3(Random.Range(-10f, 10f), Random.Range(-10f, 10f), 0f));
        }
        if (Input.GetKeyUp(KeyCode.N))
        {
            SetTargetPos(target.position);
        }
#endif
    }

    // private void CheckWorkDone()
    // {
    //     var me = transform.position;
    //     if (!isWorkDone && Vector3.Distance(me, targetPosition) < .1f)
    //     {
    //         isWorkDone = true;
    //         OnArrivalHandler?.Invoke();
    //         transform.position = targetPosition;
    //     }
    // }

    //修改目标点
    private void Move()
    {
        if (!meshAgent.pathPending && meshAgent.remainingDistance <= meshAgent.stoppingDistance)
        {
            if (!isWorkDone)
            {
                isWorkDone = true;
                OnArrivalHandler?.Invoke();
                transform.position = targetPosition;
            }
            meshAgent.isStopped = true;
        }
        else
        {
            meshAgent.isStopped = false;
        }
    }

    //设置目标点
    public void SetTargetPos(Vector3 targetPos)
    {
        if (targetPos != null)
        {
            float agentOffset = 0.001f;
            Vector3 agentPos = (Vector3)(agentOffset * Random.insideUnitCircle) + targetPos;
            //Vector3 agentPos = new Vector3(Mathf.Round(pos.x), Mathf.Round(pos.y), pos.z);
            targetPosition = agentPos;
            isWorkDone = false;
            meshAgent.SetDestination(agentPos);
        }

    }
    //寻路动画
    private void NavAnimation()
    {
        dev_x = meshAgent.steeringTarget.x - transform.position.x;
        dev_y = meshAgent.steeringTarget.y - transform.position.y;

        if (/*!meshAgent.pathPending &&*/ (meshAgent.remainingDistance > meshAgent.stoppingDistance))
        {
            animator.SetFloat("Speed", 1);
        }
        else
        {
            animator.SetFloat("Speed", 0);
        }
        animator.SetFloat("x", dev_x);
        animator.SetFloat("y", dev_y);
    }
}
