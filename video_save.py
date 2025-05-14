import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from moviepy import *
import threading
import json
import datetime

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
    files_data = []
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path) and file.lower().endswith(video_extensions):
            length = get_video_length(file_path)
            item_id = tree.insert(current_id, "end", text=file, values=[format_time(length)])
            files_length += length
            files_data.append({"name": file, "length": length, "id": item_id})
    
    total_length += files_length
    
    # 处理子目录
    subdirs_data = []
    for subdir in os.listdir(directory):
        subdir_path = os.path.join(directory, subdir)
        if os.path.isdir(subdir_path):
            subdir_length, subdir_data = scan_directory(subdir_path, tree, current_id)
            total_length += subdir_length
            subdirs_data.append({"name": subdir, "data": subdir_data, "length": subdir_length})
    
    # 更新当前目录的总长度
    tree.item(current_id, values=[format_time(total_length)])
    
    # 返回总长度和当前目录的数据结构
    dir_data = {
        "path": directory,
        "name": dir_name,
        "total_length": total_length,
        "files": files_data,
        "subdirs": subdirs_data,
        "id": current_id
    }
    
    return total_length, dir_data

def start_scan():
    """在后台线程中开始扫描，避免GUI卡顿"""
    global current_scan_data, current_directory
    
    directory = filedialog.askdirectory(title="选择要统计的视频目录")
    if not directory:
        return
    
    current_directory = directory
    
    # 清空树视图
    for item in tree.get_children():
        tree.delete(item)
    
    status_label.config(text="正在统计中，请稍候...")
    select_button.config(state="disabled")
    save_button.config(state="disabled")
    
    def scan_thread():
        global current_scan_data
        total_length, scan_data = scan_directory(directory, tree)
        current_scan_data = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "root_directory": directory,
            "total_length": total_length,
            "data": scan_data
        }
        
        # 更新界面状态
        root.after(0, lambda: status_label.config(
            text=f"统计完成！总时长: {format_time(total_length)}"
        ))
        root.after(0, lambda: select_button.config(state="normal"))
        root.after(0, lambda: save_button.config(state="normal"))
    
    threading.Thread(target=scan_thread, daemon=True).start()

