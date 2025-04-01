using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MapContorller : MonoBehaviour
{

    // ����϶�������
    public float dragSpeed = 2;

    // ������ı߽緶Χ
    public float minX = -3f;
    public float maxX = 28f;
    public float minY = -28f;
    public float maxY = 3f;

    private Vector3 dragOrigin;

    void Update()
    {
        // ������갴���¼�
        if (Input.GetMouseButtonDown(0))
        {
            dragOrigin = Input.mousePosition;
            return;
        }

        // ��������϶��¼�
        if (!Input.GetMouseButton(0)) return;

        // ��������϶���ƫ����
        Vector3 pos = Camera.main.ScreenToViewportPoint(Input.mousePosition - dragOrigin);

        // ���������Ŀ��λ��
        Vector3 move = new Vector3(pos.x * dragSpeed, pos.y * dragSpeed, 0);

        // �ƶ���������������ڱ߽緶Χ��
        transform.position = new Vector3(
            Mathf.Clamp(transform.position.x - move.x, minX, maxX),
            Mathf.Clamp(transform.position.y - move.y, minY, maxY),
            transform.position.z
        );

        // ��������϶������
        dragOrigin = Input.mousePosition;
    }
}
