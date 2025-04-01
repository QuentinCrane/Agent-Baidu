using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// 控制在老师身上摄像机的位置，防止看到场景外的黑幕
/// </summary>
public class objectCameraLimit : MonoBehaviour
{
    public float[] cameraLimitRange;//分别为上 下 左 右
    public Transform objectTrans;//老师
    // Use this for initialization
    void Start()
    {
        objectTrans = transform.parent;
    }

    // Update is called once per frame
    void Update()
    {
        cameraLimit();
    }
    void cameraLimit()
    {
        if (objectTrans.localPosition.y > cameraLimitRange[0])
        {
            transform.localPosition = new Vector3(transform.localPosition.x, cameraLimitRange[0] - objectTrans.localPosition.y, transform.localPosition.z);
        }
        else if (objectTrans.localPosition.y < cameraLimitRange[1])
        {
            transform.localPosition = new Vector3(transform.localPosition.x, cameraLimitRange[1] - objectTrans.localPosition.y, transform.localPosition.z);
        }

        if (objectTrans.localPosition.x > cameraLimitRange[3])
        {
            transform.localPosition = new Vector3(cameraLimitRange[3] - objectTrans.localPosition.x, transform.localPosition.y, transform.localPosition.z);
        }
        else if (objectTrans.localPosition.x < cameraLimitRange[2])
        {
            transform.localPosition = new Vector3(cameraLimitRange[2] - objectTrans.localPosition.x, transform.localPosition.y, transform.localPosition.z);
        }
    }

}