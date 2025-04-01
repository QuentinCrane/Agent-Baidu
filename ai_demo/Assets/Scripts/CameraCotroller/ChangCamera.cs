using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ChangCamera : MonoBehaviour
{
    public GameObject playerCamera;
    public GameObject mapCamera;
    public bool isMap = false;

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.M))
        {
            isMap = !isMap;
            playerCamera.SetActive(!isMap);
            mapCamera.SetActive(isMap);
        }
    }
}
