using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MapContorller : MonoBehaviour
{

    // 鼠标拖动灵敏度
    public float dragSpeed = 2;

    // 摄像机的边界范围
    public float minX = -3f;
    public float maxX = 28f;
    public float minY = -28f;
    public float maxY = 3f;

    private Vector3 dragOrigin;

    void Update()
    {
        // 处理鼠标按下事件
        if (Input.GetMouseButtonDown(0))
        {
            dragOrigin = Input.mousePosition;
            return;
        }

        // 处理鼠标拖动事件
        if (!Input.GetMouseButton(0)) return;

        // 计算鼠标拖动的偏移量
        Vector3 pos = Camera.main.ScreenToViewportPoint(Input.mousePosition - dragOrigin);

        // 计算摄像机目标位置
        Vector3 move = new Vector3(pos.x * dragSpeed, pos.y * dragSpeed, 0);

        // 移动摄像机，并限制在边界范围内
        transform.position = new Vector3(
            Mathf.Clamp(transform.position.x - move.x, minX, maxX),
            Mathf.Clamp(transform.position.y - move.y, minY, maxY),
            transform.position.z
        );

        // 更新鼠标拖动的起点
        dragOrigin = Input.mousePosition;
    }
}
