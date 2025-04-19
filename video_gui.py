import os
import tkinter as tk
from tkinter import filedialog, ttk
from moviepy import *

import threading

def get_video_length(file_path):
    """获取单个视频文件的长度（秒）"""
    try:
        with VideoFileClip(file_path) as video:
            return video.duration
    except Exception as e:
        print(f"无法处理文件 {file_path}: {e}")
        return 0

def format_time(seconds):
    """将秒数格式化为时分秒"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours}时{minutes}分{seconds}秒"

def scan_directory(directory, tree, parent=""):
    """递归扫描目录，计算视频长度并更新树形视图"""
    total_length = 0
    video_extensions = (".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv")
    
    # 添加当前目录到树中
    dir_name = os.path.basename(directory)
    if not dir_name:  # 如果是根目录
        dir_name = directory
    
    current_id = tree.insert(parent, "end", text=dir_name, values=["计算中..."])
    tree.update()
    
    # 首先处理当前目录中的视频文件
    files_length = 0
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path) and file.lower().endswith(video_extensions):
            length = get_video_length(file_path)
            tree.insert(current_id, "end", text=file, values=[format_time(length)])
            files_length += length
    
    total_length += files_length
    
    # 处理子目录
    for subdir in os.listdir(directory):
        subdir_path = os.path.join(directory, subdir)
        if os.path.isdir(subdir_path):
            subdir_length = scan_directory(subdir_path, tree, current_id)
            total_length += subdir_length
    
    # 更新当前目录的总长度
    tree.item(current_id, values=[format_time(total_length)])
    
    return total_length

def start_scan():
    """在后台线程中开始扫描，避免GUI卡顿"""
    directory = filedialog.askdirectory(title="选择要统计的视频目录")
    if not directory:
        return
    
    # 清空树视图
    for item in tree.get_children():
        tree.delete(item)
    
    status_label.config(text="正在统计中，请稍候...")
    select_button.config(state="disabled")
    
    def scan_thread():
        total_length = scan_directory(directory, tree)
        
        # 更新界面状态
        root.after(0, lambda: status_label.config(
            text=f"统计完成！总时长: {format_time(total_length)}"
        ))
        root.after(0, lambda: select_button.config(state="normal"))
    
    threading.Thread(target=scan_thread, daemon=True).start()

# 创建主窗口
root = tk.Tk()
root.title("视频时长统计工具")
root.geometry("800x600")

# 顶部控制区域
frame_top = tk.Frame(root, pady=10, padx=10)
frame_top.pack(fill="x")

select_button = tk.Button(frame_top, text="选择目录", command=start_scan, width=15)
select_button.pack(side="left", padx=5)

status_label = tk.Label(frame_top, text="请选择一个目录开始统计")
status_label.pack(side="left", padx=10)

# 创建树形视图
frame_tree = tk.Frame(root)
frame_tree.pack(fill="both", expand=True, padx=10, pady=5)

# 设置树的列
tree = ttk.Treeview(frame_tree)
tree["columns"] = ("length")
tree.column("#0", width=400, minwidth=200)
tree.column("length", width=150, minwidth=100, anchor="center")
tree.heading("#0", text="目录/文件")
tree.heading("length", text="时长")

# 添加滚动条
vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
hsb = ttk.Scrollbar(frame_tree, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

vsb.pack(side="right", fill="y")
hsb.pack(side="bottom", fill="x")
tree.pack(fill="both", expand=True)

# 说明标签
help_text = "说明：目录旁显示的是该目录（包含子目录）所有视频的总时长。"
help_label = tk.Label(root, text=help_text, pady=5)
help_label.pack(side="bottom", fill="x")

root.mainloop()