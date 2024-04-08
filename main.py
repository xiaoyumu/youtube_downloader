from youtube_downloader import download_video, Task, setup_proxy_socks5


if __name__ == '__main__':
    # Setup proxy if needed
    setup_proxy_socks5("192.168.1.1", 1080)

    video_list = [
        Task(1, "https://youtube.com/watch?v=Sq4R_yrE3Ug",
             subtitle=True, subtitle_offset_ms=-600, skip_video_download=True)
        ]
    output_path = "./download"
    for task in video_list:
        download_video(task, output_path)

