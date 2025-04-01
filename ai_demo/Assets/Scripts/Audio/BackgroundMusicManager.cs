using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BackgroundMusicManager : MonoBehaviour
{
    public AudioClip[] backgroundMusicClips;
    private AudioSource audioSource;

    void Start()
    {
        // 获取或添加AudioSource组件
        audioSource = GetComponent<AudioSource>();
        if (audioSource == null)
        {
            audioSource = gameObject.AddComponent<AudioSource>();
        }

        // 播放第一首背景音乐
        PlayRandomBackgroundMusic();
    }

    void PlayRandomBackgroundMusic()
    {
        if (backgroundMusicClips.Length > 0)
        {
            // 随机选择一首音乐
            AudioClip randomClip = backgroundMusicClips[Random.Range(0, backgroundMusicClips.Length)];

            // 设置选择的音乐并开始播放
            audioSource.clip = randomClip;
            audioSource.Play();

            // 在音乐结束时调用函数，用于切换到下一首
            Invoke("PlayRandomBackgroundMusic", randomClip.length);
        }
    }
}