def save_results():
    """保存统计结果到JSON文件"""
    if not current_scan_data:
        messagebox.showinfo("提示", "没有可保存的统计结果")
        return
    
    # 默认使用当前目录的名称作为文件名
    default_filename = os.path.basename(current_directory) or "video_stats"
    default_filename = f"{default_filename}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    file_path = filedialog.asksaveasfilename(
        title="保存统计结果",
        defaultextension=".json",
        initialfile=default_filename,
        filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
    )
    
    if not file_path:
        return
    
    try:
        # 准备保存数据，移除树视图的ID引用
        save_data = prepare_data_for_save(current_scan_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        messagebox.showinfo("成功", f"统计结果已保存至：\n{file_path}")
    except Exception as e:
        messagebox.showerror("错误", f"保存失败: {str(e)}")

def prepare_data_for_save(data):
    """递归处理数据，移除不需要保存的字段"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key != "id":  # 不保存树视图ID
                result[key] = prepare_data_for_save(value)
        return result
    elif isinstance(data, list):
        return [prepare_data_for_save(item) for item in data]
    else:
        return data

def load_results():
    """从JSON文件加载统计结果"""
    file_path = filedialog.askopenfilename(
        title="加载统计结果",
        filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 清空树视图
        for item in tree.get_children():
            tree.delete(item)
        
        # 加载数据到树视图
        global current_scan_data, current_directory
        current_scan_data = data
        current_directory = data.get("root_directory", "")
        
        status_label.config(text=f"加载统计数据 - 时间: {data.get('timestamp', '未知')}") 
        
        # 递归构建树视图
        build_tree_from_data(data.get("data", {}))
        
        # 展开根节点
        if tree.get_children():
            tree.item(tree.get_children()[0], open=True)
            
        save_button.config(state="normal")
        
    except Exception as e:
        messagebox.showerror("错误", f"加载失败: {str(e)}")

def build_tree_from_data(data, parent=""):
    """从保存的数据构建树视图"""
    if not data:
        return
    
    # 创建当前目录节点
    current_id = tree.insert(
        parent, "end", 
        text=data.get("name", "未知目录"),
        values=[format_time(data.get("total_length", 0))]
    )
    
    # 添加文件
    for file_info in data.get("files", []):
        tree.insert(
            current_id, "end",
            text=file_info.get("name", "未知文件"),
            values=[format_time(file_info.get("length", 0))]
        )
    
    # 递归添加子目录
    for subdir in data.get("subdirs", []):
        build_tree_from_data(subdir.get("data", {}), current_id)
    
    return current_id

def calculate_selected_duration():
    """计算选中项目的总时长"""
    selected_items = tree.selection()
    if not selected_items:
        selection_label.config(text="未选中任何项目")
        return
    
    total_duration = 0
    selected_files_count = 0
    selected_dirs_count = 0
    
    for item_id in selected_items:
        # 检查是否为文件
        item_text = tree.item(item_id, "text")
        item_values = tree.item(item_id, "values")
        parent_id = tree.parent(item_id)
        
        # 如果有父节点且值包含时间，则可能是文件
        if parent_id and item_values and item_values[0]:
            try:
                # 尝试从文件节点的数据中获取时长
                time_str = item_values[0]
                # 解析时间字符串
                hours, minutes, seconds = 0, 0, 0
                if "时" in time_str:
                    hours = int(time_str.split("时")[0])
                    time_str = time_str.split("时")[1]
                if "分" in time_str:
                    minutes = int(time_str.split("分")[0])
                    time_str = time_str.split("分")[1]
                if "秒" in time_str:
                    seconds = int(time_str.split("秒")[0])
                
                duration = hours * 3600 + minutes * 60 + seconds
                total_duration += duration
                selected_files_count += 1
            except:
                # 如果解析失败，可能是目录
                selected_dirs_count += 1
        else:
            selected_dirs_count += 1
    
    # 显示结果
    selection_text = f"已选择: {selected_files_count}个文件"
    if selected_dirs_count > 0:
        selection_text += f", {selected_dirs_count}个目录"
    selection_text += f" | 选中视频总时长: {format_time(total_duration)}"
    selection_label.config(text=selection_text)

# 创建主窗口
root = tk.Tk()
root.title("视频时长统计工具")
root.geometry("800x600")

# 全局变量
current_scan_data = None
current_directory = ""

# 顶部控制区域
frame_top = tk.Frame(root, pady=10, padx=10)
frame_top.pack(fill="x")

select_button = tk.Button(frame_top, text="选择目录", command=start_scan, width=15)
select_button.pack(side="left", padx=5)

save_button = tk.Button(frame_top, text="保存结果", command=save_results, width=15, state="disabled")
save_button.pack(side="left", padx=5)

load_button = tk.Button(frame_top, text="加载结果", command=load_results, width=15)
load_button.pack(side="left", padx=5)

status_label = tk.Label(frame_top, text="请选择一个目录开始统计")
status_label.pack(side="left", padx=10)

# 创建树形视图
frame_tree = tk.Frame(root)
frame_tree.pack(fill="both", expand=True, padx=10, pady=5)

# 设置树的列，启用多选功能
tree = ttk.Treeview(frame_tree, selectmode="extended")
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

# 选中项目信息区域
selection_frame = tk.Frame(root, pady=5, padx=10)
selection_frame.pack(fill="x")
selection_label = tk.Label(selection_frame, text="未选中任何项目", anchor="w")
selection_label.pack(fill="x")

# 绑定选择事件
tree.bind("<<TreeviewSelect>>", lambda e: calculate_selected_duration())

# 说明标签
help_text = "说明：目录旁显示的是该目录（包含子目录）所有视频的总时长。可以保存和加载统计结果。选中一个或多个视频可以查看选中项目的总时长。"
help_label = tk.Label(root, text=help_text, pady=5)
help_label.pack(side="bottom", fill="x")

root.mainloop()