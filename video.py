import os
from moviepy import *


def get_video_length(file_path):
    """获取单个视频文件的长度（秒）"""
    try:
        with VideoFileClip(file_path) as video:
            return video.duration
    except Exception as e:
        print(f"无法处理文件 {file_path}: {e}")
        return 0


def calculate_total_video_length(directory):
    """递归统计目录下所有视频文件的总长度"""
    total_length = 0
    video_extensions = (".mp4", ".avi", ".mkv", ".mov", ".flv")  # 支持的视频格式

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(video_extensions):
                file_path = os.path.join(root, file)
                total_length += get_video_length(file_path)

    return total_length


if __name__ == "__main__":
    directory = "D:\\BaiduNetdiskDownload\\03.【2025考研数学】张宇专属全程班\\03.基础30讲\\04.概率论与数理统计".strip()
    if os.path.isdir(directory):
        total_length = calculate_total_video_length(directory)
        print(
            f"目录 {directory} 下所有视频文件的总长度为 {total_length / 3600:.2f} 小时"
        )
    else:
        print("输入的路径不是有效的目录！")
